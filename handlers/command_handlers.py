from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from core.db import user_register, is_user_registered, view_user, view_data, add_data
from services.chat_engine import get_simple_user_id
import core.keyboards as kb
from core.data import HELP_TEXT, INFO_PRO, AddProState, system_message, limit_channel
import logging
import copy

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


@router.message(Command("InfoPro", prefix=["/", "!"]))
async def cmd_infoPro(message: Message): 
    await message.answer(INFO_PRO)


@router.message(Command("restart", prefix=["/", "!"]))
async def cmd_restart(message: Message):
    user_id = get_simple_user_id(message=message)
    if not user_id:
        return
    answer = await is_user_registered(user_id)
    if answer:
        await add_data(user_id, user_dialogue=copy.deepcopy(system_message))
        await message.reply("История очищена.")
    else:
        await message.reply("Зарегистрируйтесь через !start.")


@router.message(Command("ChoiceAi", prefix=["/", "!"]))
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


@router.message(Command("AddChannel", prefix=["/", "!"]))
async def cmd_add_channel(message: Message):
    user_id = get_simple_user_id(message=message)
    if not user_id:
        return
    answer = await is_user_registered(user_id)
    if answer:
        data_user = await view_user(user_id)
        if data_user["user_privilege"] in {"pro", "admin"}:
            await message.reply("Чтобы добавить канал, нажмите кнопку ниже и выберите канал, который хотите добавить.", reply_markup = kb.channel)
        else:
            await message.reply("У вас нет прав для этой команды.")
    else:
        await message.reply("Зарегистрируйтесь через !start.")


@router.message(F.chat_shared)
async def chat_shared_handler(message: Message):
    user_id = get_simple_user_id(message=message)
    if not user_id:
        return
    answer = await is_user_registered(user_id)
    if answer:
        try:
            user_data = await view_user(user_id)
            dictionary_channel_id = user_data.get("dictionary_channel_id") or []
            if len(dictionary_channel_id) >= limit_channel["pro"]:
                await message.reply("Вы достигли лимита добавления каналов.")
                return
            
            channel_id = message.chat_shared.chat_id
            title = message.chat_shared.title

            dictionary_channel_id.append({title: channel_id})
            
            await add_data(user_id, dictionary_channel_id=dictionary_channel_id)
            await message.answer(
                f"ID выбранного канала: `{channel_id}`, канал добавлен в список.",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode="Markdown"
            )
        except Exception:
            logging.exception("Ошибка при получении ID канала")
            await message.reply("Произошла ошибка. Пожалуйста, попробуйте еще раз.")
            return
    elif not answer:
        await message.reply("Зарегистрируйтесь через !start.")


@router.message(Command("DellChannel", prefix=["/", "!"]))
async def cmd_dell_channel(message: Message):
    user_id = get_simple_user_id(message=message)
    if not user_id:
        return
    answer = await is_user_registered(user_id)
    if answer:
        user_data = await view_user(user_id)
        if user_data["user_privilege"] in {"pro", "admin"}:
            dictionary_channel_id = user_data.get("dictionary_channel_id") or []
            if not dictionary_channel_id:
                await message.reply("У вас нет добавленных каналов.")
                return
            
            keyboard = kb.build_channels_keyboard(dictionary_channel_id=dictionary_channel_id, callback_prefix="deletechannel")
            await message.reply("Выберите канал для удаления:", reply_markup=keyboard)
        else:
            await message.reply("У вас нет прав для этой команды.")
    else:
        await message.reply("Зарегистрируйтесь через !start.")


@router.message(Command("ViewChannelsDays", prefix=["/", "!"]))
async def cmd_view_channels(message: Message):
    user_id = get_simple_user_id(message=message)
    if not user_id:
        return
    answer = await is_user_registered(user_id)
    if answer:
        user_data = await view_user(user_id)
        if user_data["user_privilege"] in {"pro", "admin"}:
            dictionary_channel_id = user_data.get("dictionary_channel_id") or []

            if not dictionary_channel_id:
                await message.reply("У вас нет добавленных каналов.")
                return
            
            keyboard = kb.build_channels_keyboard(dictionary_channel_id=dictionary_channel_id, callback_prefix="channeldays")
            await message.answer("Выберите канал для просмотра сообщений за день в нем.", reply_markup=keyboard)

        else:
            await message.reply("У вас нет прав для этой команды.")
    else:
        await message.reply("Зарегистрируйтесь через !start.")


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
        date_privilege = user_data["date_privilege"]
        message_today = user_data["user_message_today"]
        if not date_privilege:
            date_privilege = "----"
        if privilege in {"free", "pro"}:
            await message.reply(f"Статистика:\n\nВаш ID: {user_id}.\nПривилегия: {privilege}.\nИИ модель: {user_ai}.\nСообщений сегодня: {message_today}.\nДата подписки: {date_privilege}.")
        elif privilege == "admin":
            data = await view_data()
            count_user = data["total"]
            count_user_free = data["free"]
            count_user_pro = data["pro"]
            await message.reply(f"Статистика:\n\nВаш ID: {user_id}.\nПривилегия: {privilege}.\nИИ модель: {user_ai}.\nСообщений сегодня: {message_today}.\nДата подписки: {date_privilege}.\n\nВсего пользователей: {count_user}.\nС подпиской pro: {count_user_pro}.\nС подпиской free: {count_user_free}.")
    else:
        await message.reply("Зарегистрируйтесь через !start.")


@router.message(Command("AddPro", prefix=["/", "!"]))
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
