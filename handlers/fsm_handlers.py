from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
from core.db import view_user, add_data
from core.data import AddTitleChanel
import logging

logging.basicConfig(level=logging.INFO)

router = Router()

@router.message(AddTitleChanel.user_title_channel)
async def update_title(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = int(data.get("user_id"))
    user_id_channel = data.get("user_id_channel")

    title_channel = message.text

    user_data = await view_user(user_id)
    dictionary_channel_id = user_data.get("dictionary_channel_id") or []
    dictionary_channel_id.append({title_channel: user_id_channel})
    await add_data(user_id, dictionary_channel_id=dictionary_channel_id)

    await message.answer(
        f"ID выбранного канала: `{user_id_channel}`, канал добавлен в список.",
        parse_mode="Markdown"
    )