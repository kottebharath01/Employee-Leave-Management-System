"""
Custom exceptions used across service layer. These are translated into
appropriate HTTP responses in the route layer / global exception handlers.
"""


class AppError(Exception):
    """Base class for all expected application errors."""
    status_code = 400

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class ValidationAppError(AppError):
    status_code = 422


class AuthenticationError(AppError):
    status_code = 401


class AuthorizationError(AppError):
    status_code = 403
