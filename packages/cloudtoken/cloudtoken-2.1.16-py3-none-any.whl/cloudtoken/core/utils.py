"""These are mostly utilities used by the cli app to handle actions before the Cloudtoken library is initialised."""
from __future__ import annotations

import configparser
import copy
import getpass
import importlib
import json
import logging
import os
import pickle
import platform
import pwd
import shutil
import sys
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from lxml import html
from stat import ST_MODE
from typing import Any, List, Optional, Union

import click
import deepdiff
import keyring
import requests
import ruamel.yaml as yaml
from appdirs import user_config_dir
from cloudtoken.core import __version__
from cloudtoken.core.abstract_classes import CloudtokenPlugin
from cloudtoken.core.exceptions import (
    CloudtokenException,
    CloudtokenKeyringError,
    ConfigurationFileError,
    PluginError,
    PluginNotFoundError,
)
from cloudtoken.core.helper_classes import CloudtokenOption
from keyring.backends import macOS, Windows
from packaging import version
from pkg_resources import resource_filename


def logger(msg):
    log = logging.getLogger(__name__)
    log.debug(msg)


def load_config_from_disk(config_file: Union[str, Path, None] = None) -> dict:
    """Load YAML configuration file from disk.

    :param config_file: Path to configuration file. Loads from default location if None, defaults to None
    :type config_file: Union[str, Path, None], optional
    :raises ConfigurationFileError: If configuration file cannot be read.
    :return: Configuration dict.
    :rtype: dict
    """
    if not config_file:
        config_file = get_default_config_filename()
    try:
        logger(f"Loading config file {config_file}")
        with open(config_file, "r") as config_fh:
            config: dict = yaml.safe_load(config_fh.read())
    except yaml.constructor.DuplicateKeyError as e:
        raise ConfigurationFileError(f"Invalid duplicate key in {config_file}.") from e
    except PermissionError as e:
        raise ConfigurationFileError(f"Unable to read configuration file {config_file} due to permissions.") from e
    except Exception as e:
        raise ConfigurationFileError(f"Unable to read configuration file {config_file}.") from e

    try:
        config = convert_dashes_to_underscores_in_config_keys(config)
        # Ensures that under the 'plugins' key, any non-iterable falsy value gets converted to an empty dict as we expect
        # there to be a list of plugin names, e.g sometimes people put 'key: null' in their yaml where we would otherwise
        # expect an empty list.
        for plugin_priority, plugins in config["plugins"].items():
            if not plugins:
                logger(f"{plugin_priority} plugin list has no entries, replacing with empty list.")
                config["plugins"][plugin_priority] = []
                continue
            for index, plugin in enumerate(plugins):
                # Hack to work around the fact that Centrify is now Idaptive and people might have differing configs.
                if plugin == "centrify":
                    config["plugins"][plugin_priority][index] = "idaptive"

                if not isinstance(plugin, str):
                    raise ConfigurationFileError(
                        f"Plugin entry {plugin_priority}:{plugin} is not <string>. "
                        f"Please check your configuration file syntax ({config_file})"
                    )

        # Ensure that every plugin has a key & dict in the configuration dictionary, otherwise options fail to save their
        # configs into the configuration dict.
        for plugin_priority, plugins in config["plugins"].items():
            for plugin in plugins:
                if not config["defaults"].get(plugin, None):
                    config["defaults"][plugin] = {}
    except Exception as e:
        raise ConfigurationFileError("Malformed configuration file.")

    return config


def convert_dashes_to_underscores_in_config_keys(config: dict) -> dict:
    """Convert all the hyphens in the configuration dict keys to underscores as the command line options use hyphens
    inbetween words (e.g --system-username) but the internal variable uses underscores as hyphens are not allowed in
    variable names.

    :param config: Configuration dictionary.
    :type config: dict
    :return: Configuration dictionary.
    :rtype: dict
    """
    config_copy = {}
    for key, value in config.items():
        tmp_key = key.replace("-", "_")
        config_copy[tmp_key] = value
        if isinstance(value, dict):
            config_copy[tmp_key] = convert_dashes_to_underscores_in_config_keys(value)
    return config_copy


def get_default_config_filename() -> str:
    """Return the path to the default configuration file.

    :return: Path to Cloudtoken's config.yaml file.
    :rtype: str
    """
    return str(get_config_dir() / "config.yaml")


def get_default_cloudtoken_directory() -> Path:
    """Return the absolute path to the default Cloudtoken directory for the system.

    :raises CloudtokenException: If the default configuration directory cannot be determined.
    :return: Cloudtoken default configuration directory path.
    :rtype: str
    """
    # pylint: disable=import-outside-toplevel
    system = platform.system()
    if system in ["Linux", "Darwin"]:
        from xdg import XDG_CONFIG_HOME

        CONFIG_DIR = Path(XDG_CONFIG_HOME) / "cloudtoken"
    elif system in ["Windows"]:
        from appdirs import user_config_dir

        CONFIG_DIR = Path(user_config_dir()) / "cloudtoken"
    else:
        raise ConfigurationFileError(
            "Unable to determine path to default configuration file for your operating system. "
            "Please specify the location with --config <filename>"
        )
    logger(f"Cloudtoken configuration directory is {CONFIG_DIR}")
    return CONFIG_DIR


def parse_config_filename_from_arguments() -> str:
    """Helper to parse the configuration file specified on the command line via --config-file. We need this to take
    actions involving the config file before the we've generated all the command line options and run Click.

    :raises Exception: If the next token after '--config-file' starts with a hyphen assume it's another --option and not a filename.
    :raises ConfigurationFileError: If '--config-file' is specified with no filename.
    :return: Config filename.
    :rtype: str
    """
    i = sys.argv.index("--config-file")
    try:
        filename = sys.argv[i + 1]
        if filename.startswith("-"):  # Handle '--config-file --another-option' (no filename specified)
            raise Exception
    except Exception as e:
        raise ConfigurationFileError("Specified --config-file with no path to configuration file.") from e
    return filename


def get_config_filename() -> str:
    """Figure out what config file to use.

    1. --config-file command line option
    2. envvar CLOUDTOKEN_CONFIG_FILE
    3. Figure out default location and filename for system.

    :return: Full path to configuration file.
    :rtype: str
    """
    config_filename = None
    if "--config-file" in sys.argv:
        config_filename = parse_config_filename_from_arguments()
    elif os.environ.get("CLOUDTOKEN_CONFIG_FILE"):
        config_filename = os.environ["CLOUDTOKEN_CONFIG_FILE"]
    else:
        config_filename = get_default_config_filename()
    return config_filename


def get_config_dir() -> Path:
    config_dir = get_default_cloudtoken_directory()
    if "--config-dir" in sys.argv:
        config_dir = parse_config_directory_from_arguments()
    elif os.environ.get("CLOUDTOKEN_CONFIG_DIR"):
        config_dir = os.environ["CLOUDTOKEN_CONFIG_DIR"]
    return Path(config_dir)


def parse_config_directory_from_arguments() -> str:
    i = sys.argv.index("--config-dir")
    try:
        filename = sys.argv[i + 1]
        if filename.startswith("-"):  # Handle '--config-dir --another-option' (no filename specified)
            raise Exception
    except Exception as e:
        raise ConfigurationFileError("Specified --config-dir with no path to configuration directory.") from e
    return filename


# def get_debug_level() -> int:
#     """Return the debug level.

#     0 = debug off
#     1 = debug on (debug outputs does not contain secrets)
#     2 = debug on containing secrets.

#     :return: Integer indicating debug level.
#     :rtype: int
#     """
#     return sys.argv.count("--debug")


def set_default_values_for_options(options: list, config: dict) -> list:
    """Look in the provided config dict to determine what the default value for the Cloudtoken.Option should be.

    :param options: List of Cloudtoken.Option objects.
    :type options: list
    :param config: Config dictionary.
    :type config: dict
    :return: List of updated Cloudtoken.Option objects.
    :rtype: list
    """
    for option in options:
        default_value = get_default_config_value_for_option(option, config)
        if default_value:
            option.default = default_value
    return options


def get_default_config_value_for_option(option, config: dict) -> Union[str, bool]:
    """Retrieve the default value from the configuration dictionary for the specified command line option.

    :param option: Command line option object.
    :type option: CloudtokenOption
    :param config: Configuration dictionary.
    :type config: dict
    :return: The default value read from the configuration dictionary.
    :rtype: str|bool
    """
    if option.plugin_name:
        return config["defaults"].get(option.plugin_name, {}).get(option.human_readable_name, None)
    return config["defaults"].get(option.human_readable_name, None)


def add_param(f, param):
    """Wrapper to add the click.Option objects to the click.Command wrapped function since we don't use
    decorators to add the options.

    :param f: click.Command wrapped function.
    :type f: func
    :param param: [description]
    :type param: [type]
    """
    if isinstance(f, click.Command):
        f.params.append(param)
    else:
        if not hasattr(f, "__click_params__"):
            f.__click_params__ = []
        f.__click_params__.append(param)


def get_plugin_options(plugin_categories: dict):
    for _, plugins in plugin_categories.items():
        for plugin in plugins:
            logger(f"Loading command line options from plugin {plugin}")
            Plugin = import_plugin(plugin)
            try:
                for option in Plugin.options():
                    yield option
            except Exception as e:
                if e.args[0] == "Name defined twice":
                    msg = "Malformatted plugin parameters, expected list."
                else:
                    try:
                        msg = e.msg
                    except AttributeError:
                        msg = e
                raise PluginError(f"Unable to load options from plugin {plugin}: {msg}") from e


def import_plugin(plugin: str) -> Optional[CloudtokenPlugin]:
    try:
        logger(f"Importing plugin {plugin}")
        module = importlib.import_module(f"cloudtoken.plugins.{plugin}.plugin")
        Plugin = getattr(module, "Plugin")
    except ModuleNotFoundError as e:
        if e.msg.__contains__("No module named") and e.msg.__contains__("cloudtoken"):  # type:ignore
            raise PluginNotFoundError(f"Unable to find plugin: {plugin}") from e
        else:
            raise
    except AttributeError as e:
        raise PluginError(f"Unable to login Plugin class from plugin: {plugin}") from e
    else:
        return Plugin


def import_plugins(plugins: dict) -> List:
    """Iterate through each plugin and load it.

    :return: None.
    """
    loaded_plugins = []
    for _, plugins in plugins.items():
        for plugin in plugins:
            loaded_plugins.append(import_plugin(plugin))
    return loaded_plugins


def get_version() -> str:
    return __version__


def read_cookies():
    """Load and return the cookies from the cookiejar.

    :return: R
    :rtype: [type]
    """
    cookiejar = get_config_dir() / "cookiejar"
    logger(f"Attempting to read cookies from cookiejar {cookiejar}")
    cookies = None
    if os.path.isfile(cookiejar) and os.stat(cookiejar).st_size != 0:
        with open(cookiejar, "rb") as fh:
            cookies = pickle.load(fh)
            logger(f"Loaded cached cookies from {cookiejar}")
    return cookies


def write_cookies(cookies, username: str) -> None:
    """Write the cookie cache to disk.
    :return: True on success.
    """
    cookiejar = get_config_dir() / "cookiejar"
    logger(f"Writing cookies to {cookiejar} owned by {username}")
    with open(cookiejar, "wb") as filehandle:
        pickle.dump(cookies, filehandle, protocol=4)
        os.chmod(cookiejar, 0o600)

    # Cookiejar get written out as root when in daemon mode so this fixes that.
    chown_file(cookiejar, username)


def chown_file(filepath: Union[str, Path], username: str):
    if os.path.isfile(filepath):
        user = pwd.getpwnam(username)
        logger(f"Performing chown {user.pw_uid}:{user.pw_gid} on {filepath}")
        os.chown(filepath, user.pw_uid, user.pw_gid)


def get_config_value(config: dict[str, Any], keys: list[Any], default=None):
    """Get a configuration value. Pass multiple positional arguments for nested values:

    idaptive:
        auth_preferences:
            - Password
            - MFA (US-East-1)

    get_config_value(config, ["idaptive", "auth_preferences"])
    >>> ['Password', 'MFA']

    :return: Configuration value if it exists, None otherwise.
    :rtype: Any
    """
    assert isinstance(config, dict) and isinstance(keys, list)

    tmp_config = copy.deepcopy(config["defaults"])
    for key in keys:
        key = key.replace("-", "_")
        try:
            tmp_config = tmp_config[key]
        except KeyError:
            return default
    if tmp_config == {}:
        return default
    return tmp_config


def set_config_value(config: dict, value: str, *args: Any) -> dict:
    """Set a configuration value. You can pass in multiple positional arguments for nested values:

    idaptive:
        admin_password: 'blah'

    set_config_value(config, "mypassword", "idaptive", "admin_password")

    :raises: KeyError: If one of the specified dictionary keys cannot be found.
    :return: Configuration dictionary.
    :rtype: dict
    """
    tmp = config["defaults"]
    for arg in args:
        arg = arg.replace("-", "_")
        if isinstance(tmp.get(arg), str) or tmp.get(arg) is None:
            tmp[arg] = value
            break
        tmp = tmp[arg]
    return config


def prompt_for_password() -> str:
    return getpass.getpass(prompt="Password: ")


def get_keyring_password(username: str, keyring_name="cloudtoken") -> Optional[str]:
    return keyring.get_password(keyring_name, username)


def set_keyring_password(username, password, keyring_name="cloudtoken"):
    keyring.set_password(keyring_name, username, password)


def ensure_username_set(config: dict) -> dict:
    username = get_username(config)
    if not username:
        username = getpass.getuser()
    return set_config_value(config, username, "username")


def validate_usernames(config: dict) -> None:
    uname_regex = re.compile(r'[\w\\]+')

    username = get_username(config)
    if uname_regex.fullmatch(username) is None:
        raise CloudtokenException(f"Username is not valid: {username}")

    system_username = get_username(config)
    if uname_regex.fullmatch(system_username) is None:
        raise CloudtokenException(f"System Username is not valid: {system_username}")


def ensure_password_set(config: dict[str, Any]) -> dict[str, Any]:
    # Ensure that the various methods of specifying the auth password eventually are all stored in the 'password'
    # config key.

    # If --password specified then use that value.
    # If --password-prompt specified then use that value and save value to keyring.
    # Otherwise load saved password in keyring.
    keyring_name = get_config_value(config, ["keyring_name"])
    if not keyring_name:
        keyring_name = "cloudtoken"

    password = None
    filename = get_config_value(config, ["password_file"])
    if get_config_value(config, ["password"]):
        pass
    elif filename:
        password = load_password_from_file(filename)
    elif get_config_value(config, ["password_prompt"]):
        password = prompt_for_password()
        set_keyring_password(get_system_username(config), password, keyring_name)
    elif get_config_value(config, ["skip_keyring"]):
        password = prompt_for_password()
    else:
        try:
            password = get_keyring_password(get_system_username(config), keyring_name)
        except keyring.errors.KeyringLocked as e:
            raise CloudtokenKeyringError(f"Unable to unlock keyring to obtain password: {repr(e)}")
            # raise
        if not password:
            click.echo("No password found in keyring. Please enter your authentication password below.")
            password = prompt_for_password()
            set_keyring_password(get_system_username(config), password, keyring_name)

    if password:
        config = set_config_value(config, password, "password")
    return config


def perform_config_migrations(config: dict) -> dict:
    # TODO: Revisit this and make nicer.

    tmp_config = copy.deepcopy(config)

    # Centrify -> Idaptive migration
    try:
        if tmp_config["defaults"]["centrify"]:
            tmp_config["defaults"]["idaptive"] = tmp_config["defaults"]["centrify"]
            del tmp_config["defaults"]["centrify"]
    except KeyError:
        pass

    # Centrify -> Idaptive - SAML Response
    try:
        if tmp_config["defaults"]["saml"]["saml_response_plugin"] == "centrify":
            tmp_config["defaults"]["saml"]["saml_response_plugin"] = "idaptive"
    except KeyError:
        pass

    try:
        if tmp_config["defaults"]["mfa_method"]:
            tmp_config["defaults"]["idaptive"]["mfa_method"] = tmp_config["defaults"]["mfa_method"]
            del tmp_config["defaults"]["mfa_method"]
    except KeyError:
        pass

    if not deepdiff.DeepDiff(config, tmp_config, ignore_order=True):
        return tmp_config

    logger("Configuration file requires migration.")
    config_filename = get_config_filename()

    backup_config_file(get_config_filename())

    with open(config_filename, "w") as config_file:
        config_file.write(yaml.dump(tmp_config))

    username = get_system_username(config)
    chown_file(config_filename, username)

    return tmp_config


def get_username(config: dict) -> str:
    return get_config_value(config, ["username"]) or get_config_value(config, ["system_username"])


def get_system_username(config: dict) -> str:
    try:
        username = get_config_value(config, ["system_username"]) or get_config_value(config, ["username"])
    except KeyError:
        username = getpass.getuser()
    return username


def backup_config_file(filename: Union[str, Path]):
    backup_timestamp = datetime.strftime(datetime.now(), "%Y-%m-%d-%H-%m-%M")
    shutil.copyfile(filename, f"{filename}.{backup_timestamp}")


def acquire_lock(lock):
    logger("Acquiring thread lock.")
    lock.acquire()


def release_lock(lock):
    logger("Releasing thread lock.")
    lock.release()


def find_credentials(data: dict, exclude: Optional[list[str]] = None) -> Optional[dict]:
    """Find and return the last instance of credentials stored in 'data'."""
    if not exclude:
        exclude = []
    credentical_list = []
    try:
        for plugin, plugin_data in data.items():
            for key, value in plugin_data.items():
                if key == "credentials" and plugin not in exclude:
                    credentical_list.append(value)
    except Exception as e:
        raise PluginError("Error while trying to find valid AWS credentials in passed plugin data.") from e

    return credentical_list[-1] if credentical_list else None


def existing_valid_saml_credentials(data: dict) -> bool:
    try:
        credentials = data["saml"]["credentials"]
    except KeyError:
        return False
    expiration = datetime.strptime(credentials["Expiration"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    expiration = expiration - timedelta(minutes=5)
    return datetime.now(timezone.utc) < expiration


def load_proxy_yaml(filename: Union[str, Path]) -> dict:
    """Return the proxy metadata yaml file into as dict.

    :param filename: Proxy metadata configuration file.
    :type filename: str|Path
    :returns: Proxy metadata configuration dict.
    :rtype: dict
    """
    with open(filename, "r") as fh:
        data = yaml.load(fh.read(), Loader=yaml.Loader)
    return data


def load_password_from_file(filename: str) -> str:
    """Read and return the authentication password stored in a file.

    :param filename: Path to the file containing the authentication password.
    :type filename: str
    :returns: Password.
    :rtype: str
    """
    ensure_password_file_permissions(filename)
    with open(filename, "r") as fh:
        password = fh.readline().strip()
    return password


def ensure_password_file_permissions(filename: str) -> None:
    """Raise an exception if the file containing the authentication password has permissions that are too permissive.

    :param filename: Path to file containing authentication password.
    :type filename: str
    :returns: None
    :raises: Exception if permission on file is not 600.
    """
    if oct(os.stat(filename)[ST_MODE])[-2:] != "00":
        raise Exception(f"Permissions on {filename} are too permissive. Please change to 600.")


def make_configuration_directory() -> Path:
    config_dir = Path(get_config_dir())
    logger(f"Making configuration directory if it doesn't exist: {config_dir}")
    config_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    return config_dir


def copy_skeleton_files() -> None:
    # [(src_dir, src_filename)]
    files = [
        ("data/skeleton_files", "config.yaml"),
        ("data/skeleton_files", "proxy.yaml"),
    ]

    config_dir = Path(get_config_dir())
    for src_dir, src_filename in files:
        source = Path(resource_filename("cloudtoken", f"{src_dir}/{src_filename}"))
        dest = Path(f"{config_dir}/{src_filename}")
        logger(f"Copying {source} to {dest}")

        if dest.is_file():
            logger(f"Existing file {dest} found. Skipping.")
            continue

        shutil.copyfile(source, dest)
        dest.chmod(0o600)
        logger(f"Successfully copied {source} to {dest}")


def initialize_configuration_directory():
    config_dir = make_configuration_directory()
    return config_dir


def echo(text):
    click.echo(text)


def is_root():
    if platform.system() == "Windows":
        return False
    return os.geteuid() == 0


def init_keyring():
    """This is required to work around PyInstaller not detecting Keyring properly."""
    # https://github.com/jaraco/keyring/issues/324#issuecomment-652598542
    system = platform.system()
    if system == "Darwin":
        keyring.set_keyring(macOS.Keyring())
    elif system == "Windows":
        keyring.set_keyring(Windows.WinVaultKeyring())
    else:
        pass


def is_update_available(quiet=False):
    try:
        latest_version, forced_update = get_latest_version()
    except Exception:
        if not quiet:
            click.echo("Unable to check for updates.")
        return False, None, False
    update_available = version.parse(latest_version) > version.parse(__version__)
    return update_available, latest_version, forced_update


def get_latest_version():
    """Requests the versions JSON file and returns the version that is the last entry in the list.

    Structure of file looks like:

    {
        "versions": [
            {
                "build_time": "2020-11-09T23:50:24.017940",
                "force_update": false,
                "version": "2.0.0"
            }
        ]
    }

    :return: [description]
    :rtype: [type]
    """
    version_url = "https://cloudtoken-update.atlassian.com/versions.json"
    req = requests.get(version_url)
    req.raise_for_status()
    versions = req.json()
    latest_version = versions["versions"][-1]["version"]
    forced_update = versions["versions"][-1]["force_update"]
    return latest_version, forced_update


def export_credentials_to_stdout(credentials: dict) -> None:
    print(
        f"""
export AWS_ACCESS_KEY_ID={credentials.access_key}
export AWS_SECRET_ACCESS_KEY={credentials.secret_key}
export AWS_SECURITY_TOKEN={credentials.token}
export AWS_SESSION_TOKEN={credentials.token}
export AWS_EXPIRATION={credentials.expiration}
export AWS_ACCOUNT_ID={credentials.account_id}
        """
    )


def get_options(config: dict) -> dict:
    options = get_default_options()
    existing_human_readable_names = []
    for option in get_plugin_options(config["plugins"]):
        if option.human_readable_name in existing_human_readable_names:
            raise PluginError(f"Duplicate command line option detected: {option.human_readable_name}")
        existing_human_readable_names.append(option.human_readable_name)
        options.append(option)
    return options


def combine_config(cmd_line_options) -> dict:
    disk_config = load_config_from_disk(get_config_filename())
    options = get_options(disk_config)
    tmp_config = copy.deepcopy(disk_config)
    for option in options:
        option_value = cmd_line_options[option.human_readable_name]
        plugin_name = option.plugin_name
        human_readable_name = option.human_readable_name
        if plugin_name and option_value:
            tmp_config["defaults"][plugin_name][human_readable_name] = option_value
        elif option_value:
            tmp_config["defaults"][human_readable_name] = option_value
    return tmp_config


def get_default_options():
    options = [
        CloudtokenOption(
            ["--allowed-cidr"],
            type=str,
            default="169.254.169.254/32",
            help="Comma separated list of CIDRs that requests will be accepted from when operating in daemon mode.",
            show_default=True,
        ),
        CloudtokenOption(["--config-file"], type=str, help="Path to the configuration file."),
        CloudtokenOption(["--config-dir"], type=str, help="Path to the configuration directory."),
        CloudtokenOption(["--metadata-config"], type=str, help="Path to the metadata config file."),
        CloudtokenOption(
            ["--daemon", "-d"],
            is_flag=True,
            help="Run in daemon mode and provide metadata endpoint.",
        ),
        CloudtokenOption(
            ["--debug"],
            is_flag=True,
            help="Debug output. Does not contain secrets.",
        ),
        CloudtokenOption(
            ["--debug-with-secrets"],
            is_flag=True,
            help="Include secrets in the debug output.",
        ),
        CloudtokenOption(
            ["--keyring-name"],
            type=str,
            default="cloudtoken",
            help="The name of the entry in your keyring",
        ),
        CloudtokenOption(["--password", "-p"], type=str, help="Your authentication password."),
        CloudtokenOption(["--password-prompt"], is_flag=True, help="Prompt for your password."),
        CloudtokenOption(["--password-file"], type=str, help="File containing authentication password."),
        CloudtokenOption(["--quiet", "-q"], is_flag=True, help="Surpress non-essential output."),
        CloudtokenOption(
            ["--refresh-interval"],
            type=int,
            help="Daemon mode credential refresh in seconds.",
        ),
        CloudtokenOption(
            ["--skip-keyring"],
            is_flag=True,
            help="Do not access keyring for reading or saving credentials.",
        ),
        CloudtokenOption(
            ["--system-username"],
            type=str,
            help="System username (required for daemon mode).",
        ),
        CloudtokenOption(["--username", "-u"], type=str, help="Your authentication username."),
        CloudtokenOption(["--version", "-v"], is_flag=True, help="Display version information."),
        CloudtokenOption(["--skip-update-check"], is_flag=True, help="Skip checking if an update is available."),
    ]
    return options


def write_state(data, config):
    cloudtoken_dir = get_config_dir()
    state_filename = cloudtoken_dir / "state.json"
    credentials = find_credentials(data)
    state = {"Expiration": credentials["Expiration"], "LastRole": credentials["LastRole"]}
    state_filename.write_text(json.dumps(state))
    chown_file(state_filename, get_system_username(config))


def read_state():
    cloudtoken_dir = get_config_dir()
    state_filename = cloudtoken_dir / "cloudtoken_state.json"
    try:
        state_data = json.loads(state_filename.read_text())
    except FileNotFoundError as e:
        return None
    except json.decoder.JSONDecodeError as e:
        raise CloudtokenException(f"Unable to decode {state_filename}") from e
    except Exception as e:
        raise CloudtokenException(f"Unknown error when reading {state_filename}") from e
    return state_data


def check_for_shell_additions():
    config_dir = get_config_dir()
    shell_additions = ["bashrc_additions", "fishconfig_additions"]
    for shell_addition in shell_additions:
        filename = config_dir / shell_addition
        if filename.is_file():
            raise SystemExit(
                f"{filename} is not compatible with versions of Cloudtoken >= 1.0. Please see Cloudtoken upgrade instructions."
            )


def get_aws_credentials_path():
    """Return the path to the AWS credentials file.

    :returns: Path to the AWS credentials file.
    :rtype: Path
    """
    env_path = os.getenv("AWS_SHARED_CREDENTIALS_FILE")
    if env_path:
        return Path(env_path)

    system = platform.system()
    if system in ["Linux", "Darwin"]:
        return Path(os.path.expanduser("~/.aws/credentials"))
    elif system in ["Windows"]:
        return Path(user_config_dir()) / ".aws" / "credentials"
    else:
        raise PluginError("Cannot determine AWS configuration directory.")


def read_aws_credentials():
    """Read the contents of the AWS credentials file into a dict-like object.

    :return: Dict-like object representing the AWS credentials file.
    :rtype: configparser.ConfigParser
    """
    credentials_filename = get_aws_credentials_path()
    credentials_file_contents = configparser.ConfigParser()
    credentials_file_contents.read(credentials_filename)
    return credentials_file_contents


def remove_credentials_from_aws_cli_profile(profile="default"):
    """Remove the specified profile from the AWS credentials file.

    :param profile: Profile name, defaults to "default"
    :type profile: str, optional
    :raises SystemExit: If the specified profile is not managed by Cloudtoken.
    """
    credentials = read_aws_credentials()
    credentials_filename = get_aws_credentials_path()
    try:
        del credentials[profile]
    except KeyError:
        raise SystemExit(f"Profile '{profile}'' does not exist in AWS credentials file.")
    with open(credentials_filename, "w") as fh:
        credentials.write(fh)


def is_aws_profile_managed_by_cloudtoken(credentials, profile):
    if profile in credentials:
        if credentials[profile].getboolean("cloudtoken"):
            return True
        else:
            return False
    else:
        return False

def get_saml_response_from_html(content):
    # https://docs.python-guide.org/scenarios/scrape/
    tree = html.fromstring(content)
    try:
        saml_response = tree.xpath("//input[@name='SAMLResponse']")[0].value
    except IndexError:
        error_text = tree.xpath("//div[@class='error-text']/text()")
        if isinstance(error_text, list):
            raise PluginError(f"Received the following error: {error_text[0]}")
        raise PluginError(f"Unable to parse SAMLResponse in response. No error message available.")
    else:
        return saml_response