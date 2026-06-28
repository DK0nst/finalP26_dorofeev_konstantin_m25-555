from datetime import datetime
from pydantic import BaseModel


class UserPublic(BaseModel):
    """Публичное представление пользователя (без пароля)."""
    id: int
    email: str
    role: str
    created_at: datetime