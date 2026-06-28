import httpx
from app.core.config import settings


def call_openrouter(prompt: str) -> str:
    """
    Отправляет запрос к OpenRouter Chat Completions.
    Возвращает текст ответа от LLM.
    В случае ошибки сети или API выбрасывает исключение.
    """
    url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "HTTP-Referer": settings.OPENROUTER_SITE_URL,
        "X-Title": settings.OPENROUTER_APP_NAME,
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }

    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, json=payload, headers=headers)

        # Проверяем статус
        if response.status_code != 200:
            raise httpx.HTTPStatusError(
                f"OpenRouter API error: {response.status_code} {response.text}",
                request=response.request,
                response=response,
            )

        # Извлекаем ответ
        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            raise ValueError("OpenRouter returned empty choices")

        content = choices[0].get("message", {}).get("content", "")
        return content