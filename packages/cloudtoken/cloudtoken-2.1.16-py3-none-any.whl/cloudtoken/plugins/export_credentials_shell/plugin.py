from cloudtoken.core.abstract_classes import CloudtokenPlugin
from cloudtoken.core.exceptions import PluginError
from cloudtoken.core.helper_classes import CloudtokenOption
from typing import List
from cloudtoken.core import utils
import os


class Plugin(CloudtokenPlugin):
    name = "export_credentials_shell"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def execute(self, data: dict) -> dict:
        print(
            f"The {self.name} plugin has been deprecated. Please move to using `--export` option or the `export_credentials_awscli` plugin."
        )

        credentials = utils.find_credentials(data)
        if not credentials:
            raise PluginError("Unable to find credetials provided by previous plugin.")

        self.write_credentials(credentials)
        return {}

    @classmethod
    def options(cls) -> List[CloudtokenOption]:
        return []

    def write_credentials(self, credentials):
        envvars = [
            ("AWS_ACCESS_KEY_ID", "{AWS_ACCESS_KEY_ID}"),
            ("AWS_SECRET_ACCESS_KEY", "{AWS_SECRET_ACCESS_KEY}"),
            ("AWS_SECURITY_TOKEN", "{AWS_SECURITY_TOKEN}"),
            ("AWS_SESSION_TOKEN", "{AWS_SECURITY_TOKEN}"),
            ("AWS_EXPIRATION", "{AWS_EXPIRATION}"),
            ("AWS_ACCOUNT_ID", "{AWS_ACCOUNT_ID}"),
        ]

        template = "#!{SHELL}\n"
        shell = os.environ["SHELL"]
        if shell.endswith("fish"):
            template += "\n".join(["set -xU " + p[0] + " " + p[1] for p in envvars])
        else:
            template += "\n".join(["export " + p[0] + "=" + p[1] for p in envvars])

        template = template.format(
            AWS_ACCESS_KEY_ID=credentials["AccessKeyId"],
            AWS_SECRET_ACCESS_KEY=credentials["SecretAccessKey"],
            AWS_SECURITY_TOKEN=credentials["Token"],
            AWS_SESSION_TOKEN=credentials["Token"],
            AWS_EXPIRATION=credentials["Expiration"],
            AWS_ACCOUNT_ID=credentials["AccountId"],
            SHELL=shell,
        )

        token_filename = utils.get_config_dir() / "tokens.shell"
        with open(token_filename, "w") as fh:
            fh.write(template)
        username = utils.get_system_username(self._config)
        utils.chown_file(token_filename, username)
