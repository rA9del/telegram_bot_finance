import os
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from app.handlers import router



async def main():
    token = os.getenv('BOT_TOKEN')
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        load_dotenv()
        print("Variables loaded")
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')