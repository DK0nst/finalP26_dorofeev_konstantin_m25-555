from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    """Тело запроса для регистрации."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Ответ с JWT-токеном."""
    access_token: str
    token_type: str = "bearer"