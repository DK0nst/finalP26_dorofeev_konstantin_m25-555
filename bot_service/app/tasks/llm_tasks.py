import httpx
from celery import shared_task
from app.services.openrouter_client import call_openrouter
from app.core.config import settings

TELEGRAM_API_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"

@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def llm_request(self, tg_chat_id: int, prompt: str) -> str:
    try:
        # Получаем ответ от OpenRouter
        response_text = call_openrouter(prompt)

        # Отправляем ответ пользователю через синхронный HTTP-запрос
        url = f"{TELEGRAM_API_URL}/sendMessage"
        payload = {
            "chat_id": tg_chat_id,
            "text": response_text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()

        return response_text
    except Exception as exc:
        raise self.retry(exc=exc)