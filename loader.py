import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from aiogram import Bot
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
AI_TOKEN_API_KEY = os.getenv("AI_TOKEN_API_KEY")

client = AsyncOpenAI(
    api_key = AI_TOKEN_API_KEY,
    base_url = "https://routerai.ru/api/v1"
)

bot = Bot(token=TOKEN)
