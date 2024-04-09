from enum import Enum


# Authentication with Okta uses a state machine: https://developer.okta.com/docs/reference/api/authn/#transaction-state
# The members in this enum are states we support and implement handlers for.
class TransactionState(str, Enum):
    MfaRequired = "MFA_REQUIRED"
    MfaChallenge = "MFA_CHALLENGE"
    Success = "SUCCESS"


# Result of the second factor part of the auth flow.
# See: https://developer.okta.com/docs/reference/api/authn/#factor-result
class FactorResult(str, Enum):
    Cancelled = "CANCELLED"
    # waiting for the user to verify MFA, such as accepting a push notification
    Waiting = "WAITING"
    # waiting for user to submit a challenge result, like TOTP
    Challenge = "CHALLENGE"
    # the user rejected/cancelled MFA or challenge
    Rejected = "REJECTED"
    # timed out waiting for user to verify MFA or challenge
    # this is currently 5 minutes (stateToken lifetime)
    Timeout = "TIMEOUT"