from __future__ import annotations

import json
import logging
import threading
import time
from ipaddress import ip_address, ip_network

from cloudtoken.core import utils
from cloudtoken.core.exceptions import CloudtokenException
from flask import Flask, Response, request


class Daemon:
    def __init__(self, config, lock, event, data):
        self._logger = logging.getLogger(__name__)
        self._config = config
        self._lock = lock
        self._thread_event = event
        self.thread_name = threading.current_thread().name
        self._data = data

        # Waiting for the plugins to finish their first run so that any auth prompts have been handled before
        # Flask takes over the screen.
        while not self._thread_event.isSet():
            self._logger.debug("Sleeping while waiting for plugins first run to complete.")
            time.sleep(1)
        self._thread_event.clear()

        try:
            self.start()
        except Exception as e:
            utils.echo(e)
            raise SystemExit

    def start(self):
        app = Flask(__name__)

        index = Index(config=self._config, data=self._data)
        app.add_url_rule("/", "index", index)
        app.add_url_rule("/<path:path>", "index_path", index)

        credentials = Credentials(config=self._config, data=self._data)
        app.add_url_rule("/<path:version>/meta-data/iam/security-credentials/", "credentials", credentials)
        app.add_url_rule(
            "/<path:version>/meta-data/iam/security-credentials/<path:role>", "credentials_role", credentials
        )

        try:
            app.run(host="169.254.169.254", port=80, use_reloader=False, debug=False)
        except PermissionError as e:
            raise CloudtokenException("Unable to bind to interface. You probably need to run using sudo.") from e
        except KeyboardInterrupt:
            raise SystemExit

    def get_credentials(self):
        with self._lock:
            credentials = utils.find_credentials(self._data)
            if credentials:
                self._logger.debug(f"Found credentials {credentials}")
        return credentials


class Route:
    def __init__(self, config, data):
        self._config = config
        self._data = data
        self._mime_type = "text/plain"
        self._allowed_cidr = utils.get_config_value(self._config, ["allowed_cidr"]).split(",")

    def __call__(self, *args, **kwargs):
        if not self.is_allowed_ip(request.remote_addr, self._allowed_cidr):
            return Response(
                response=Responses.blocked_cidr_401(request.remote_addr),
                status=401,
                headers={},
                mimetype=self._mime_type,
            )

    def is_allowed_ip(self, ip_addr: str, cidrs: list):
        """Check if the supplied IP is allowed to access the route.
        :param ip_addr: IP address the request is coming from.
        :type ip_addr: str
        :param cidrs: List of of CIDR's that daemon mode will respond queries for.
        :type cidrs: list
        :return: bool
        """
        request_ip = ip_address(ip_addr)
        networks = [ip_network(cidr) for cidr in cidrs]
        for network in networks:
            if request_ip in network:
                return True
        return False


class Index(Route):
    def __init__(self, config, data):
        super().__init__(config, data)

        proxy_data_filename = utils.get_config_value(self._config, ["metadata_config"])
        if not proxy_data_filename:
            proxy_data_filename = utils.get_config_dir() / "proxy.yaml"
        try:
            self._proxy_data = utils.load_proxy_yaml(proxy_data_filename)
        except FileNotFoundError:
            self._proxy_data = None

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)

        if not self._proxy_data:
            status_code = 404
            resp = Responses.file_not_found_404()
            return Response(response=resp, status=status_code, headers={}, mimetype="text/html")

        status_code = 200
        resp = []
        # If request has url paths e.g. /latest
        if kwargs:
            # Remove any falsey values caused by trailing slashes, etc.
            url_paths = [path for path in kwargs["path"].split("/") if path]

            # If request path is /latest then map this to whatever is specified as
            # latest in the YAML
            if url_paths[0] == "latest":
                version = self._proxy_data["latest"]
                url_paths.pop(0)
            else:
                version = url_paths.pop(0)

            branch = "/" + "/".join(url_paths).rstrip("/")

            try:
                data = self._proxy_data["paths"][version][branch]
            except KeyError:
                status_code = 404
                resp = Responses.file_not_found_404()
                return Response(response=resp, status=status_code, headers={}, mimetype="text/html")

            if isinstance(data, list):
                for key in data:
                    if branch == "/":
                        tmp_branch = branch
                    else:
                        tmp_branch = branch + "/" + key

                    if not isinstance(self._proxy_data["paths"][version][tmp_branch], str):
                        resp.append(key + "/")
                    else:
                        resp.append(key)
            elif isinstance(data, dict):
                resp = json.dumps(data)
            elif isinstance(data, str):
                resp = data
        else:
            # If request is at root '/'
            for key in self._proxy_data["paths"]["/"]:
                resp.append(key)

        if isinstance(resp, list):
            resp = "\n".join(resp)

        return Response(response=resp, status=status_code, headers={}, mimetype="text/plain")

    def _traverse_config(self, paths, data):
        for path in paths:
            data = data[path]
        return data


class Credentials(Route):
    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)

        credentials = utils.find_credentials(self._data)

        if "role" in kwargs:
            # Ensure we only return credentials for the Role that was requested.
            if kwargs["role"] == credentials["LastRole"].split("/").pop():
                creds = {
                    "Expiration": credentials["Expiration"],
                    "Token": credentials["Token"],
                    "SecretAccessKey": credentials["SecretAccessKey"],
                    "AccessKeyId": credentials["AccessKeyId"],
                    "Type": credentials["Type"],
                    "LastUpdated": credentials["LastUpdated"],
                    "Code": credentials["Code"],
                }
                response = json.dumps(creds)
                status = 200
            else:
                response = Responses.file_not_found_404()
                status = 404
        else:
            response = credentials["LastRole"].split("/").pop()
            status = 200
        return Response(response=response, status=status, headers={}, mimetype=self._mime_type)


class Responses:
    @staticmethod
    def blocked_cidr_401(ip_address):
        return f"Request denied from IP address {ip_address}"

    @staticmethod
    def file_not_found_404():
        # This is so we replicate the exact 404 page that the real metadata endpoint displays.
        return """<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
  <title>404 - Not Found</title>
</head>
<body>
  <h1>404 - Not Found</h1>
</body>
</html>"""
