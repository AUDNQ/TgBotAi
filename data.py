from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class AddProState(StatesGroup):
    user_id_privilege = State()
    confirm_privilege = State()

ai_privilege = {
    "free": {
        "Gemini 3.7 Flash": "google/gemini-3.7-flash",
        "Qwen3.7 Plus": "qwen/qwen3.7-plus",
        "Claude 3 Haiku": "anthropic/claude-3-haiku"
    },
    
    "pro": {
        "Grok 4.6": "x-ai/grok-4.6",
        "GPT 5.4 mini": "openai/gpt-5.4-mini",
        "Claude Haiku 4.5": "anthropic/claude-haiku-4.5"
    }
}

limit = {
    "free": 20,
    "pro": 23,
}

system_message = [{"role": "system", "content": "Привет! Ты ИИ чат-бот Nestra в Telegram. Ты умеешь отвечать на текст и анализировать картинки и файлы, которые тебе присылают. Не используй Markdown-разметку (звёздочки, решётки и т.д.) — она не отображается в Telegram."}]

HELP_TEXT = """
Привет! Мои команды:
!start — старт.
!help — помощь.
!restart — перезапуск.
!choice_ai - поменять ИИ модель.

Можно писать и с /.

👥 В группах и супергруппах: чтобы я ответил, начни сообщение с моего @username, иначе я не увижу его.

Для покупки подписки и получения доступа к ИИ, пожалуйста, свяжитесь с @NestraSupport.
Для привелегии "pro" доступны следующие модели:
- Grok 4.6, - GPT 5.4 mini, - Claude Haiku 4.5.
Это привилегия стоит 350р.
"""





