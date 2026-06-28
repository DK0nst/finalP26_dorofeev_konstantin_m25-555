from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"])


def hash_password(password: str) -> str:
    """Возвращает хеш пароля."""
    return pwd_context.hash(password)


def verify_password(real_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля его хешу."""
    return pwd_context.verify(real_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Создаёт JWT с полями sub, role, iat, exp.
    data должен содержать sub и role
    """

    to_encode = data.copy()

    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])

    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"iat": now, "exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALG,
    )
    
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Декодирует JWT и проверяет подпись и срок действия.
    В случае ошибки возвращает исключение JWTError.
    """

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
        )
        return payload
    
    except JWTError:
        raise