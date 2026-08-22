class AppException(Exception):
    """Base exception for expected application errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class InvalidCredentialsError(AppException):
    """Raised when authentication credentials are invalid."""


class EmailAlreadyRegisteredError(AppException):
    """Raised when attempting to register an existing email."""


class ResourceNotFoundError(AppException):
    """Raised when a requested resource does not exist."""


class RuleLimitExceededError(AppException):
    """Raised when a monitoring task already has the maximum number of rules."""