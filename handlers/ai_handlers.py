import logging
from aiogram import F, Router
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from core.db import decrease_message_count, is_user_registered, check_all
from services.chat_engine import get_user_id, process_ai, process_photo, process_file
from core.loader import bot, client

logging.basicConfig(level=logging.INFO)

router = Router()


@router.message(F.text & ~F.text.startswith(("/", "!")))
async def cmd_text(message: Message):
    user_id = await get_user_id(message)
    if not user_id:
        return
    answer = await is_user_registered(user_id)
    if answer:
        check = await check_all(user_id)
        if not check:
            await message.reply("Вы исчерпали лимит.")
            return
        elif check == "privilege":
            await message.reply("У вас закончилась привилегия.")
            return
        try:
            async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
                user_message = message.text
                name = message.from_user.first_name or message.from_user.username or "Пользователь"
                assistant_reply = await process_ai(client, user_id, user_message, name)
                await message.reply(assistant_reply)
        except Exception:
            logging.exception("Ошибка при обработке сообщения")
            await decrease_message_count(user_id)
            await message.reply("Ошибка ответа ИИ :(")
    else:
        await message.reply("Зарегистрируйтесь через !start.")


@router.message(F.photo)
async def cmd_photo(message: Message):
    user_id = await get_user_id(message)
    if not user_id:
        return
    answer = await is_user_registered(user_id)
    if answer:
        check = await check_all(user_id)
        if not check:
            await message.reply("Вы исчерпали лимит.")
            return
        elif check == "privilege":
            await message.reply("У вас закончилась привилегия.")
            return
        caption = message.caption or ""
        name = message.from_user.first_name or message.from_user.username or "Пользователь"
        photo = message.photo[-1]
        file = await bot.download(photo.file_id)
        user_message = process_photo(file, caption)
        async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
            try:
                assistant_reply = await process_ai(client, user_id, user_message, name)
                await message.reply(assistant_reply)
            except Exception:
                logging.exception("Ошибка при обработке фото")
                await decrease_message_count(user_id)
                await message.reply("Ошибка ответа ИИ :(")
    else:
        await message.reply("Зарегистрируйтесь через !start.")


@router.message(F.document)
async def cmd_document(message: Message):
    user_id = await get_user_id(message)
    if not user_id:
        return
    answer = await is_user_registered(user_id)
    if answer:
        check = await check_all(user_id)
        if not check:
            await message.reply("Вы исчерпали лимит.")
            return
        elif check == "privilege":
            await message.reply("У вас закончилась привилегия.")
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
                await message.reply(
                    assistant_reply,
                    parse_mode="Markdown"
                    )
            except Exception:
                logging.exception("Ошибка при обработке документа")
                await decrease_message_count(user_id)
                await message.reply("Ошибка ответа ИИ :(")
    else:
        await message.reply("Зарегистрируйтесь через !start.")