import asyncio
from app.bot.dispatcher import dp, bot
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)

async def main():
    logging.info("Бот запущен, polling начат")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")