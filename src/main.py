import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from src.database.connection import DatabaseManager
from src.handlers import commands, messages
from src.middlewares.access_control import AccessControlMiddleware

load_dotenv()

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    dp = Dispatcher()
    db_manager = DatabaseManager()

    await db_manager.initialize()
    dp["db_manager"] = db_manager

    dp.message.middleware(AccessControlMiddleware(db_manager))

    dp.include_router(commands.router)
    dp.include_router(messages.router)

    try:
        await dp.start_polling(bot, drop_pending_updates=True)
    finally:
        await db_manager.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
