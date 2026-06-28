import pytest
from unittest.mock import MagicMock, AsyncMock
import fakeredis.aioredis
from app.bot.handlers import router, TOKEN_KEY_PREFIX
from app.infra.redis import get_redis
from app.core.jwt import decode_and_validate, BotJWTError


@pytest.fixture
def mock_redis():
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.fixture(autouse=True)
def patch_get_redis(monkeypatch, mock_redis):
    monkeypatch.setattr("app.bot.handlers.get_redis", lambda: mock_redis)
    monkeypatch.setattr("app.infra.redis.get_redis", lambda: mock_redis)


def create_message(text: str, user_id: int = 12345, chat_id: int = 67890):
    msg = MagicMock()
    msg.text = text
    msg.from_user.id = user_id
    msg.chat.id = chat_id
    msg.answer = AsyncMock(return_value=None)
    return msg


class TestTokenCommand:
    @pytest.mark.asyncio
    async def test_token_valid(self, mock_redis):
        from app.core.config import settings
        from jose import jwt
        from datetime import datetime, timedelta, timezone

        payload = {
            "sub": "42",
            "role": "user",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

        msg = create_message(f"/token {token}")
        handler = router.message.handlers[0]
        await handler.callback(msg)

        saved = await mock_redis.get(f"{TOKEN_KEY_PREFIX}{msg.from_user.id}")
        assert saved == token
        msg.answer.assert_called_once()
        assert "принят" in msg.answer.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_token_missing(self):
        msg = create_message("/token")
        handler = router.message.handlers[0]
        await handler.callback(msg)
        msg.answer.assert_called_once()
        assert "укажите токен" in msg.answer.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_token_invalid(self, mock_redis):
        msg = create_message("/token invalid.token.here")
        handler = router.message.handlers[0]
        await handler.callback(msg)

        saved = await mock_redis.get(f"{TOKEN_KEY_PREFIX}{msg.from_user.id}")
        assert saved is None
        msg.answer.assert_called_once()
        assert "недействителен" in msg.answer.call_args[0][0].lower()


class TestMessageHandler:
    @pytest.mark.asyncio
    async def test_no_token_stored(self, mock_redis):
        msg = create_message("Привет, бот!")
        handler = router.message.handlers[-1]
        await handler.callback(msg)
        msg.answer.assert_called_once()
        assert "для доступа" in msg.answer.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_valid_token_calls_celery(self, mock_redis, mocker):
        from app.core.config import settings
        from jose import jwt
        from datetime import datetime, timedelta, timezone

        payload = {
            "sub": "42",
            "role": "user",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        await mock_redis.set(f"{TOKEN_KEY_PREFIX}12345", token)

        mock_delay = mocker.patch("app.bot.handlers.llm_request.delay")

        msg = create_message("Как дела?", user_id=12345)
        handler = router.message.handlers[-1]
        await handler.callback(msg)

        mock_delay.assert_called_once_with(tg_chat_id=msg.chat.id, prompt="Как дела?")
        msg.answer.assert_called_once()
        assert "запрос принят" in msg.answer.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_expired_token(self, mock_redis, mocker):
        from app.core.config import settings
        from jose import jwt
        from datetime import datetime, timedelta, timezone

        payload = {
            "sub": "42",
            "role": "user",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        await mock_redis.set(f"{TOKEN_KEY_PREFIX}12345", token)

        mock_delay = mocker.patch("app.bot.handlers.llm_request.delay")

        msg = create_message("Привет", user_id=12345)
        handler = router.message.handlers[-1]
        await handler.callback(msg)

        mock_delay.assert_not_called()
        msg.answer.assert_called_once()
        assert "недействителен" in msg.answer.call_args[0][0].lower()
