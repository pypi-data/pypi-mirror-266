from __future__ import annotations

import platform

import delegator
import ifaddr
from cloudtoken.core.exceptions import CloudtokenException


class Networking:
    def __init__(self):
        self.adapters = ifaddr.get_adapters()
        self.adapter = self.get_adapter()

    def does_alias_exist(self):
        addresses = [ip.ip for adapter in self.adapters for ip in adapter.ips if ip.ip == "169.254.169.254"]
        if addresses:
            return True
        return False

    def get_adapter(self):
        adapters = [adapter.name for adapter in self.adapters]
        system = platform.system()

        if system == "Darwin":
            if "lo0" in adapters:
                return "lo0"
            return None
        elif system == "Linux":
            if "lo" in adapters:
                return "lo"
            return None
        else:
            raise ValueError

    def remove_alias(self):
        if self.adapter == "lo0":
            cmd = f"ifconfig {self.adapter} -alias 169.254.169.254"
        else:
            cmd = f"ifconfig {self.adapter}:0 169.254.169.254 down"
        c = delegator.run(cmd)
        if c.err:
            raise Exception(c.err)

    def add_alias(self):
        if self.adapter == "lo0":
            cmd = f"ifconfig {self.adapter} alias 169.254.169.254 255.255.255.255"
        else:
            cmd = f"ifconfig {self.adapter}:0 169.254.169.254 netmask 255.255.255.255 up"
        c = delegator.run(cmd)
        if c.err:
            raise CloudtokenException(f"Unable to add 169.254.169.254 alias to {self.adapter} - {c.err}")

    def configure(self):
        if not self.does_alias_exist():
            self.add_alias()

    def unconfigure(self):
        if self.does_alias_exist():
            self.remove_alias()
