from aiogram.fsm.state import State, StatesGroup

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
        "Qwen3.8 Max (0902)": "qwen/qwen3.8-max-0902"
    }
}

limit_channel = {
    "pro": 10
}


limit = {
    "free": 20,
    "pro": 23,
}

system_message = [{"role": "system", "content": "Привет! Ты ИИ чат-бот Nestra в Telegram. Ты умеешь отвечать на текст и анализировать картинки и файлы, которые тебе присылают. Не используй Markdown-разметку (звёздочки, решётки и т.д.) — она не отображается в Telegram."}]

INFO_PRO = """
Про тариф pro:
Доступные ИИ модели:
-Grok 4.6
-GPT 5.4 mini
-Qwen3.8 Max (0902)
Про функцию саммери:
Это функция на данный момент в DEMO тестировании, еслм вам хочется добавить закрытый канал (вход в который по заявке), попросите помоши с этим у @NestraSupport после того как вам ответят что все готово добавте канал в паметь бота
Если у вас появился вопрос или идея которую можно добавить пишите в @NestraSupport там же можно купить платную подписку.
Подписка на месяц стоит 350р.
"""

HELP_TEXT = """
Привет! Мои команды:
Без тарифа "pro":
!start — старт.
!help — помощь.
!restart — перезапуск.
!ChoiceAi - поменять ИИ модель.
С тарифом добовляется:
!AddChannel - добвовляет канал в паметь бота.
!DellChannel - удаляет канал в памети бота.
!ViewChannelsDays - делает саммари за последний день канала.

Можно писать и с /.

👥 В группах и супергруппах: чтобы я ответил, начни сообщение с моего @username, иначе я не увижу его.

Подробнее про платный тариф вы можете узнать командой /InfoPro 
"""





