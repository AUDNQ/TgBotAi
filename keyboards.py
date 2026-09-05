from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text="!help"),
         KeyboardButton(text="!choice_ai"),
         KeyboardButton(text="!stats")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


free_ai = InlineKeyboardMarkup(
    inline_keyboard=[
            [InlineKeyboardButton(text="Gemini 3.7 Flash", callback_data="Ai_Gemini 3.7 Flash")],
            [InlineKeyboardButton(text="Qwen3.7 Plus", callback_data="Ai_Qwen3.7 Plus")],
            [InlineKeyboardButton(text="Claude 3 Haiku", callback_data="Ai_Claude 3 Haiku")]
    ]
)


pro_ai = InlineKeyboardMarkup(
    inline_keyboard=[
                [InlineKeyboardButton(text="Grok 4.6", callback_data="Ai_Grok 4.6")],
                [InlineKeyboardButton(text="GPT 5.4 mini", callback_data="Ai_GPT 5.4 mini")],
                [InlineKeyboardButton(text="Claude Haiku 4.5", callback_data="Ai_Claude Haiku 4.5")] 
    ]
)
