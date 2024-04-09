from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Union

from cloudtoken.core import utils
from cloudtoken.core.exceptions import PluginError
from cloudtoken.core.helper_classes import CloudtokenOption


class CloudtokenPlugin(ABC):
    """The abstract class that all Cloudtoken plugins inherit from.

    Provides structure and helper methods.
    """

    name = None

    def __init__(self, config: dict[str, Any]):
        self._config = config
        self._logger = logging.getLogger(f"cloudtoken.plugins.{self.name}")

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    @abstractmethod
    def options(self) -> list:
        """Declares and returns the command line options that the plugin will expose."""
        return []

    @abstractmethod
    def execute(self, data: dict) -> dict:
        """Main method to is called to execute the plugin."""
        data = {}
        return data

    @classmethod
    def add_option(cls, *args: list, **kwargs: dict):
        """Helper class method to add a command line option for the plugin.
        This class is essentially a wrapper around click.Option so take a look at the
        Click API docs to see what's possible.

        Example:
            add_option(["-f", "--filter"], help="Filter the roles.")

        :return: Returns a CloudtokenOption object which is a wrapper around click.Option
        :rtype: CloudtokenOption
        """
        plugin_name = getattr(cls, "name", None)
        if not plugin_name:
            raise PluginError(f"{cls.__module__} does not provide the required cls.name attribute.")
        kwargs["plugin_name"] = plugin_name

        # If you specify a default then it's impossible to tell if the click.Option()
        # value shoudl take precedence over the value pulled in from the config.yaml
        if "default" in kwargs:
            raise PluginError("Do not include default values in command options, instead check for None value.")

        return CloudtokenOption(*args, **kwargs)

    def _get_plugin_config(self, keys: list, default: Union[str, int, None] = None) -> Union[str, int, None]:
        """Return the value associated with a configuration key for the current plugin.

        :param keys: A list of keys dictating a potentially nested dictionary, e.g. `["idaptive", "appkey"]
        :type keys: list
        :param default: The default value to return if the configuration key is not found , defaults to None
        :type default: Union[str, int, None], optional
        :return: The value of the configuration key.
        :rtype: str|int|None
        """
        keys.insert(0, self.name)
        value = utils.get_config_value(self._config, keys, default)
        return value

    def _get_config(self, keys: list[Any], default: Union[str, int, None] = None) -> Union[str, int, None]:
        """Return the value associated with a configuration key.

        :param keys: A list of keys dictating a potentially nested dictionary, e.g. `["defaults", "idaptive", "appkey"]
        :type keys: list
        :param default: The default value to return if the configuration key is not found , defaults to None
        :type default: Union[str, int, None], optional
        :return: The value of the configuration key.
        :rtype: str|int|None
        """
        value = utils.get_config_value(self._config, keys, default)
        return value

    def _set_config(self, plugin: str, value: Union[str, int], *args: Any) -> None:
        """Set the value for a configuration key.

        :param plugin: The plugin that this configuration key belongs to.
        :type plugin: str
        :param value: The value to set.
        :type value: Union[str, int]
        :return: None
        :rtype: None
        """
        return utils.set_config_value(self._config, value, plugin, *args)
