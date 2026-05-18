class OAuthError(Exception):
    error: str = "server_error"

    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message


class InvalidRequestError(OAuthError):
    error = "invalid_request"


class InvalidClientError(OAuthError):
    error = "invalid_client"


class InvalidGrantError(OAuthError):
    error = "invalid_grant"


class UnauthorizedClientError(OAuthError):
    error = "unauthorized_client"


class UnsupportedGrantTypeError(OAuthError):
    error = "unsupported_grant_type"


class InvalidScopeError(OAuthError):
    error = "invalid_scope"


class AccessDeniedError(OAuthError):
    error = "access_denied"


class ClientLimitExceededError(OAuthError):
    error = "invalid_client"
