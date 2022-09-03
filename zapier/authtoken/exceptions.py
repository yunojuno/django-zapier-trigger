class TokenAuthError(Exception):
    """Base token authentication/authorisation error."""

    pass


class MissingTokenHeader(TokenAuthError):
    """Request is missing the X-Api-Token header."""

    pass


class UnknownToken(TokenAuthError):
    """Token does not exist."""

    pass


class TokenUserError(TokenAuthError):
    """User is inactive, or is not the same as request.user."""

    pass


class TokenScopeError(TokenAuthError):
    """Token does not have the valid scope."""

    pass


class JsonResponseError(Exception):
    """Response does not contain valid JSON."""

    pass
