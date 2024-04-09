class UnsupportedOperationError(ValueError):
    pass


class UnsupportedTransactionStateError(UnsupportedOperationError):
    pass


class UnsupportedFactorResultError(UnsupportedOperationError):
    pass


class UnsupportedFactorTypeError(UnsupportedOperationError):
    pass


class UserCancelledAuthError(Exception):
    pass


class OktaError(Exception):
    pass