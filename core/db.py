from sqlalchemy import Column, BigInteger, Integer, String, JSON, select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from core.data import limit
import os
from dotenv import load_dotenv
import datetime
from dateutil.relativedelta import relativedelta
from core.data import system_message
import copy

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=False
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)
    dialogue = Column(JSON, nullable=True, default=lambda: copy.deepcopy(system_message))
    ai = Column(String(50), default="anthropic/claude-3-haiku")
    privilege = Column(String(50), nullable=True, default="free")
    dictionary_channel_id = Column(JSON, nullable=True, default=list)
    tokens_days = Column(Integer, default=0)
    last_message_date = Column(String(20), nullable=True)


async def check_all(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)

        today = str(datetime.date.today())

        if user.last_message_date != today:
            user.last_message_date = today
            user.tokens_days = 0
            await session.commit()

        if user.privilege == "free" and user.tokens_days >= limit["free"]:    
            return False
        
        await session.commit()
        return True


async def user_register(user_id: int):
    """Добавление юзера в бд."""
    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            new_user = User(user_id=user_id)
            session.add(new_user)
            await session.commit()
            return True
        return False


async def is_user_registered(user_id: int):
    """Функция проверки юзера в базе."""
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            return True
        return False


async def add_data(user_id, user_dialogue=None, user_ai=None, dictionary_channel_id=None, total_tokens=None):
    """Функция для изменение значений в бд."""
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            if user_dialogue is not None:
                user.dialogue = user_dialogue
            if user_ai is not None:
                user.ai = user_ai
            if dictionary_channel_id is not None:
                user.dictionary_channel_id = dictionary_channel_id
            if total_tokens is not None:
                user.tokens_days = int(total_tokens) + user.tokens_days
            await session.commit()
            return True
        return False


async def view_user(user_id: int):
    """Достает значение User."""
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            return {
                "user_dialogue": user.dialogue,
                "user_ai": user.ai,
                "user_privilege": user.privilege,
                "user_tokens_days": user.tokens_days,
                "dictionary_channel_id": user.dictionary_channel_id
            }
        return None


async def view_data():
    """Функция считает статистику по пользователям."""
    async with async_session() as session:
        total = await session.scalar(select(func.count()).select_from(User))
        return {
            "total": total,
        }


async def init_db():
    """Асинхронная инициализация базы"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)