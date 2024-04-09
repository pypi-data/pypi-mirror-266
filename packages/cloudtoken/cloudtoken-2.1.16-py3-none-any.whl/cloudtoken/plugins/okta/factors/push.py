import time

from halo import Halo

from cloudtoken.plugins.okta.enums import FactorResult, TransactionState
from cloudtoken.plugins.okta.exceptions import UnsupportedFactorResultError


@Halo(text="Accept push notification on your device", spinner="dots")
def handle_push_factor(plugin, next_link):
    interval_seconds = plugin._get_plugin_config(["verify_interval"]) or 4
    # Times out after 5 minutes (stateToken lifetime)
    while True:
        response = plugin._session.post(next_link, json={"stateToken": plugin._state_token})
        plugin.check_response_and_raise(response)
        data = response.json()
        if data["status"] != TransactionState.MfaChallenge:
            # This will be TransactionState.Success when the user verifies the push notification
            break
        factor_result = data.get("factorResult")
        if factor_result in [FactorResult.Rejected, FactorResult.Timeout, FactorResult.Cancelled]:
            break
        if factor_result != FactorResult.Waiting:
            raise UnsupportedFactorResultError(f"unsupported factor result {factor_result}")
        next_link = data["_links"]["next"]["href"]
        time.sleep(interval_seconds)
    return response
