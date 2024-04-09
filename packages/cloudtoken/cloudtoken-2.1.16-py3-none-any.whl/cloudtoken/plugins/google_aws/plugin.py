from typing import List

import requests
from cloudtoken.core import utils
from cloudtoken.core.abstract_classes import CloudtokenPlugin
from cloudtoken.core.exceptions import ConfigurationError, PluginError
from cloudtoken.core.helper_classes import CloudtokenOption
from pyquery import PyQuery

from .google_auth import Google


class Plugin(CloudtokenPlugin):
    name = "google_aws"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._session = requests.session()

    @classmethod
    def options(cls) -> List[CloudtokenOption]:
        options = [
            cls.add_option(["--idp-id", "-I"], type=str, help="Google SSO IDP identifier ($GOOGLE_IDP_ID)."),
            cls.add_option(["--sp-id", "-S"], type=str, help="Google SSO SP identifier ($GOOGLE_SP_ID)."),
        ]

        return options

    def execute(self, data: dict) -> dict:
        credentials = utils.find_credentials(data)
        if not credentials:
            raise PluginError("Unable to find credetials provided by previous plugin.")

        self._session.cookies = self._read_cookies()

        try:
            google_client = Google(self._config, self._session)
            google_client.do_login()
            html = PyQuery(google_client.session_state.text)
            response = html("input[@name='SAMLResponse']")
            if response:
                saml_response = response[0].value
            else:
                raise Exception("SAML Response not found in response from Google {}".format(response))

            self._session = google_client.session
            if not self._get_config(["daemon"]):
                self._write_cookies()
        except AttributeError as e:
            raise PluginError(f"Unable to login to Google AWS IdP: {e}")

        data = {}
        return data

    def _write_cookies(self):
        username = utils.get_system_username(self._config)
        utils.write_cookies(self._session.cookies, username)

    def _read_cookies(self) -> requests.cookies.RequestsCookieJar:
        """Return an existing cookiejar or create a new one if one doesn't exist."""
        cookiejar = utils.read_cookies()
        if cookiejar:
            return cookiejar
        return requests.cookies.RequestsCookieJar()
