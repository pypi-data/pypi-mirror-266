"""Exceptions for the Fixpoint SDK."""


class FixpointException(Exception):
    """The base Fixpoint SDK exception."""


class InitException(FixpointException):
    """An exception raised when the Fixpoint client fails to initialize."""


class ApiException(FixpointException):
    """An exception raised when the Fixpoint API returns an error."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"API error: {status_code} {message}")
