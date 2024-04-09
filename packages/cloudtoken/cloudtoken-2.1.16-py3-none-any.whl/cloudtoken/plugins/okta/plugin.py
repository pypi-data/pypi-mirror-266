from __future__ import annotations
from urllib.error import HTTPError
from urllib.parse import urlunparse, ParseResult, quote, urlencode

import click
import requests
from typing import List

from datetime import datetime, timedelta
from time import sleep

from cloudtoken.core import utils
from cloudtoken.core.abstract_classes import CloudtokenPlugin
from cloudtoken.core.exceptions import (
    AuthenticationError,
    ConfigurationError,
)
from cloudtoken.core.helper_classes import CloudtokenOption
from cloudtoken.plugins.okta.exceptions import OktaError


class Plugin(CloudtokenPlugin):
    name = "okta"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._ensure_required_config()

        self._session = requests.session()
        self._init_session_headers()

        self._okta_domain = self._get_plugin_config(["okta_domain"])
        self._aws_app_id = self._get_plugin_config(["aws_app_id"])
        self._client_id = self._get_plugin_config(["client_id"])

    def _api_endpoint(self, path='', query=[]):
        """
        Create a full Okta URL for an API Path with optionl query parameters
        """
        return urlunparse(
            ParseResult(
                scheme='https', 
                netloc=self._okta_domain,
                path=quote(path),
                query=urlencode(query),
                params='',
                fragment='')
        )

    def _ensure_required_config(self) -> None:
        required_fields = ["okta_domain", "aws_app_id", "client_id"]

        for field in required_fields:
            if not self._get_plugin_config([field]):
                raise ConfigurationError(f"Required configuration key '{field}' missing for okta plugin.")

    def _init_session_headers(self):
        self._session.headers.update({"CACHE-CONTROL": "no-cache"})
        self._session.headers.update({"User-Agent": f"Cloudtoken {utils.get_version()}"})
        self._session.headers.update({"Accept": "application/json"})

    def execute(self, data: dict) -> dict:
        if utils.existing_valid_saml_credentials(data):
            return data[self.name]

        # step 1 - initiate device authorization
        auth_body = self.initate_authorization()
        self.user_mfa_url(auth_body['verification_uri_complete'])

        # step 2 - poll Okta until the user authentication is complete
        auth_complete_body = self.poll_for_auth_complete(auth_body)

        # step 3 - request API Token from Okta once MFA is complete
        token_body = self.get_access_token(auth_complete_body)

        # step 4 - retrieve SAML assertion with access token
        saml_body = self.get_saml_assertion(token_body)

        data = {"saml_response": saml_body}
        return data

    def initate_authorization(self):
        # /oauth2/v1/device/authorize
        try:
            utils.logger("initialising authoration with Okta: /oauth2/v1/device/authorize")
            response = self._session.post(
                self._api_endpoint(path='/oauth2/v1/device/authorize'),
                data={
                    'client_id': self._client_id,
                    'scope': 'openid okta.apps.sso okta.apps.read'
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            return response.json()
        except HTTPError:
            utils.logger(f"Okta API Call failed for endpoint /oauth2/v1/device/authorize - Status Code {response.status_code}")
            raise AuthenticationError("Failed to authenticate with Okta")

    def user_mfa_url(self, url):
        """
        Prompt user for MFA completion based on config options
        """
        mfa_output = self._get_plugin_config(["mfa_url_output"])
        if mfa_output == "cli":
            print(f"Complete MFA by following this link: {url}")
        else: # browser is default
            print(f"Opening browser to complete MFA at: {url}")
            click.launch(url)


    def poll_for_auth_complete(self, auth_body):
        """
        Poll for user authentication completion

        Example auth_body:
        {
            "device_code": "b40d6dfe-fdd2-4da0-93ab-6640ae2301a0",
            "user_code": "SSVMWWVS",
            "verification_uri": "https://test.oktapreview.com/activate",
            "verification_uri_complete": "https://test.oktapreview.com/activate?user_code=SSVMWWVS",
            "expires_in": 600,
            "interval": 5
        }
        """

        timeout = datetime.now() + timedelta(seconds=int(auth_body['expires_in']))
        interval = int(auth_body['interval'])
        device_code = auth_body['device_code']

        response = None

        utils.logger("polling Okta until MFA is completed")
        while datetime.now() <= timeout:
            try:
                response = self._session.post(
                    self._api_endpoint(path='/oauth2/v1/token'),
                    data={
                        'client_id': self._client_id,
                        'device_code': device_code,
                        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
            except HTTPError:
                utils.logger(f"Okta API Error /oauth2/v1/token - status code {response.status_code}")
                raise AuthenticationError("Okta authenication failed while polling for MFA")

            if response.status_code == 200:
                # return when MFA is complete (code 200) 
                return response.json()

            sleep(interval) # wait for specified interval

        utils.logger(f"Okta MFA was not completed before timeout - {timeout}")
        raise AuthenticationError("MFA was not completed before timeout")
        
    def get_access_token(self, auth_complete_body):
        """
        Retrieve Access token from Okta once MFA is complete
        example auth_complete_body:
        {
            "token_type": "Bearer",
            "expires_in": 3600,
            "access_token": "abc",
            "scope": "openid okta.apps.sso okta.apps.read",
            "id_token": "def"
        }
        """
        try:
            utils.logger("Requesting Authentication token from Okta - /oauth2/v1/token ")
            response = self._session.post(
                self._api_endpoint(path='/oauth2/v1/token'),
                data={
                    'actor_token': auth_complete_body['access_token'],
                    'actor_token_type': 'urn:ietf:params:oauth:token-type:access_token',
                    'audience': f'urn:okta:apps:{self._aws_app_id}',
                    'client_id': self._client_id,
                    'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
                    'requested_token_type': 'urn:okta:oauth:token-type:web_sso_token',
                    'subject_token': auth_complete_body['id_token'],
                    'subject_token_type': 'urn:ietf:params:oauth:token-type:id_token'
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            response.raise_for_status()
            return response.json()
        except HTTPError:
            utils.logger(f"Okta API Call failed for endpoint /oauth2/v1/token - Status Code {response.status_code}")
            raise AuthenticationError("Failed to authenticate with Okta")

    def get_saml_assertion(self, token_body):
        """
        Retrieve a SAML assertion once an API Token has been retrieved 
        Example token_body:
        {
            "token_type": "...",
            "expires_in": 300,
            "access_token": "<some_token>",
            "issued_token_type": "urn:okta:oauth:token-type:web_sso_token"
        }
        """
        try:
            utils.logger("retrieving SAML assertion from Okta /login/token/sso")
            response = self._session.get(
                self._api_endpoint(path='/login/token/sso', query={'token': token_body["access_token"]}),
                # override the standard application/json becuase SAML is returned as webpage
                headers={'Accept': 'text/html'} 
            )
            response.raise_for_status()

            return utils.get_saml_response_from_html(response.content)

        except HTTPError:
            utils.logger(f"Error retrieving SAML Assertion from Okta - /login/token/sso - status code {response.status_code}")
            raise OktaError("Unable to retrieve SAML Assertion from Okta")


    @classmethod
    def options(cls) -> List[CloudtokenOption]:
        options = [
            cls.add_option(["--mfa-url-output"], type=click.Choice(["browser", "cli"]), help="Configure how the Okta MFA url should be presented")
        ]
        return options