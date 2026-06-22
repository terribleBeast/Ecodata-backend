class AppError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(AppError):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(f"{resource} with id '{resource_id}' not found", 404)


class ValidationError(AppError):
    def __init__(self, message: str):
        super().__init__(message, 422)
