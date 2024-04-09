from datetime import datetime, timezone
from typing import List

import boto3
from cloudtoken.core import utils
from cloudtoken.core.abstract_classes import CloudtokenPlugin
from cloudtoken.core.exceptions import PluginError
from cloudtoken.core.helper_classes import CloudtokenOption


class Plugin(CloudtokenPlugin):
    name = "assume_role"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @classmethod
    def options(cls) -> List[CloudtokenOption]:
        options = [
            cls.add_option(["--assume-role"], is_flag=True, help="Assume to another role from a federated role."),
            cls.add_option(["--dest-account"], type=str, help="Destination account number to assume role."),
            cls.add_option(["--dest-role-name"], type=str, help="Destination role name to assume."),
            cls.add_option(["--dest-role-arn"], type=str, help="Destination role arn to assume to."),
            cls.add_option(["--dest-role-alias", "-a"], type=str, help="Destination role arn alias name from config."),
            cls.add_option(["--role-session-name"], type=str, help="An identifier for the assumed role session."),
            cls.add_option(
                ["--switch-role-session-duration"], type=int, help="Specify AWS role session duration for assume Role"
            ),
        ]

        return options

    def execute(self, data: dict) -> dict:
        # When running in daemon mode plugins are executing more than once,
        # return the last set of credentials that aren't from the previous assume_role execution
        credentials = utils.find_credentials(data, exclude=[self.name])
        if not credentials:
            raise PluginError("Unable to find credetials provided by previous plugin.")

        if not self._get_plugin_config(["assume_role"]):
            return {}
        destination_role_arn = self._get_destination_role()
        session_name = self._get_plugin_config(["role_session_name"], credentials["AssumedRoleSessionName"])
        session_duration = self._get_plugin_config(["switch_role_session_duration"], 3600)

        utils.echo(f"Assume Role from {credentials['LastRole']} to {destination_role_arn}")

        assume_role_credentials = self._assume_role(credentials, destination_role_arn, session_name, session_duration)
        data = {"credentials": assume_role_credentials}
        return data

    def _get_destination_role(self):
        if (
            not self._get_plugin_config(["dest_role_arn"])
            and not (self._get_plugin_config(["dest_account"]) and self._get_plugin_config(["dest_role_name"]))
            and not self._get_plugin_config(["dest_role_alias"])
        ):
            raise PluginError("Please specify the role you want to switch to.")

        if self._get_plugin_config(["dest_role_alias"]):

            destination_role_arn = self._get_plugin_config([self._get_plugin_config(["dest_role_alias"])])
            if not destination_role_arn:
                raise PluginError(f"Destination role alias does not exist, Please check your config file.")
        else:
            destination_role_arn = self._get_plugin_config(
                ["dest_role_arn"],
                f'arn:aws:iam::{self._get_plugin_config(["dest_account"])}:role/{self._get_plugin_config(["dest_role_name"])}',
            )
        return destination_role_arn

    def _assume_role(
        self, credentials: dict, destination_role_arn: str, session_name: str, session_duration: int
    ) -> dict:
        client = boto3.client(
            "sts",
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["Token"],
        )
        try:
            response = client.assume_role(
                RoleArn=destination_role_arn, RoleSessionName=session_name, DurationSeconds=session_duration
            )
        except Exception as e:
            raise PluginError(f"Failed to assume role: {e}")
        try:
            credentials = {
                "AccessKeyId": response["Credentials"]["AccessKeyId"],
                "AccountId": destination_role_arn.split(":")[4],
                "Code": "Success",
                "Expiration": response["Credentials"]["Expiration"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "LastRole": destination_role_arn,
                "LastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "SecretAccessKey": response["Credentials"]["SecretAccessKey"],
                "Token": response["Credentials"]["SessionToken"],
                "Type": "AWS-assume-role",
                "Duration": session_duration,
            }
        except KeyError:
            raise PluginError(f"Unable to find all required fields in assume_role() AWS API response.")
        return credentials
