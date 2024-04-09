import click

from cloudtoken.core import utils
from cloudtoken.plugins.idaptive.plugin import Plugin


def handler(config: dict, plugin: Plugin):
    # Valid methods are ["push", "phone", "passcode"]
    # Push and Phone are sent back as the text strings 'push' and 'phone'.
    # method = utils.get_config_value(config, "idaptive", "mfa_method")
    # if method == "passcode":
    #     answer = utils.get_config_value(config, "idaptive", "mfa_passcode")
    #     if not answer:
    #         answer = click.prompt("Passcode", type=str)
    # else:
    #     answer = method
    # return answer

    return None
