# bot_service/tests/test_openrouter.py

import httpx
import pytest
import respx
from app.services.openrouter_client import call_openrouter
from app.core.config import settings


class TestOpenRouterClient:
    """Интеграционные тесты клиента OpenRouter (с моком HTTP)."""

    @respx.mock
    def test_call_openrouter_success(self):
        """Успешный запрос возвращает текст ответа."""
        # Готовим фальшивый ответ OpenRouter
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Привет! Я LLM-консультант."
                    }
                }
            ]
        }
        # Мокаем POST-запрос к OpenRouter
        route = respx.post(f"{settings.OPENROUTER_BASE_URL}/chat/completions")
        route.respond(json=mock_response, status_code=200)

        result = call_openrouter("Привет, как дела?")

        assert result == "Привет! Я LLM-консультант."
        # Проверяем, что запрос действительно был сделан
        assert route.called

    @respx.mock
    def test_call_openrouter_error_status(self):
        """При не-200 статусе выбрасывается HTTPStatusError."""
        route = respx.post(f"{settings.OPENROUTER_BASE_URL}/chat/completions")
        route.respond(status_code=500, json={"error": "Internal Server Error"})

        with pytest.raises(httpx.HTTPStatusError):
            call_openrouter("Запрос вызывающий ошибку")

        assert route.called

    @respx.mock
    def test_call_openrouter_empty_choices(self):
        """При пустом списке choices выбрасывается ValueError."""
        route = respx.post(f"{settings.OPENROUTER_BASE_URL}/chat/completions")
        route.respond(json={"choices": []}, status_code=200)

        with pytest.raises(ValueError):
            call_openrouter("Ещё один запрос")

        assert route.called