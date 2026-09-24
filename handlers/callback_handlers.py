from aiogram.types import CallbackQuery
from aiogram import F, Router
from core.db import view_user,  add_data
from core.loader import app, client
import logging
from services.chat_engine import get_channel_message, process_channel_ai
from services.filters import UserRegistred

logging.basicConfig(level=logging.INFO)

router = Router()

@router.callback_query(UserRegistred(), F.data.startswith("Ai_"))
async def chek_ai(callback: CallbackQuery, user_id: int):
    user_ai = callback.data.split("_")[1]
    try:
        answer = await add_data(user_id, user_ai=user_ai)
        if answer:
            await callback.answer(f"Модель изменина")
            await callback.message.edit_text(f"ИИ модель изменена.", reply_markup=None)
        else:
            await callback.message.reply("Ошибка попробуйте еще раз.")
    except Exception:
            logging.exception("Ошибка при выборе AI")


@router.callback_query(UserRegistred(), F.data.startswith("deletechannel:"))
async def delete_channel(callback: CallbackQuery, user_id: int):
    user_data = await view_user(user_id)
    updated_channels = []
    dictionary_channel_id = user_data.get("dictionary_channel_id") or []
    channel_id_to_delete = callback.data.split(":")[1]

    for item in dictionary_channel_id:
        if str(list(item.values())[0]) != str(channel_id_to_delete):
            updated_channels.append(item)
  
    if len(updated_channels) == len(dictionary_channel_id):
        await callback.answer("Канал не найден в списке.")
        return
    await add_data(user_id, dictionary_channel_id=updated_channels)
    await callback.message.edit_text("Канал удален из списка.", reply_markup=None)


@router.callback_query(UserRegistred(), F.data.startswith("channeldays:"))
async def view_channel_days(callback: CallbackQuery, user_id: int):
    user_data = await view_user(user_id)
    dictionary_channel_id = user_data.get("dictionary_channel_id") or []
    channel_id_to_view = callback.data.split(":")[1]
    
    channel_info = next((item for item in dictionary_channel_id if str(list(item.values())[0]) == str(channel_id_to_view)), None)
    
    if not channel_info:
        await callback.message.edit_text("Канал не найден в списке.")
        return

    channel_title = list(channel_info.keys())[0]
    channel_id = int(list(channel_info.values())[0])

    text = await get_channel_message(channel_id, app)
    if text is None:
        await callback.message.edit_text(f"Сообщений небыло")
        return
    if text == "Error":
        await callback.message.edit_text(f"Ошибка при получении сообщений из канала {channel_title}.")
        return
    try:
        ai_answer = await process_channel_ai(user_id, client, text)
        await callback.message.edit_text(
            ai_answer,
            parse_mode="Markdown"
            )
    except Exception:
        await callback.message.edit_text("Ошибка ии =(")
        logging.exception("Ошибка при обработке сообщения")