"""Custom exceptions used by FocusFlow services."""


class FocusFlowError(Exception):
    """Base error type for application-specific errors."""


class ValidationError(FocusFlowError):
    """Raised when input data fails validation rules."""


class NotFoundError(FocusFlowError):
    """Raised when a requested resource cannot be found."""


class AuthorizationError(FocusFlowError):
    """Raised when data is accessed by the wrong user."""


class InvalidTransitionError(FocusFlowError):
    """Raised when a task status change is not allowed."""
