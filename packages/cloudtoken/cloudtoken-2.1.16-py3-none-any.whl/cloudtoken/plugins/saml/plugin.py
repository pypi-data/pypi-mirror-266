from __future__ import annotations

import base64
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import NamedTuple

import boto3
import click
from botocore.exceptions import EndpointConnectionError
from cloudtoken.core import utils
from cloudtoken.core.abstract_classes import CloudtokenPlugin
from cloudtoken.core.exceptions import ExportCredentials, InvalidRoleIndex, NoRolesFoundError, PluginError
from cloudtoken.core.helper_classes import CloudtokenOption


class Arn(NamedTuple):
    role: str
    idp: str


class Plugin(CloudtokenPlugin):
    name = "saml"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def execute(self, data: dict) -> dict:
        if utils.existing_valid_saml_credentials(data):
            return data[self.name]
        saml_response = self._find_saml_response_in_data(data)
        if not saml_response:
            raise PluginError("Unable to find SAMLResponse provided by previous plugin.")

        roles = self._generate_role_list(base64.b64decode(saml_response))

        if not roles:
            raise NoRolesFoundError("No roles found in SAML response.")

        # Refresh the last role or filter on pattern if pattern provided.
        pattern = self._get_plugin_config(["filter"])
        if self._get_plugin_config(["refresh"]):
            state_data = utils.read_state()
            if not state_data:
                print("No previous state found.")
            else:
                try:
                    last_role = state_data["LastRole"]
                    pattern = rf"^{last_role}$"
                except Exception as e:
                    raise PluginError("No previous role found in state data.")

        if pattern:
            roles = self._filter_role_list(pattern, roles)

        if not roles:
            raise NoRolesFoundError("No roles found matching filter.")

        roles = self._sort_roles(roles)

        if self._get_plugin_config(["numbers_only"]):
            self._print_roles(roles, numbers_only=True)
            raise SystemExit

        if self._get_plugin_config(["list"]):
            self._print_roles(roles)
            raise SystemExit

        role, role_index = self._select_role(roles, self._get_plugin_config(["role_number"]))

        # We do this so the plugin knows which role to use for future exections in daemon mode.
        self._set_config(self.name, role.role, "filter")

        credentials = self._assume_role(role, saml_response)

        if self._get_plugin_config(["export"]):
            raise ExportCredentials(
                access_key=credentials["AccessKeyId"],
                secret_key=credentials["SecretAccessKey"],
                token=credentials["Token"],
                expiration=credentials["Expiration"],
                account_id=credentials["AccountId"],
            )

        data = {"credentials": credentials}
        return data

    @classmethod
    def options(cls) -> list[CloudtokenOption]:
        options = [
            cls.add_option(["--list", "-l"], is_flag=True, help="List available Roles."),
            cls.add_option(["--filter", "-f"], type=str, help="Filter available Roles on TEXT."),
            cls.add_option(
                ["--numbers-only", "-n"], is_flag=True, help="List only the Role numbers, useful for automation."
            ),
            cls.add_option(["--refresh"], is_flag=True, help="Refresh credentials for the last selected Role."),
            cls.add_option(["--role-number", "-r"], type=int, help="Select a Role by its number."),
            cls.add_option(
                ["--export"], is_flag=True, help="Print credentials to stdout in a form that can used in eval()."
            ),
            cls.add_option(["--session-duration"], type=int, help="Specify AWS Role session duration."),
        ]

        return options

    def _find_saml_response_in_data(self, data: dict):
        try:
            for plugin_name, plugin_data in data.items():
                for key, value in plugin_data.items():
                    if key == "saml_response":
                        return value
        except Exception:
            raise PluginError("Unable to find valid SAMLResponse in passed plugin data.")
        return None

    def _generate_role_list(self, saml_response: bytes) -> list[Arn]:
        namespaces = {
            "ds": "http://www.w3.org/2000/09/xmldsig#",
            "html": "http://www.w3.org/1999/xhtml",
            "saml": "urn:oasis:names:tc:SAML:2.0:assertion",
            "samlp": "urn:oasis:names:tc:SAML:2.0:protocol",
            "xs": "http://www.w3.org/2001/XMLSchema",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        }

        saml = ET.fromstring(saml_response)
        elements = saml.find(
            ".//{urn:oasis:names:tc:SAML:2.0:assertion}Attribute[@Name='https://aws.amazon.com/SAML/Attributes/Role']",
            namespaces=namespaces,
        )
        if not elements:
            raise NoRolesFoundError("No roles found.")

        roles = []
        for child in elements:
            arns = child.text.split(",")
            if ":saml-provider/" in arns[0]:
                arn = Arn(role=arns[1], idp=arns[0])
            else:
                arn = Arn(role=arns[0], idp=arns[1])
            roles.append(arn)
        return roles

    def _filter_role_list(self, pattern: str, roles: list[Arn]) -> list[Arn]:
        p = re.compile(pattern, re.IGNORECASE)
        filtered_list = []
        for role in roles:
            if p.search(role.role):
                filtered_list.append(role)
        return filtered_list

    def _sort_roles(self, roles: list[Arn]) -> list[Arn]:
        roles.sort(key=lambda role: role.role)
        return roles

    def _print_roles(self, roles, numbers_only=False) -> None:
        click.echo("Available roles:")

        for index, role in enumerate(roles):
            if numbers_only:
                click.echo(index + 1)
            else:
                click.echo(f"    {index + 1}. {role.role}")

    def _role_selection_prompt(self, roles):
        click.echo()
        selection = None
        while not selection:
            selection = click.prompt("Select Role", type=int)
            if selection not in [i for i in range(1, len(roles) + 1)]:
                selection = None
                continue

        return selection

    def _select_role(self, roles: list, selection: int = None):
        if len(roles) == 1:
            selection = 0

            if not self._get_config(["quiet"]):
                click.echo(f"Auto selecting role: {roles[selection].role}")
            return roles[selection], selection

        if not selection:
            self._print_roles(roles)
            selection = self._role_selection_prompt(roles)

        # Because we print the Role numbers starting at 1, but lists are indexed from 0.
        if selection:
            selection -= 1

        if not self._get_config(["quiet"]):
            try:
                role_arn = roles[selection].role
            except IndexError:
                raise InvalidRoleIndex("Specified role is invalid.")
            click.echo(f"Assumed {role_arn}")
        return roles[selection], selection

    def _assume_role(self, arn: Arn, saml_response: str) -> dict:
        try:
            client = boto3.client("sts")
            session_duration = self._get_plugin_config(["session_duration"], 3600)

            if session_duration < 900:
                raise PluginError("Session duration must be at least 900 seconds.")

            response = client.assume_role_with_saml(
                RoleArn=arn.role, PrincipalArn=arn.idp, SAMLAssertion=saml_response, DurationSeconds=session_duration
            )
        except EndpointConnectionError as e:
            raise PluginError(f"{e} - This is normally due to incorrect region setting in ~/.aws/config or equivalent")
        except Exception as e:
            raise PluginError(f"Failed to assume role: {e}")  # TODO: Include error msg

        try:
            credentials = {
                "AccessKeyId": response["Credentials"]["AccessKeyId"],
                "AccountId": arn.role.split(":")[4],
                "Code": "Success",
                "Expiration": response["Credentials"]["Expiration"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "Issuer": response["Issuer"],
                "LastRole": arn.role,
                "LastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "SAMLProvider": arn.idp,
                "SecretAccessKey": response["Credentials"]["SecretAccessKey"],
                "Token": response["Credentials"]["SessionToken"],
                "Type": "AWS-HMAC",
                "Duration": session_duration,
                "AssumedRoleSessionName": response["AssumedRoleUser"]["AssumedRoleId"].split(":")[1]
            }
        except KeyError:
            raise PluginError(f"Unable to find all required fields in assume_role_with_saml() AWS API response.")

        return credentials
