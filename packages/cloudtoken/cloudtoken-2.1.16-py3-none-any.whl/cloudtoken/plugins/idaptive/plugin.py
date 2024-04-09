from __future__ import annotations

import importlib
import json
from typing import List
from urllib.parse import parse_qs, urlparse

import click
import requests
from cloudtoken.core import utils
from cloudtoken.core.abstract_classes import CloudtokenPlugin
from cloudtoken.core.exceptions import (
    AuthenticationError,
    ConfigurationError,
    PluginError,
)
from cloudtoken.core.helper_classes import CloudtokenOption
from requests import cookies
from requests.models import Response


class Plugin(CloudtokenPlugin):
    name = "idaptive"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._ensure_required_config()

        self._session = requests.session()
        self._init_session_headers()

        self._tenant_id = self._get_plugin_config(["tenant_id"])
        if not self._tenant_id:
            raise ConfigurationError("Required Idaptive configuration 'tenant_id' cannot be found.")

        self._vanity_id = self._get_plugin_config(["vanity_id"])
        self._base_url = self._get_initial_base_url()
        self._session_id = None
        self.mechanism_id = None

    @property
    def session_id(self):
        return self._session_id

    @session_id.setter
    def session_id(self, value):
        self._session_id = value

    @property
    def mechanism_id(self):
        return self._mechanism_id

    @mechanism_id.setter
    def mechanism_id(self, value):
        self._mechanism_id = value

    def execute(self, data: dict) -> dict:
        if utils.existing_valid_saml_credentials(data):
            return data[self.name]
        try:
            self._session.cookies = self._read_cookies()
            self._authenticate()
            saml_response = self._perform_appclick()

            data = {"saml_response": saml_response}
        except Exception as e:
            raise PluginError(f"Unable to execute SAML plugin: {e}")
        return data

    @classmethod
    def options(cls) -> List[CloudtokenOption]:
        options = [
            cls.add_option(["--mfa-passcode"], type=str, help="Specify the MFA passcode to use."),
            cls.add_option(
                ["--mfa-method"],
                type=click.Choice(["push", "phone", "passcode"]),
                help="Specify the MFA method.",
            ),
        ]
        return options

    def _read_cookies(self) -> cookies.RequestsCookieJar:
        """Return an existing cookiejar or create a new one if one doesn't exist."""
        cookiejar = utils.read_cookies()
        if cookiejar:
            return cookiejar
        return cookies.RequestsCookieJar()

    def _write_cookies(self):
        username = utils.get_system_username(self._config)
        utils.write_cookies(self._session.cookies, username)

    def _init_session_headers(self):
        """Add the standard headers to each request.

        :return: None
        """
        self._session.headers.update({"X-IDAP-NATIVE-CLIENT": "True"})
        self._session.headers.update({"CONTENT-TYPE": "application/json"})
        self._session.headers.update({"CACHE-CONTROL": "no-cache"})
        self._session.headers.update({"User-Agent": f"Cloudtoken {utils.get_version()}"})

        self._logger.debug(f"Session headers initialised to {self._session.headers}")

    def _ensure_required_config(self) -> None:
        required_fields = ["tenant_id", "appkey"]

        for field in required_fields:
            if not self._get_plugin_config([field]):
                raise ConfigurationError(f"Required configuration key '{field}' missing for Idaptive plugin.")

    def _post(self, path, payload) -> dict:
        response = None
        self._logger.debug(f"Making request to {path}")
        response = self._request(path=path, method=self._session.post, json=payload)
        try:
            json_response = response.json()
        except json.decoder.JSONDecodeError:
            self._logger.debug(f"Received a non-JSON response back for {self._base_url}{path}: {response.text}")
            raise PluginError(f"Received a non-JSON response back for {self._base_url}{path}")

        self._check_response_successful(json_response)

        # The redirect is requested as part of the JSON response, it's not a 301/302 unfortunately.
        if self._check_for_redirect(json_response):
            json_response = self._post(path, payload)
        return json_response

    def _get(self, path) -> Response:
        self._logger.debug(f"Making GET request to {path}")
        return self._request(path=path, method=self._session.get)

    def _request(self, path, method, *args, **kwargs) -> Response:
        url = f"{self._base_url}{path}"
        response = method(url, *args, **kwargs)
        response.raise_for_status()
        return response

    # TODO: Need to implement this
    # def _check_is_response_json(self, response):
    #     try:
    #         response = response.json()
    #         self._logger.debug(f"Received response {response}")
    #     except json.decoder.JSONDecodeError:
    #         self._logger.debug(f"Received a non-JSON response back for {url}: {response.text}")
    #         raise PluginError(f"Received a non-JSON response back for {url}")
    #     return response

    def _check_for_redirect(self, response: dict) -> bool:
        # The documentation is currently wrong about this. It says 'PodFqdn' is in the 'Summary' field, nope.
        # https://developer.idaptive.com/docs/adaptive-authentication#section-initiating-authentication
        if "PodFqdn" in response["Result"]:
            podfqdn = response["Result"]["PodFqdn"]

            # Idaptive keeps sending "PodFqdn" key in the response, even after you're using the new url.
            if f"https://{podfqdn}" == self._base_url:
                return False

            self._base_url = f"https://{podfqdn}"
            self._logger.debug(f"Idaptive requesting we use {self._base_url} for future requests.")
            return True
        return False

    def _get_initial_base_url(self) -> str:
        idaptive_domain = self._get_plugin_config(["domain_name"])
        if not idaptive_domain:
            idaptive_domain = "my.idaptive.app"
        host = self._vanity_id or self._tenant_id
        if not host:
            raise ConfigurationError("No Idaptive vanity_id or tenant_id configured.")
        return f"https://{host}.{idaptive_domain}"

    def _authenticate(self) -> None:
        if ".ASPXAUTH" in self._session.cookies:
            self._logger.debug("Found existing .ASPX auth cookie.")

        response = self._start_authentication()

        if self._is_login_successful(response):
            self._logger.debug("Authentication successful.")
            return

        if not self._is_new_auth_package(response):
            raise PluginError(f"Unexpected Idaptive summary value '{response['Result']['Summary']}'")

        response = self._advance_authentication(response)

        if not self._is_login_successful(response):
            self._logger.debug("Authentication was unsuccessful.")
            raise PluginError(response["Message"])

    def _start_authentication(self) -> dict:
        path = "/Security/StartAuthentication"
        payload = {
            "TenantId": self._tenant_id,
            "User": utils.get_username(self._config),
            "Version": "1.0",
        }
        self._logger.debug(f"Starting authentication with payload: {payload}")
        response = self._post(path=path, payload=payload)
        return response

    def _advance_authentication(self, response):
        challenges = response["Result"]["Challenges"]
        self.session_id = response["Result"]["SessionId"]
        response = self._execute_challenges(challenges)
        self._write_cookies()
        return response

    def _execute_challenges(self, challenges):
        num_challenges = len(challenges)
        self._logger.debug(f"Received {num_challenges} challenges")
        for index, challenge in enumerate(challenges):
            self._logger.debug(f"Executing challenge {index + 1} of {num_challenges}")
            response = self._execute_challenge(challenge)

            # Return once we've passed enough challenges and our login was successful.
            if self._is_login_successful(response):
                return response

            # We can be provided with a whole new set of challenges at any time.
            if self._is_new_auth_package(response):
                self._logger.debug(f"New challange package found in response. Executing new package.")
                return self._execute_challenges(response["Result"]["Challenges"])

        raise PluginError("Exhausted all authentication challenges without success.")

    def _execute_challenge(self, challenge):
        path = "/Security/AdvanceAuthentication"
        # Put the data into a more usable structure, keyed by a identifier.
        mechanisms = {}
        for mechanism in challenge["Mechanisms"]:
            try:
                name = mechanism["UiPrompt"] if mechanism.get("UiPrompt", None) else mechanism["PromptSelectMech"]
            except KeyError:
                self._logger.debug(f"Detected unknown mechanism without UiPrompt or PromptSelectMech: {mechanism}")
                continue
            mechanisms[name] = mechanism
        self._logger.debug(f"Challenge mechanisms: {[mechanism['Name'] for mechanism in mechanisms.values()]}")
        friendly_name, mechanism_id = self._determine_auth_mechanism(mechanisms)
        self.mechanism_id = mechanism_id
        type_name = mechanisms[friendly_name]["Name"]
        self.mechanism = mechanisms[friendly_name]
        answer = self._execute_mechanism(type_name)

        if type_name == "DUO":
            # out-of-bounds Duo handler returns JSON response from API calls
            return answer
        else:

            payload = {
                "TenantId": self._tenant_id,
                "SessionId": self.session_id,
                "MechanismId": self.mechanism_id,
                "Action": "Answer",
                "Answer": answer,
            }
            self._logger.debug(f"Answer payload for challenge mechanism {friendly_name} of type {type_name}")

            return self._post(path=path, payload=payload)

    def _execute_mechanism(self, name: str):
        self._logger.debug(f"Executing challenge mechanism {name}")
        name = name.lower()
        handler = self._import_mechanism_handler(name)
        return handler(self._config, self)

    def _import_mechanism_handler(self, name: str):
        try:
            self._logger.debug(f"Importing mechanism handler {name}")
            module = importlib.import_module(f"cloudtoken.plugins.idaptive.mechanisms.{name}")
            handler = getattr(module, "handler")
        except (ModuleNotFoundError, AttributeError):
            raise PluginError(f"Unable to find authentication handler for {name} mechanism")
        else:
            return handler

    def _determine_auth_mechanism(self, mechanisms):
        auth_preferences = self._get_plugin_config(["auth_preferences"])

        if not auth_preferences:
            name, mechanism_id = self._prompt_for_auth_mechanism(mechanisms)
            return name, mechanism_id

        for auth_preference in auth_preferences:
            if mechanisms.get(auth_preference):
                self._logger.debug(
                    f"Found auth preference {auth_preference} which is of type {mechanisms[auth_preference]['Name']}"
                )
                return auth_preference, mechanisms[auth_preference]["MechanismId"]

        name, mechanism_id = self._prompt_for_auth_mechanism(mechanisms)
        return name, mechanism_id

    def _list_auth_mechanisms(self, mechanisms):
        click.echo("Available authentication methods: ")
        index = 1
        for name, mechanism in mechanisms.items():
            name = mechanism["UiPrompt"] if mechanism.get("UiPrompt", None) else mechanism["PromptSelectMech"]
            click.echo(f"    {index}. {name}")
            index += 1

    def _prompt_for_auth_mechanism(self, mechanisms):
        self._list_auth_mechanisms(mechanisms)

        valid_choices = [i for i in range(1, len(mechanisms) + 1)]
        self._logger.debug(f"Valid choices {valid_choices}")
        choice = None

        if len(mechanisms) == 1:
            choice = 1
            name = [m for m in mechanisms][0]
            click.echo(f"Auto selecting method: {name}")

        while not choice:
            choice = click.prompt("Select authentication method", type=int)
            if choice not in valid_choices:
                choice = None
                click.echo("Invalid selection.")

        choice -= 1
        name = [m for m in mechanisms][choice]
        mechanism_id = mechanisms[name]["MechanismId"]
        return name, mechanism_id

    def _get_auth_mechanism_details_from_selection(self, selection, mechanisms):
        index = selection - 1  # Selections are printed to screen with a starting index of 1.
        name = [m for m in mechanisms][index]
        return name, mechanisms[name]["MechanismId"]

    def _is_login_successful(self, response):
        try:
            return response["Result"]["Summary"] == "LoginSuccess"
        except KeyError:
            self._logger.debug(f"Response received {response}")
            raise PluginError("Invalid JSON response from Idaptive.")

    def _check_response_successful(self, response) -> None:
        if response["success"]:
            return
        self._logger.debug(f"Request to Idaptive failed {response}")
        message = response["Message"]
        if message.startswith("Authentication (login or challenge) has failed"):
            raise AuthenticationError(
                f"Authentication (login or challenge) has failed. Normal causes of this include recently changing your password (try 'cloudtoken --password-prompt'), MFA failing to authenticate or not being on a VPN."
            )
        raise PluginError(response["Message"])

    def _perform_appclick(self):
        appkey = self._get_plugin_config(["appkey"])
        self._logger.debug(f"Performing appclick on {appkey}")
        path = f"/uprest/HandleAppClick?appkey={appkey}"  # TODO; Does this work if privilege escalation is not required for the app?
        response = self._get(path)

        if "elevate" in response.url:
            response = self._elevate_privileges(response)

        return utils.get_saml_response_from_html(response.content)

    def _is_new_auth_package(self, response):
        try:
            return response["Result"]["Summary"] == "NewPackage"
        except KeyError:
            self._logger.debug(f"Response received {response}")
            raise PluginError("Invalid JSON response from Idaptive.")

    def _elevate_privileges(self, response):
        self._logger.debug("Elevating privileges")
        try:
            obj = urlparse(response.url)
            query_params = parse_qs(obj.query)
            elevate_key = query_params["elevate"][0]
            challenge_id = query_params["challengeId"][0]
        except Exception:
            raise PluginError("Unable to extract challengeId when attempting to escalate privileges.")

        self._logger.debug(f"Elevated privileges successfully.")
        # self._logger.debug(f"Elevated privileges with key {elevate_key} and {challenge_id}")

        path = "/security/startchallenge"
        payload = {
            "Version": "1.0",
            "elevate": elevate_key,
            "ChallengeStateId": challenge_id,
        }

        response = self._post(path, payload)

        response = self._advance_authentication(response)
        if not self._is_login_successful(response):
            raise PluginError(response["Message"])

        appkey = self._get_plugin_config(["appkey"])
        path = f"/run?appkey={appkey}&elevate{elevate_key}=&challengeId={challenge_id}"
        return self._get(path)
