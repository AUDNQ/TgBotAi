from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message
from aiogram.enums import ChatType
from typing import Union
from core.db import is_user_registered
from core.loader import bot

class UserRegistred(BaseFilter):
    async def __call__(self, event: Union[Message, CallbackQuery]):
        if isinstance(event, Message):
            if event.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}:
                user_id = event.chat.id
            elif event.chat.type == ChatType.PRIVATE:
                user_id = event.from_user.id
        else:
            if event.message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}:
                user_id = event.message.chat.id
            elif event.message.chat.type == ChatType.PRIVATE:
                user_id = event.from_user.id
        if user_id is None:
            return False
        answer = await is_user_registered(user_id)
        if not answer:
            if isinstance(event, Message) and event.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP} and f"{me.username}" in text:
                await event.reply("Зарегистрируйтесь через /start")
            elif isinstance(event, Message) and event.chat.type == ChatType.PRIVATE:
                await event.message.reply("Зарегистрируйтесь через /start")
            return False
        return {"user_id": user_id}

class UserRegistredAi(BaseFilter):
    async def __call__(self, message: Message):
        me = await bot.get_me()
        text = message.text or message.caption or ""
        if message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP} and f"{me.username}" in text:
            user_id = message.chat.id
        elif message.chat.type == ChatType.PRIVATE:
            user_id = message.from_user.id
        if user_id is None:
            return False
        answer = await is_user_registered(user_id)
        if not answer:
            await message.reply("Зарегистрируйтесь через /start")
            return False
        return {"user_id": user_id}        
