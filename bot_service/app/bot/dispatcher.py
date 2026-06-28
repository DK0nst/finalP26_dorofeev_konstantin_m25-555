from aiogram import Dispatcher
from app.bot.handlers import router
from app.bot.bot_instance import get_bot

dp = Dispatcher()
dp.include_router(router)

# Для удобства создаём bot при загрузке приложения (не при импорте)
bot = get_bot()
