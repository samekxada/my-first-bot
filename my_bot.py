import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# ... (Здесь оставь все свои TEXTS, PRODUCTS и хендлеры без изменений) ...

async def main():
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN не найден в переменных окружения!")

    bot = Bot(token=token)
    dp = Dispatcher()

    # ... (Здесь оставь все свои @dp.message хендлеры) ...

    print("🚀 Бот запущен в режиме Polling...")
    await bot.delete_webhook(drop_pending_updates=True) # На всякий случай чистим старый вебхук
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
