import click

from cloudtoken.core import utils
from cloudtoken.plugins.idaptive.plugin import Plugin


def handler(config: dict, plugin: Plugin):
    # Valid methods are ["push", "phone", "passcode"]
    # Push and Phone are sent back as the text strings 'push' and 'phone'.
    method = utils.get_config_value(config, ["idaptive", "mfa_method"])
    if method == "passcode":
        answer = utils.get_config_value(config, ["idaptive", "mfa_passcode"])

        # When using --export with MFA passcode the passcode prompt gets eaten
        # by the the shell `eval()`, so we print the passcode prompt to stderr
        # to work around it.
        use_stderr = utils.get_config_value(config, ["saml", "export"])
        if not answer:
            answer = click.prompt("Passcode", type=str, err=use_stderr)
    else:
        if not method:
            answer = "push"
        else:
            answer = method
    return answer
