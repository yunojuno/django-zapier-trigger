class AuthenticationError(Exception):
    """Error raised when Zapier auth fails."""


class JsonResponseError(Exception):
    """Response does not contain valid JSON."""
