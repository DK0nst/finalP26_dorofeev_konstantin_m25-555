from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from app.infra.redis import get_redis
from app.core.jwt import decode_and_validate, BotJWTError
from app.tasks.llm_tasks import llm_request

router = Router()

TOKEN_KEY_PREFIX = "token:"


@router.message(Command("token"))
async def cmd_token(message: Message):
    """
    Сохраняет JWT-токен, переданный пользователем.
    Использование: /token <jwt>
    """
    tg_user_id = message.from_user.id
    parts = message.text.strip().split(maxsplit=1)

    if len(parts) < 2:
        await message.answer("Укажите токен после команды: /token <jwt>")
        return

    token = parts[1]

    try:
        decode_and_validate(token)
    except BotJWTError:
        await message.answer("Токен недействителен или истёк. Получите новый в Auth Service.")
        return

    # Сохраняем токен в Redis с ключом token:<tg_user_id>
    redis = get_redis()
    await redis.set(f"{TOKEN_KEY_PREFIX}{tg_user_id}", token)
    await message.answer("Токен принят. Теперь вы можете задавать вопросы LLM.")


@router.message(F.text & ~F.text.startswith("/"))
async def handle_message(message: Message):
    """
    Обрабатывает обычные текстовые сообщения.
    Если у пользователя есть сохранённый валидный токен — отправляет задачу в Celery.
    Если нет — отказывает в доступе.
    """
    tg_user_id = message.from_user.id

    # Проверяем наличие токена в Redis
    redis = get_redis()
    token = await redis.get(f"{TOKEN_KEY_PREFIX}{tg_user_id}")

    if not token:
        await message.answer(
            "Для доступа к LLM необходим JWT-токен.\n"
            "Зарегистрируйтесь в Auth Service (Swagger) и отправьте токен командой:\n"
            "/token <ваш_токен>"
        )
        return

    # Валидируем токен
    try:
        payload = decode_and_validate(token)
    except BotJWTError:
        await message.answer("Ваш токен недействителен или истёк. Получите новый в Auth Service и передайте /token.")
        return

    # Токен валиден — отправляем задачу в Celery
    prompt = message.text
    llm_request.delay(tg_chat_id=message.chat.id, prompt=prompt)

    await message.answer("Ваш запрос принят и обрабатывается. Пожалуйста, подождите...")