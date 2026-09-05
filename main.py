import asyncio
from aiogram import Bot, Dispatcher
from loader import bot
from handlers import router
import os
from db import init_db

async def main():
    dp = Dispatcher()
    await init_db()
    dp.include_router(router)
    
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
