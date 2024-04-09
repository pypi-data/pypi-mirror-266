from __future__ import annotations

import logging
import sys

import click
from cloudtoken.core.core import Cloudtoken
from cloudtoken.core.exceptions import CloudtokenException
from cloudtoken.core.networking import Networking
from cloudtoken.core.utils import (
    ensure_password_set,
    ensure_username_set,
    get_config_filename,
    get_config_value,
    get_options,
    get_version,
    import_plugins,
    init_keyring,
    initialize_configuration_directory,
    is_root,
    is_update_available,
    load_config_from_disk,
    combine_config,
    perform_config_migrations,
    validate_usernames,
)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("cloudtoken")


def cli(*args, **cmd_line_options):
    """Combines the configuration loaded from config.yaml, command line options and
    environment variables and passes on the merged configuration to Cloudtoken()
    """
    config = combine_config(cmd_line_options)
    config = ensure_username_set(config)
    config = ensure_password_set(config)
    validate_usernames(config)

    if get_config_value(config, ["debug"]):
        logger.setLevel(logging.DEBUG)

    quiet = get_config_value(config, ["quiet"])

    # Enable debug logging for all imported packages and modules
    # This generally means secrets are printed out by Requests, etc.
    if get_config_value(config, ["debug_with_secrets"]):
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

    if not get_config_value(config, ["skip_update_check"]):
        logger.debug("Checking for update.")
        try:
            update_available, version, forced_update = is_update_available(quiet=quiet)
        except Exception as e:
            if not quiet:
                click.echo(f"Update check failed: {e}. Continuing.")
        else:
            if update_available and not quiet:
                click.echo(f"An update to Cloudtoken is available ({version}).")

    if get_config_value(config, ["daemon"]) and not is_root():
        raise SystemExit("Daemon mode requires Cloudtoken to be run with root privileges.")

    if is_root() and not get_config_value(config, ["daemon"]):
        print("Warning: Running as root but not in daemon mode.")

    try:
        ct = Cloudtoken(config=config)
        ct.run()
    except KeyboardInterrupt:
        if get_config_value(config, ["daemon"]):
            Networking().unconfigure()


def run():
    """Kicks off initial running of Cloudtoken.

    Handles loading the plugin configuration from disk, obtaining the command
    line options that each plugin exports and creating click.Option objects for each
    of those that get passed to click.Command
    """
    try:
        logger.debug(f"Command line options {sys.argv}")
        if "--version" in sys.argv or "-v" in sys.argv:
            print(get_version())
            raise SystemExit

        initialize_configuration_directory()

        # Required for PyInstaller to detect Keyring properly. See `init_keyring()` docstring
        init_keyring()

        config_filename = get_config_filename()
        config = load_config_from_disk(config_filename)
        config = perform_config_migrations(config)

        # Check that all plugins can be imported successfully
        import_plugins(config["plugins"])

        cmd_line_options = get_options(config)
        cmd_line_options.sort(key=lambda x: x.human_readable_name)

        # Setup the click.Command()
        cmd = click.Command("cloudtoken", params=cmd_line_options, callback=cli)
        cmd(auto_envvar_prefix="CLOUDTOKEN")
    except KeyboardInterrupt:
        pass
    except CloudtokenException as e:
        # Click isn't initialised here so we do a simple check to see if `--debug`
        # was passed on the command line.
        if "--debug" in sys.argv:
            raise
        else:
            raise SystemExit(e)
