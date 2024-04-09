def handle_totp_factor(plugin, next_link):
    passcode = input("Please enter your TOTP: ")
    response = plugin._session.post(next_link, json={"stateToken": plugin._state_token, "passCode": passcode})
    return response
