import json
import os
from pathlib import Path
from typing import List

from cloudtoken.core import utils
from cloudtoken.core.abstract_classes import CloudtokenPlugin
from cloudtoken.core.helper_classes import CloudtokenOption


class Plugin(CloudtokenPlugin):
    name = "export_credentials_json"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @classmethod
    def options(cls) -> List[CloudtokenOption]:
        options = [
            cls.add_option(["--temp", "-t"], is_flag=True, help="Export tokens to current shell only."),
        ]

        return options

    def execute(self, data: dict) -> dict:
        credentials = utils.find_credentials(data)

        if self._get_plugin_config(["temp"]):
            self._echo_credentials_to_shell(credentials)
        else:
            self._write_json_tokens(credentials)

        data = {}
        return data

    @staticmethod
    def _get_default_json_filename_path():
        filename = utils.get_config_dir() / "tokens.json"
        return filename

    def _write_json_tokens(self, credentials):
        # https://stackoverflow.com/questions/2333872/atomic-writing-to-file-with-python
        filename = self._get_plugin_config(["json_tokens"], self._get_default_json_filename_path())
        tmp_file = Path(f"{filename}.tmp")
        with open(tmp_file, "w") as fh:
            fh.write(json.dumps(credentials))
            fh.flush()
            os.fsync(fh.fileno())
            os.chmod(tmp_file, 0o600)
        os.rename(tmp_file, filename)
        utils.chown_file(filename, utils.get_system_username(self._config))

    def _echo_credentials_to_shell(self, credentials):
        utils.echo(f"export AWS_ACCESS_KEY_ID={credentials['AccessKeyId']}")
        utils.echo(f"export AWS_SECRET_ACCESS_KEY={credentials['SecretAccessKey']}")
        utils.echo(f"export AWS_SESSION_TOKEN={credentials['Token']}")
        utils.echo(f"export AWS_EXPIRATION={credentials['Expiration']}")
