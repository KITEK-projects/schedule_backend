import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher


import my_token
from app.get_schedule.handlers import router

TOKEN = my_token.token

dp = Dispatcher()

async def main() -> None:
    bot = Bot(token=TOKEN)
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())