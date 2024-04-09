"""Main Cloudtoken module."""
from __future__ import annotations

import copy
import logging
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Union

from cloudtoken.core import utils
from cloudtoken.core.daemon import Daemon
from cloudtoken.core.exceptions import CloudtokenException, ExportCredentials, PluginError
from cloudtoken.core.networking import Networking


class Cloudtoken:
    """Cloudtoken"""

    def __init__(self, config: dict):
        self._logger = logging.getLogger("cloudtoken.core")
        self.config = config
        self._plugins = defaultdict(list)
        self._thread_lock = threading.Lock()
        self._thread_event = threading.Event()
        self._data: dict = {}
        self._networking = Networking()

    def run(self) -> None:
        """Run Cloudtoken."""
        # Make a deep copy to ensure we don't accidentally replace the real
        # values with *****
        clean_config = copy.deepcopy(self.config)
        if not self.get_config_value(["debug-with-secrets"]):
            clean_config["defaults"]["password"] = "*****"
        self._logger.debug(f"Initialising Cloudtoken() with config {clean_config}")
        del clean_config
        utils.initialize_configuration_directory()
        utils.check_for_shell_additions()
        self._load_plugins()

        daemon_httpd_thread = None
        if self.get_config_value(["daemon"]):
            self._remove_existing_aws_credentials_default_profile()
            self._networking.configure()
            daemon_httpd_thread = self._start_daemon_mode()

        self._start_plugins_threads(daemon_httpd_thread)

    def _start_plugins_threads(self, daemon_httpd_thread=None) -> None:
        """Plugins are run in a separate thread.

        :param daemon_httpd_thread: Thread object representing the Flask HTTPD interface, defaults to None
        :type daemon_httpd_thread: Thread, optional

        :returns: None
        """
        t = threading.Thread(
            name="cloudtoken_plugins",
            target=self._run_plugins,
            daemon=True,
            kwargs={"daemon_httpd_thread": daemon_httpd_thread},
        )
        t.start()
        t.join()

    def _run_plugins(self, daemon_httpd_thread=None):
        """We run the plugins sequentially in their own thread.

        :param daemon_httpd_thread: [description], defaults to None
        :type daemon_httpd_thread: [type], optional
        :raises SystemExit: [description]
        """
        try:
            daemon_mode = self.get_config_value(["daemon"])
            while True:
                self._logger.debug(f"Running plugins {dict(self._plugins)}")
                for plugin_category, plugins in self._plugins.items():
                    # Don't run post_auth plugins in daemon mode as writing out the
                    # credentials to the standard location will prevent the SDKs from
                    # looking at the metadata endpoint.
                    if daemon_mode and plugin_category == "post_auth":
                        continue
                    for plugin in plugins:
                        self._execute_plugin(plugin)

                # Write some state information into the cloudtoken dir
                utils.write_state(self._data, self.config)

                if not daemon_mode:
                    break
                # Signal the daemon thread that it can proceed. Only required on startup so we prompt for any auth
                # tokens, etc before Flask takes over the screen.
                self._thread_event.set()
                self._sleep(daemon_httpd_thread)
        except Exception as e:
            msg = f"Unable to execute plugin {plugin}: {e}"
            if self.get_config_value(["debug"]):
                raise PluginError(msg) from e
            else:
                # Need to `print` otherwise `SystemExit` doesn't print anything
                # to stdout in a thread
                print(msg)
                raise SystemExit(msg)

    def _execute_plugin(self, plugin):
        utils.acquire_lock(self._thread_lock)
        try:
            self._data[str(plugin)] = plugin.execute(data=self._data)
        except ExportCredentials as e:
            utils.export_credentials_to_stdout(credentials=e)
            raise SystemExit(0)
        utils.release_lock(self._thread_lock)

    def _sleep(self, daemon_thread=None):
        """When in daemon mode sleep inbetween credential refreshes/plugin runs.

        :param daemon_thread: [description], defaults to None
        :type daemon_thread: [type], optional
        :raises SystemExit: [description]
        """
        interval = self._get_refresh_interval()
        sleep_until = datetime.now(timezone.utc) + timedelta(seconds=interval)
        self._logger.debug(f"Sleeping _run_plugins thread for {interval} seconds until {sleep_until}.")
        # We need to check every X seconds if the daemon thread is still alive and quit if it is not.
        while datetime.now(timezone.utc) < sleep_until:
            self._logger.debug("Checking if daemon thread is still alive.")
            if not daemon_thread.is_alive():
                self._logger.debug("Daemon thread is dead. Exiting.")
                raise SystemExit(1)
            time.sleep(5)
        self._logger.debug("Sleep period finished.")

    def _get_refresh_interval(self):
        refresh_interval = self.get_config_value(["refresh_interval"])
        if refresh_interval:
            self._logger.debug(f"Refresh interval of {refresh_interval} provided on the command line")
            return self.get_config_value(["refresh_interval"])
        return self._determine_refresh_timestamp_from_credential_expiry()

    def _determine_refresh_timestamp_from_credential_expiry(self):
        credentials = utils.find_credentials(self._data)
        if not credentials:
            raise CloudtokenException("Unable to find credentials when attempting to determine refresh interval.")

        tmp_dt = datetime.strptime(credentials["Expiration"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        expiration_dt = tmp_dt - timedelta(minutes=5)
        utc_dt = datetime.now(timezone.utc)
        if expiration_dt <= utc_dt:
            self._logger.debug("Credentials have already expired. Will refresh immediately.")
            return 0

        # Refresh when the credentials are within 5 minutes of expiring.
        self._logger.debug(f"Credentials will be refreshed at {expiration_dt}")
        refresh_in = expiration_dt.timestamp() - utc_dt.timestamp()
        return refresh_in

    def get_config_value(self, *args: Union[str, list]) -> Any:
        return utils.get_config_value(self.config, *args)

    def _load_plugins(self) -> None:
        """Iterate through each plugin and load it.

        :return: None.
        """
        for plugin_priority, plugins in self.config["plugins"].items():
            for plugin in plugins:
                self._load_plugin(plugin_priority, plugin)

    def _load_plugin(self, plugin_priority: str, plugin: str) -> None:
        """Load a specific plugin.

        :param plugin_priority: Which priority this plugin should run at.
        :type plugin_priority: str
        :param plugin: The name of the plugin.
        :type plugin: str
        :raises PluginError: When the plugin object cannot be instantiated.
        """
        if not self.is_plugin_loaded(plugin_priority, plugin):
            self._logger.debug(f"Loading plugin {plugin_priority}:{plugin}")
            Plugin = utils.import_plugin(plugin)
            if not Plugin:
                return
            try:
                plugin = Plugin(config=self.config)  # type: ignore
                self._plugins[plugin_priority].append(plugin)
            except Exception as e:
                raise PluginError(f"Unable to initialise plugin: {plugin}") from e

    def is_plugin_loaded(self, priority: str, plugin: str) -> bool:
        """Check if a plugin has already been loaded.

        :param priority: Plugin priority, e.g pre_auth, auth, post_auth.
        :type priority: str
        :param plugin: Name of plugin.
        :type plugin: str
        :return: True if plugin is loaded, False if not.
        :rtype: bool
        """
        for existing_plugin in self._plugins[priority]:
            if str(plugin) == str(existing_plugin):
                self._logger.info(f"Plugin {priority}:{plugin} has already been loaded.")
                return True
        return False

    def _start_daemon_mode(self):
        self._thread_event.clear()
        self._logger.debug("Starting daemon mode")
        t = threading.Thread(
            name="cloudtoken_daemon",
            target=Daemon,
            daemon=True,
            kwargs={"config": self.config, "lock": self._thread_lock, "event": self._thread_event, "data": self._data},
        )
        t.start()
        return t

    def _remove_existing_aws_credentials_default_profile(self):
        """Remove an existing 'default' profile from the AWS credentials file
        if one exists.
        """
        credentials = utils.read_aws_credentials()
        if utils.is_aws_profile_managed_by_cloudtoken(credentials=credentials, profile="default"):
            utils.remove_credentials_from_aws_cli_profile(profile="default")
            self._logger.debug("Removed [default] profile from AWS credential file")
        else:
            if "default" in credentials:
                raise CloudtokenException(
                    "Default profile in the AWS credentials file not managed by Cloudtoken, cannot continue."
                )
