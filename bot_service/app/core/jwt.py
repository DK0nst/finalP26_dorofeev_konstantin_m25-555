from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import settings


class BotJWTError(Exception):
    """Доменное исключение для ошибок JWT в Bot Service."""
    pass


def decode_and_validate(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
        )
        return payload
    except (JWTError, ExpiredSignatureError) as e:
        raise BotJWTError(f"Invalid token: {e}")
