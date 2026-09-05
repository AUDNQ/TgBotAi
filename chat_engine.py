from aiogram.enums import ChatType
from aiogram.types import Message, CallbackQuery
from db import add_data, view_user
from openai import AsyncOpenAI
import base64
import os
import asyncio
from loader import bot, client
from data import ai_privilege

_locks: dict[int, asyncio.Lock] = {}

def get_user_lock(user_id: int) -> asyncio.Lock:
    if user_id not in _locks:
        _locks[user_id] = asyncio.Lock()
    return _locks[user_id]


async def process_ai(client: AsyncOpenAI, user_id, user_message, name):
    async with get_user_lock(user_id):
        user_data = await view_user(user_id)
        user_dialogue = user_data["user_dialogue"]
        if isinstance(user_message, str):
            user_dialogue.append({"role": "user", "content": f"{name} \n {user_message}"})
        else:
            user_message["content"][0]["text"] = f"{name}\n{user_message['content'][0]['text']}"
            user_dialogue.append(user_message)

        user_ai = user_data["user_ai"]
        
        response = await client.chat.completions.create(
            model=user_ai,
            messages=user_dialogue,
        )

        assistant_reply = response.choices[0].message.content
        user_dialogue.append({"role": "assistant", "content": assistant_reply})
        while len(user_dialogue) > 20:
            user_dialogue.pop(1)
            user_dialogue.pop(1)
        await add_data(user_id, user_dialogue=user_dialogue)
        return assistant_reply


def get_simple_user_id(message=None, callback=None):
    if message is not None:
        if message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}:
            return message.chat.id
        elif message.chat.type == ChatType.PRIVATE:
            return message.from_user.id
    elif callback is not None:
        if callback.message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}:
            return callback.message.chat.id
        elif callback.message.chat.type == ChatType.PRIVATE:
            return callback.from_user.id
    return None


def find_model(ai_name: str):
    for tier_models in ai_privilege.values():
        if ai_name in tier_models:
            return tier_models[ai_name]
    return None


async def get_user_id(message):
    user_message = message.text or message.caption or ""
    me = await bot.get_me()
    if message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP} and f"@{me.username}" in user_message:
        return message.chat.id
    elif message.chat.type == ChatType.PRIVATE:
        return message.from_user.id
    return None


def process_photo(file, caption):
    image_bytes = file.read()
    base64_str = base64.b64encode(image_bytes).decode("utf-8")
    data_uri = f"data:image/jpeg;base64,{base64_str}"
    user_message = {
        "role": "user",
        "content": [
            {"type": "text", "text": caption},
            {"type": "image_url", "image_url": {"url": data_uri}}
        ]
    }
    return user_message


def process_file(file, caption):
    file_bytes =file.read()
    filename = file.name
    base64_str = base64.b64encode(file_bytes).decode("utf-8")
    mime_types = {
            '.pdf': 'application/pdf',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
        }
    ext = os.path.splitext(filename)[1].lower()
    mime_type = mime_types.get(ext, 'application/octet-stream')
    data_url = f"data:{mime_type};base64,{base64_str}"
    user_message = {
        "role": "user",
        "content": [
            {"type": "text", "text": caption},
            {"type": "file", "file": {
                    "filename": filename,
                    "file_data": data_url
                }
            }
        ]
    }
    return user_message