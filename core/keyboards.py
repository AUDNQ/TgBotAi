from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton,  KeyboardButtonRequestChat
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

channel = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(
            text="Выбрать канал",
            request_chat=KeyboardButtonRequestChat(
                request_id=1,
                chat_is_channel=True
            )
        )
    ]],
    resize_keyboard=True,
    one_time_keyboard=True
)


def build_channels_keyboard(dictionary_channel_id: list, callback_prefix: str) -> InlineKeyboardMarkup:
    """Функция для создания клавиатуры с каналами."""
    builder = InlineKeyboardBuilder()
    for item in dictionary_channel_id:
        title = list(item.keys())[0]
        channel_id = list(item.values())[0]
        builder.button(
            text=title,
            callback_data=f"{callback_prefix}:{channel_id}"
        )

    builder.adjust(2)
    return builder.as_markup()


def build_ai_keyboard(privilege, ai_privilege):
    """Функция создания клавиатуры выбора ии модели."""
    builder = InlineKeyboardBuilder()
    choice = ai_privilege.get(privilege)
    
    for model_name, model_id in choice.items():
        builder.button(
            text=model_name,
            callback_data=f"Ai_{model_id}"
        )
    
    builder.adjust(1)
    return builder.as_markup()
