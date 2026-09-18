import asyncio
from aiogram import Bot, Dispatcher
from handlers import ai_handlers, callback_handlers, command_handlers, fsm_handlers
from core.loader import bot, app
import os
from core.db import init_db


async def main():
    dp = Dispatcher()
    await init_db()
    dp.include_router(command_handlers.router)
    dp.include_router(callback_handlers.router)
    dp.include_router(fsm_handlers.router)
    dp.include_router(ai_handlers.router)
    await app.start()
    print("Pyrogram запущен")
    try:
        await dp.start_polling(bot)
    finally:
        await app.stop()

    print("Бот запущен...")

if __name__ == "__main__":
    asyncio.run(main())
