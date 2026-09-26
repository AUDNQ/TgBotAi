from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from core.db import user_register, view_user, view_data, add_data
import core.keyboards as kb
from services.filters import UserRegistred
from services.chat_engine import get_simple_user_id, get_user_channels
from core.data import HELP_TEXT, AddTitleChanel, system_message, limit_channel, ai_privilege, limit_tokens_free
import logging
import copy

logging.basicConfig(level=logging.INFO)

router = Router()

@router.message(Command("start", prefix=["/", "!"]))
async def cmd_start(message: Message):
    user_id = get_simple_user_id(message=message)

    answer = await user_register(user_id)
    if answer:
        await message.reply("Вы зарегистрированны, напишите команду !help.")
    else:
        await message.reply("Вы уже были зарегистрированны, напишите команду /help.")


@router.message(Command("help", prefix=["/", "!"]))
async def cmd_help(message: Message):
    await message.reply(HELP_TEXT)


@router.message(UserRegistred(), Command("restart", prefix=["/", "!"]))
async def cmd_restart(message: Message, user_id: int):
    await add_data(user_id, user_dialogue=copy.deepcopy(system_message))
    await message.reply("История очищена.")


@router.message(UserRegistred(), Command("choiceai", prefix=["/", "!"]))
async def cmd_choice_ai(message: Message, user_id: int):
    user_data = await view_user(user_id)
    privilege = user_data["user_privilege"]
    keyboard = kb.build_ai_keyboard(privilege=privilege, ai_privilege=ai_privilege)
    await message.reply("Выберете ИИ модель", reply_markup = keyboard)


@router.message(UserRegistred(), Command("addchannel", prefix=["/", "!"]))
async def cmd_add_channel(message: Message, user_id: int):
    if message.chat.type != "private":
        await message.reply("⚠️ Эта команда работает только в личных сообщениях с ботом!")
        return
    data_user = await view_user(user_id)
    if data_user["user_privilege"] in {"free", "admin"}:
        await message.reply("Чтобы добавить канал, нажмите кнопку ниже и выберите канал, который хотите добавить.", reply_markup = kb.channel)


@router.message(UserRegistred(), F.chat_shared)
async def chat_shared_handler(message: Message, state: FSMContext, user_id: int):
    try:
        user_data = await view_user(user_id)
        dictionary_channel_id = user_data.get("dictionary_channel_id") or []
        if len(dictionary_channel_id) >= limit_channel["free"]:
            await message.reply("Вы достигли лимита добавления каналов.")
            return
        channel_id = message.chat_shared.chat_id
        if not channel_id:
            await message.reply("Ошибка получения ID канала попробуйте еще раз.")
            return
        await state.update_data(user_id=user_id)
        await state.update_data(user_id_channel=channel_id)
        await state.set_state(AddTitleChanel.user_title_channel)
        await message.reply("Напишите название канала(не обезательно точь в точь как он называется)", reply_markup=ReplyKeyboardRemove())
    except Exception:
        logging.exception("Ошибка")
        await message.reply("Произошла ошибка. Пожалуйста, попробуйте еще раз.")
        return


@router.message(UserRegistred(), Command("delchannel", prefix=["/", "!"]))
async def cmd_del_channel(message: Message, user_id: int):
    user_data = await view_user(user_id)
    dictionary_channel_id = get_user_channels(user_data)
    if dictionary_channel_id is None:
        await message.reply("У вас нет добавленных каналов.")
    else:
        keyboard = kb.build_channels_keyboard(dictionary_channel_id=dictionary_channel_id, callback_prefix="deletechannel")
        await message.reply("Выберите канал для удаления:", reply_markup=keyboard)


@router.message(UserRegistred(), Command("viewchannelsdays", prefix=["/", "!"]))
async def cmd_view_channels(message: Message, user_id: int):
    user_data = await view_user(user_id)
    dictionary_channel_id = get_user_channels(user_data)
    if dictionary_channel_id is None:
        await message.reply("У вас нет добавленных каналов.")
    else:
        keyboard = kb.build_channels_keyboard(dictionary_channel_id=dictionary_channel_id, callback_prefix="channeldays")
        await message.answer("Выберите канал для просмотра сообщений за день в нем.", reply_markup=keyboard)


@router.message(UserRegistred(), Command("stats", prefix=["/", "!"]))
async def cmd_stats(message: Message, user_id: int):
    user_data = await view_user(user_id)
    privilege = user_data["user_privilege"]
    user_ai = user_data["user_ai"]
    user_tokens_days= user_data["user_tokens_days"]
    if privilege in {"free"}:
        await message.reply(f"Статистика:\n\nВаш ID: {user_id}.\nИИ модель: {user_ai}.\nТокенов: {user_tokens_days}/{limit_tokens_free}.")
    elif privilege == "admin":
        admin_data = await view_data(user_id)
        count_user = admin_data["total"]
        await message.reply(f"Статистика:\n\nВаш ID: {user_id}.\nИИ модель: {user_ai}.\nСообщений сегодня: {user_tokens_days}.\n\nВсего пользователей: {count_user}.")
