from aiogram.fsm.state import State, StatesGroup


limit_channels_free = 5
limit_tokens_free = 50000
model_ai_channel = "deepseek/deepseek-v4-pro-0813"


class AddTitleChanel(StatesGroup):
    user_id = State()
    user_id_channel = State()
    user_title_channel = State()

class AddProState(StatesGroup):
    user_id_privilege = State()
    confirm_privilege = State()

ai_privilege = {
    "free": {
        "Gemini 3.7 Flash": "google/gemini-3.7-flash",
        "Qwen3.7 Plus": "qwen/qwen3.7-plus",
        "Claude 3 Haiku": "anthropic/claude-3-haiku"
    },
    
    "admin": {
        "Gemini 3.7 Flash": "google/gemini-3.7-flash",
        "Qwen3.7 Plus": "qwen/qwen3.7-plus",
        "Claude 3 Haiku": "anthropic/claude-3-haiku",
        "Grok 4.6": "x-ai/grok-4.6",
        "GPT 5.4 mini": "openai/gpt-5.4-mini",
        "Qwen3.8 Max (0902)": "qwen/qwen3.8-max-0902",
    }
}

limit_channel = {
    "free": limit_channels_free
}


limit = {
    "free": limit_tokens_free,
}

system_message = [{"role": "system", "content": "Привет! Ты ИИ чат-бот Nestra в Telegram. Ты умеешь отвечать на текст и анализировать картинки и файлы, которые тебе присылают. Можешь использовать Telegram Markdown v1. *одинарные звездочки* для жирного текста, _одинарные подчеркивания_ для курсива, `код в апострофах`, нельзя заголовки с решетками### двойные звездочки и формулы LaTeX"}]


HELP_TEXT = """
Привет! Мои команды:
!start — старт.
!help — помощь.
!restart — перезапуск.
!choiceai - поменять ИИ модель.
!addchannel - добовляет канал в память бота.
!dellchannel - удаляет канал в памяти бота.
!viewchannelsdays - делает саммари за последний день канала.

Можно писать и с /.

👥 В группах и супергруппах: чтобы я ответил, начни сообщение с моего @username, иначе я не увижу его.
"""
