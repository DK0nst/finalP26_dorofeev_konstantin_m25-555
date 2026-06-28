import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.jwt import decode_and_validate, BotJWTError
from app.core.config import settings

def create_test_token(sub: str, role: str = "user", expired: bool = False) -> str:
    """Создаёт валидный JWT для тестов."""
    now = datetime.now(timezone.utc)
    exp = now - timedelta(minutes=1) if expired else now + timedelta(minutes=30)
    payload = {"sub": sub, "role": role, "iat": now, "exp": exp}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

class TestJWTValidation:
    """Модульные тесты проверки JWT в Bot Service."""

    def test_decode_valid_token(self):
        """Валидный токен декодируется успешно и содержит правильные поля."""
        token = create_test_token(sub="42", role="user")
        payload = decode_and_validate(token)
        assert payload["sub"] == "42"
        assert payload["role"] == "user"

    def test_decode_invalid_signature(self):
        """Токен с неверной подписью вызывает BotJWTError."""
        token = create_test_token(sub="42")
        tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
        with pytest.raises(BotJWTError):
            decode_and_validate(tampered)

    def test_decode_expired_token(self):
        """Истёкший токен вызывает BotJWTError."""
        token = create_test_token(sub="42", expired=True)
        with pytest.raises(BotJWTError):
            decode_and_validate(token)

    def test_decode_garbage_token(self):
        """Невалидная строка вместо токена вызывает BotJWTError."""
        with pytest.raises(BotJWTError):
            decode_and_validate("just_some_garbage")