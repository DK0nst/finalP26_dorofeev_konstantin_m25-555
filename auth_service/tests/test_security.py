from app.core.security import hash_password, verify_password, create_access_token, decode_token
from jose import JWTError
import pytest


class TestPasswordHashing:
    """Тесты хеширования паролей."""

    def test_hash_is_not_plain_password(self):
        """Хеш не равен исходному паролю."""
        password = "mysecret123"
        hashed = hash_password(password)
        assert hashed != password

    def test_verify_correct_password(self):
        """Правильный пароль проходит проверку."""
        password = "mysecret123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        """Неправильный пароль не проходит проверку."""
        password = "mysecret123"
        wrong = "otherpassword"
        hashed = hash_password(password)
        assert verify_password(wrong, hashed) is False

    def test_different_passwords_produce_different_hashes(self):
        """Разные пароли дают разные хеши."""
        hash1 = hash_password("pass1")
        hash2 = hash_password("pass2")
        assert hash1 != hash2


class TestJWT:
    """Тесты создания и проверки JWT."""

    def test_create_and_decode_token(self):
        data = {"sub": 42, "role": "user"}
        token = create_access_token(data)
        payload = decode_token(token)

        assert "sub" in payload
        # sub теперь строка, как того требует JWT
        assert payload["sub"] == "42"
        assert "role" in payload
        assert payload["role"] == "user"
        assert "iat" in payload
        assert "exp" in payload
        assert payload["exp"] > payload["iat"]

    def test_decode_invalid_token_raises(self):
        """Невалидный токен вызывает JWTError."""
        invalid_token = "this.is.not.a.valid.token"
        with pytest.raises(JWTError):
            decode_token(invalid_token)


    def test_decode_expired_token_raises(self):
        """Истёкший токен вызывает JWTError."""
        from datetime import datetime, timedelta, timezone
        from jose import jwt
        from app.core.config import settings

        # Создаём токен, истёкший 1 минуту назад
        now = datetime.now(timezone.utc)
        expired = now - timedelta(minutes=1)
        payload = {"sub": "1", "role": "user", "iat": now, "exp": expired}
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

        with pytest.raises(JWTError):
            decode_token(token)