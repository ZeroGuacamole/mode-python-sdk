class ModeAPIError(Exception):
    """Base exception class for the Mode API SDK."""

    pass


class AuthenticationError(ModeAPIError):
    """Raised when authentication fails."""

    pass


class APIError(ModeAPIError):
    """Raised when the API returns an error response."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {status_code}: {message}")
