from aiogram.types import Message, CallbackQuery
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.utils.chat_action import ChatActionSender
from aiogram.filters import Command
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from db import add_privilege, decrease_message_count, user_register, is_user_registered, view_user, view_data, add_data, check_all
from chat_engine import get_user_id, get_simple_user_id, process_ai, process_photo, process_file, find_model
import os
import keyboards as kb
from loader import bot, client
from data import HELP_TEXT, AddProState, system_message
import logging

logging.basicConfig(level=logging.INFO)

router = Router()

@router.message(Command("start", prefix=["/", "!"]))
async def cmd_start(message: Message):
    user_id = get_simple_user_id(message=message)
    if not user_id:
        return
    answer = await user_register(user_id)
    if answer:
        await message.reply("Вы зарегистрированны напишите команду !help.")
    else:
        await message.reply("Вы уже зарегистрированны.")


@router.message(Command("help", prefix=["/", "!"]))
async def cmd_help(message: Message):
    await message.reply(HELP_TEXT)


@router.message(Command("restart", prefix=["/", "!"]))
async def cmd_restart(message: Message):
    user_id = get_simple_user_id(message=message)
    if not user_id:
        return
    answer = await is_user_registered(user_id)
    if answer:
        await add_data(user_id, user_dialogue=system_message)
        await message.reply("История очищена.")
    else:
        await message.reply("Зарегистрируйтесь через !start.")


@router.message(Command("choice_ai", prefix=["/", "!"]))
async def cmd_choice_ai(message: Message):
    user_id = get_simple_user_id(message=message)
    if not user_id:
        return
    answer = await is_user_registered(user_id)
    if answer:
        user_data = await view_user(user_id)
        privilege = user_data["user_privilege"]
        if privilege == "free":
            await message.reply("Выберите ИИ модель.", reply_markup = kb.free_ai)
        elif privilege in {"pro", "admin"}:
            await message.reply("Выберите ИИ модель.", reply_markup = kb.pro_ai)
    else:
        await message.reply("Зарегистрируйтесь через !start.")


@router.callback_query(F.data.startswith("Ai_"))
async def chek_ai(callback: CallbackQuery):
    ai_name = callback.data.split("_")[1]
    user_ai = find_model(ai_name)
    try:
        user_id = get_simple_user_id(callback=callback)
        answer = await add_data(user_id, user_ai=user_ai)
        if answer:
            await callback.answer(f"Вы выбрали {ai_name}!!!")
            await callback.message.reply(f"Вы выбрали {ai_name}. Изменение сохранены.")
        else:
            await callback.message.reply("Ошибка попробуйте еще раз.")
    except Exception:
            logging.exception("Ошибка при выборе AI")

    
@router.message(Command("stats", prefix=["/", "!"]))
async def cmd_stats(message: Message):
    user_id = get_simple_user_id(message=message)
    if not user_id:
        return
    answer = await is_user_registered(user_id)
    if answer:
        user_data = await view_user(user_id)
        privilege = user_data["user_privilege"]
        user_ai = user_data["user_ai"]
        if privilege in {"free", "pro"}:
            await message.reply(f"Статистика:\n\nВаш ID: {user_id}.\nПривилегия: {privilege}.\nИИ модель: {user_ai}.\nСообщений сегодня: {user_data['user_message_today']}.")
        elif privilege == "admin":
            data = await view_data()
            count_user = data["total"]
            count_user_free = data["free"]
            count_user_pro = data["pro"]
            await message.reply(f"Статистика:\n\nВаш ID: {user_id}.\nПривилегия: {privilege}.\nИИ модель: {user_ai}.\nВсего пользователей: {count_user}.\nС подпиской pro: {count_user_pro}.\nС подпиской free: {count_user_free}.")
    else:
        await message.reply("Зарегистрируйтесь через !start.")


@router.message(Command("add_pro", prefix=["/", "!"]))
async def cmd_add_pro(message: Message, state: FSMContext):
    user_id = get_simple_user_id(message=message)
    if not user_id:
        return
    answer = await is_user_registered(user_id)
    if answer:
        user_data = await view_user(user_id)
        privilege = user_data["user_privilege"]
        if privilege == "admin":
            await state.set_state(AddProState.user_id_privilege)
            await message.reply("Введите ID пользователя, которому хотите дать подписку pro, (!id и сам ID).")
        else:
            await message.reply("У вас нет прав для этой команды.")


@router.message(AddProState.user_id_privilege)
async def process_add_pro(message: Message, state: FSMContext):
    try:
        text = (message.text)
        text = text.replace("!id", "").strip()
        user_id_privilege = int(text)
    except Exception:
        logging.exception("Ошибка при вводе ID пользователя")
        await message.reply("Ошибка! Попробуйте еще раз. Введите корректный ID пользователя.")
        await state.clear()
        return
    answer = await is_user_registered(user_id_privilege)
    if answer:
        try:
            chat = await bot.get_chat(user_id_privilege)
            username = chat.username
        except Exception:
            logging.exception("Ошибка при получении юзернейма пользователя")
            await message.reply(f"Не удалось получить юзернейм пользователя с ID {user_id_privilege}. Пожалуйста, убедитесь, что ID правильный.")
            await state.clear()
            return 
        await message.reply(f"Вы хотите дать подписку pro пользователю с ID {user_id_privilege} и юзернеймом @{username}. Подтвердите '!да' или '!нет'.")
        await state.update_data(user_id_privilege=user_id_privilege)
        await state.set_state(AddProState.confirm_privilege)
    else:
        await message.reply(f"Пользователь с ID {user_id_privilege} не зарегистрирован. Попросите его зарегистрироваться через !start.")
        await state.clear()
        return


@router.message(AddProState.confirm_privilege)
async def confirm_add_pro(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id_privilege = data.get("user_id_privilege")
    if message.text.lower() == "!да":
        answer = await add_privilege(user_id_privilege, "pro")
        if answer:
            await message.reply(f"Пользователю с ID {user_id_privilege} успешно предоставлена подписка pro.")
            await state.clear()
        else:
            await message.reply(f"Не удалось предоставить подписку pro пользователю с ID {user_id_privilege}.")
            await state.clear()
    elif message.text.lower() == "!нет":
        await message.reply(f"Вы отказались предоставить подписку pro пользователю с ID {user_id_privilege}.")
        await state.clear()


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
        elif check == "privilege":
            await message.reply("У вас закончилась привилегия.")
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
        elif check == "privilege":
            await message.reply("У вас закончилась привилегия.")
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
        elif check == "privilege":
            await message.reply("У вас закончилась привилегия.")
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
                await message.reply(assistant_reply)
            except Exception:
                logging.exception("Ошибка при обработке документа")
                await decrease_message_count(user_id)
                await message.reply("Ошибка ответа ИИ :(")
    else:
        await message.reply("Зарегистрируйтесь через !start.")
