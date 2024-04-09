from cloudtoken.core import utils
from cloudtoken.plugins.idaptive.plugin import Plugin


def handler(config: dict, plugin: Plugin):
    password = utils.get_config_value(config, ["password"])
    return password
