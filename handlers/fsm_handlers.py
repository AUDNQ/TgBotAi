from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
from core.db import add_privilege, is_user_registered
from core.loader import bot
from core.data import AddProState
import logging

logging.basicConfig(level=logging.INFO)

router = Router()

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