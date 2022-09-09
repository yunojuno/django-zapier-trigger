from zapier.exceptions import AuthenticationError


class TokenAuthError(AuthenticationError):
    """Base token authentication/authorisation error."""


class MissingTokenHeader(TokenAuthError):
    """Request is missing the Authorization header."""


class TokenInactiveError(AuthenticationError):
    """AuthToken is inactive."""


class UnknownToken(TokenAuthError):
    """Token does not exist."""


class TokenUserError(TokenAuthError):
    """User is inactive, or is not the same as request.user."""
