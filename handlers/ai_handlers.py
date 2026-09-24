import logging
from aiogram import F, Router
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from core.db import check_all
from services.chat_engine import process_ai, process_photo, process_file
from core.loader import bot, client
from services.filters import UserRegistredAi

logging.basicConfig(level=logging.INFO)

router = Router()


@router.message(UserRegistredAi(), F.text & ~F.text.startswith(("/", "!")))
async def cmd_text(message: Message, user_id: int):
    check = await check_all(user_id)
    if not check:
        await message.reply("Вы исчерпали лимит токенов.")
        return
    try:
        async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
            user_message = message.text
            name = message.from_user.first_name or message.from_user.username or "Пользователь"
            assistant_reply = await process_ai(client, user_id, user_message, name)
            await message.reply(assistant_reply, parse_mode="Markdown")
    except Exception:
        logging.exception("Ошибка при обработке сообщения")
        await message.reply("Ошибка ответа ИИ :(")


@router.message(UserRegistredAi(), F.photo)
async def cmd_photo(message: Message, user_id: int):
    check = await check_all(user_id)
    if not check:
        await message.reply("Вы исчерпали лимит токенов.")
        return
    caption = message.caption or ""
    name = message.from_user.first_name or message.from_user.username or "Пользователь"
    photo = message.photo[-1]
    file = await bot.download(photo.file_id)
    user_message = process_photo(file, caption)
    async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
        try:
            assistant_reply = await process_ai(client, user_id, user_message, name)
            await message.reply(assistant_reply, parse_mode="Markdown")
        except Exception:
            logging.exception("Ошибка при обработке фото")
            await message.reply("Ошибка ответа ИИ :(")


@router.message(UserRegistredAi(), F.document)
async def cmd_document(message: Message, user_id: int):
    check = await check_all(user_id)
    if not check:
        await message.reply("Вы исчерпали лимит токенов.")
        return
    caption = message.caption or ""
    file = await bot.download(message.document.file_id)
    file.name = message.document.file_name
    try:
        user_message = process_file(file, caption)
    except Exception:
        logging.exception("Ошибка при обработке файла")
        await message.reply("Ошибка обработки файла =(")
        return
    name = message.from_user.first_name or message.from_user.username or "Пользователь"
    async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
        try:
            assistant_reply = await process_ai(client, user_id, user_message, name)
            await message.reply(assistant_reply, parse_mode="Markdown")
        except Exception:
            logging.exception("Ошибка при обработке документа")
            await message.reply("Ошибка ответа ИИ :(")