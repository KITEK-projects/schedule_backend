import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from app.handlers import router

load_dotenv()

TOKEN = os.getenv('TOKEN')

dp = Dispatcher()

async def main() -> None:
    bot = Bot(token=TOKEN)
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())