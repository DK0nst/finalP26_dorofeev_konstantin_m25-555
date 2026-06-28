from fastapi import HTTPException, status


class BaseHTTPException(HTTPException):
    """Базовое HTTP-исключение для Auth Service."""
    def __init__(self, detail: str = "Error"):
        super().__init__(status_code=self.status_code, detail=detail)


class UserAlreadyExistsError(BaseHTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = "User with this email already exists"

    def __init__(self, detail: str = None):
        super().__init__(detail=detail or self.detail)


class InvalidCredentialsError(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid email or password"

    def __init__(self, detail: str = None):
        super().__init__(detail=detail or self.detail)


class InvalidTokenError(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid token"

    def __init__(self, detail: str = None):
        super().__init__(detail=detail or self.detail)


class TokenExpiredError(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token has expired"

    def __init__(self, detail: str = None):
        super().__init__(detail=detail or self.detail)


class UserNotFoundError(BaseHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "User not found"

    def __init__(self, detail: str = None):
        super().__init__(detail=detail or self.detail)


class PermissionDeniedError(BaseHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Permission denied"

    def __init__(self, detail: str = None):
        super().__init__(detail=detail or self.detail)