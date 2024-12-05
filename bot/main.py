import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from app.handlers import router

load_dotenv()

TOKEN = os.getenv('TOKEN')

dp = Dispatcher()

async def main() -> None:
    bot = Bot(token=TOKEN)
    
    # Регистрируем команды для меню бота
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Запустить бота"),
        types.BotCommand(command="help", description="Помощь"),
        # Добавьте другие команды по необходимости
    ])
    
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())