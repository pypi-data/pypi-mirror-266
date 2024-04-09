from fastapi import status
from .base_exception import InternalBaseException


class BadGatewayException(InternalBaseException):
    code = "error_bad_gateway"
    message = "Bad gateway"

    def __init__(self, message: str = None, **kwargs):
        _message = message or self.message
        super().__init__(status.HTTP_502_BAD_GATEWAY, self.code, _message, **kwargs)


class GatewayTimeoutException(InternalBaseException):
    code = "error_gateway_timeout"
    message = "Gateway timeout"

    def __init__(self, message: str = None, **kwargs):
        _message = message or self.message
        super().__init__(status.HTTP_504_GATEWAY_TIMEOUT, self.code, _message, **kwargs)


class DatabaseInitializeFailureException(InternalBaseException):
    code = "error_database_initialize"
    message = "Database initialize failure"

    def __init__(self, message: str = None, **kwargs):
        _message = message or self.message
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, self.code, _message, **kwargs)


class DatabaseConnectFailureException(InternalBaseException):
    code = "error_database_connect"
    message = "Database connect failure"

    def __init__(self, message: str = None, **kwargs):
        _message = message or self.message
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, self.code, _message, **kwargs)


class NoChangeException(InternalBaseException):
    code = "error_no_change"
    message = "Document no change"

    def __init__(self, message: str = None, **kwargs):
        _message = message or self.message
        super().__init__(status.HTTP_200_OK, self.code, _message, **kwargs)
