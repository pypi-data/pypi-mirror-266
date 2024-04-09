from queue import Queue, Empty
import threading
import webbrowser
from flask import Flask, request
from cloudtoken.core import utils
from cloudtoken.plugins.idaptive.plugin import Plugin
from werkzeug.serving import make_server

# Used to pass the signed_response from the API server thread
# to the waiting handler function.
_shared_queue = Queue()


def index():
    """Handle the duo form submission from the browser"""
    utils.logger("Received auth form from browser")
    try:
        _shared_queue.put(request.form["sig_response"])
    except KeyError:
        return {"success": False, "detail": "sig_response field not present in form"}, 400
    return {"success": True}


class ServerThread(threading.Thread):
    """Flask server listening for browser response.

    There's no way to shutdown a Flask app from outside the request
    context/outside route handlers so we make the werkzeug server.
    """

    def __init__(self, app):
        super().__init__()
        self.server = make_server("127.0.0.1", port=0, app=app)

        ctx = app.app_context()
        ctx.push()

    def run(self) -> None:
        utils.logger(f"Server listening on {self.server.host}:{self.server.port}")
        return self.server.serve_forever()

    def shutdown(self):
        utils.logger("Shutting down server")
        self.server.shutdown()


def handler(config: dict, plugin: Plugin):
    # start the out of bounds authentication flow
    # idaptive will be waiting for us to post the signed response that is retrieved from auth provider (Duo)
    utils.logger("Starting OOB authentication")
    payload = build_payload(plugin, "StartOOB")
    plugin._post(path="/Security/AdvanceAuthentication", payload=payload)

    # start a flask server for the browser to send us back the signed response
    # we are using browser based technology (WebAuthN + Duo)
    app = Flask(__name__)
    app.add_url_rule("/", "index", index, methods=("POST",))

    server_thread = ServerThread(app)
    server_thread.start()

    utils.logger("Opening browser to complete duo authentication")
    sign_request = plugin.mechanism["ThirdPartyMfaRequest"]
    # browser posts the signed response to our listening flask server
    callback_url = f"http://127.0.0.1:{server_thread.server.port}/"
    browser_url = plugin._get_plugin_config(["auth_browser_url"])
    webbrowser.open(
        # this is a testing page used during development, the query string might change when
        # the real integration is created.
        f"{browser_url}/?sig_request={sign_request}&callback_url={callback_url}",
        new=0,
        autoraise=True,
    )

    auth_timeout = plugin._get_plugin_config(["auth_timeout_secs"])
    try:
        signed_response = _shared_queue.get(timeout=auth_timeout)
    except Empty:
        utils.logger(f"Authentication timed out after {auth_timeout} seconds")
        return {"Result": {"Summary": "AuthenticationTimeout"}}
    finally:
        server_thread.server.shutdown()

    utils.logger("Received signed response, submitting to idaptive")
    plugin._post(
        path="/security/SubmitDuo",
        payload={"SessionId": plugin.session_id, "signedResponse": signed_response},
    )

    utils.logger("Retreiving authentcation cookies")
    payload = build_payload(plugin, "Poll")
    response = plugin._post(path="/Security/AdvanceAuthentication", payload=payload)

    return response


def build_payload(plugin: Plugin, action: str):
    return {
        "TenantId": plugin._tenant_id,
        "SessionId": plugin.session_id,
        "MechanismId": plugin.mechanism_id,
        "Action": action,
    }
