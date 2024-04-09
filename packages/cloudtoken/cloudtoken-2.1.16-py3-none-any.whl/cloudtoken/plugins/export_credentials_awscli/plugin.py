import copy
import os
from datetime import datetime, timezone
from typing import List

from cloudtoken.core import utils
from cloudtoken.core.abstract_classes import CloudtokenPlugin
from cloudtoken.core.exceptions import PluginError
from cloudtoken.core.helper_classes import CloudtokenOption


class Plugin(CloudtokenPlugin):
    name = "export_credentials_awscli"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def execute(self, data: dict) -> dict:
        credentials = utils.find_credentials(data)
        if not credentials:
            raise PluginError("Unable to find credetials provided by previous plugin.")

        credentials_filename = utils.get_aws_credentials_path()
        credentials_file_contents = utils.read_aws_credentials()

        profile_name = self._get_plugin_config(["profile"], "default")

        if "default" in credentials_file_contents:
            if not credentials_file_contents["default"].getboolean("cloudtoken"):
                timestamp = datetime.strftime(datetime.now(timezone.utc), "%Y-%m-%d-%H-%m-%S")
                credentials_file_contents[f"default_backup_{timestamp}"] = copy.deepcopy(
                    credentials_file_contents["default"]
                )

        aws_credentials = {
            "aws_access_key_id": credentials["AccessKeyId"],
            "aws_secret_access_key": credentials["SecretAccessKey"],
            "aws_session_token": credentials["Token"],
            "cloudtoken": "true",
            "expiration": credentials["Expiration"],
        }
        credentials_file_contents[profile_name] = aws_credentials

        if not os.path.exists(os.path.expanduser("~/.aws")):
            os.makedirs(os.path.expanduser("~/.aws"))

        with open(credentials_filename, "w") as fh:
            credentials_file_contents.write(fh)

        username = utils.get_system_username(self._config)
        utils.chown_file(credentials_filename, username)

        data = {}
        return data

    @classmethod
    def options(cls) -> List[CloudtokenOption]:
        options = [
            cls.add_option(["--profile"], type=str, help="Save credentials to specified AWS Profile."),
        ]

        return options
