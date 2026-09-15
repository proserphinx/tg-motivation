import os
import asyncio
from dotenv import load_dotenv
import logging
import aiosqlite

from handlers import rt
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

logging.basicConfig(level=logging.INFO)

load_dotenv()
token = os.getenv("TOKEN")


async def main() -> None:
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(rt)
    async with aiosqlite.connect("tasks.db") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                task TEXT,
                is_active INTEGER DEFAULT 1,
                last_notification 
            )
        """)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())