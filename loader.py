import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from aiogram import Bot
from pyrogram import Client, enums
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
AI_TOKEN_API_KEY = os.getenv("AI_TOKEN_API_KEY")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

app = Client(
        "my_account",
        api_id=API_ID,
        api_hash=API_HASH,
        device_model="Honor X8D",
        system_version="14 (34)",
        app_version="11.13.2 (60601)",
        lang_pack="android",
        lang_code="ru",
        client_platform=enums.ClientPlatform.ANDROID
    )

client = AsyncOpenAI(
    api_key = AI_TOKEN_API_KEY,
    base_url = "https://routerai.ru/api/v1"
)

bot = Bot(token=TOKEN)
