import os
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from app.handlers import router
from app.db import init_db



async def main():
    token = os.getenv('BOT_TOKEN')
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(router, on_startup=on_startup)
    


async def on_startup():
    await init_db()


if __name__ == '__main__':
    try:
        load_dotenv()
        print("Variables loaded")
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')