from sqlalchemy import Column, BigInteger, Integer, String, Boolean, JSON, select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from data import limit
import os
from dotenv import load_dotenv
import datetime
from dateutil.relativedelta import relativedelta
from data import system_message


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
    dialogue = Column(JSON, nullable=True, default=lambda: system_message)
    ai = Column(String(50), default="anthropic/claude-3-haiku")
    privilege = Column(String(50), nullable=True, default="free")
    message_today = Column(Integer, default=0)
    last_message_date = Column(String(20), nullable=True)
    date_privilege = Column(String(20), default=None)


async def check_all(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)

        today = str(datetime.date.today())

        if user.date_privilege is not None:
            str_date_privilege = user.date_privilege
            object_date_privilege = datetime.datetime.strptime(str_date_privilege, "%Y-%m-%d").date()
            end_date_privilege = object_date_privilege + relativedelta(months=1)
            today_date = datetime.date.today()
            if today_date >= end_date_privilege:
                await add_privilege(user_id, "free")
                await add_data(user_id, user_ai="anthropic/claude-3-haiku")
                await session.commit()
                return "privilege"

        
        if user.last_message_date != today:
            user.last_message_date = today
            user.message_today = 0
            user.message_today += 1
            await session.commit()

        if user.privilege == "pro" and user.message_today >= limit["pro"]:
            return False
        if user.privilege == "free" and user.message_today >= limit["free"]:    
            return False

        user.message_today += 1
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


async def decrease_message_count(user_id: int):
    """"Функция удаляет лишний запрос в случае ошибки."""
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.message_today -= 1
            await session.commit()
        return False


async def add_data(user_id, user_dialogue=None, user_ai=None):
    """Функция для изменение значений в бд."""
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            if user_dialogue is not None:
                user.dialogue = user_dialogue
            if user_ai is not None:
                user.ai = user_ai
            await session.commit()
            return True
        return False


async def add_privilege(user_id, privilege):
    """Функция меняет значение привилегии и ставит дату изменения."""
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.privilege = privilege
            user.date_privilege = str(datetime.date.today()) if privilege == "pro" else None
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
                "user_message_today": user.message_today
            }
        return None


async def view_data():
    """Функция считает статистику по пользователям."""
    async with async_session() as session:
        total = await session.scalar(select(func.count()).select_from(User))
        free = await session.scalar(select(func.count()).select_from(User).where(User.privilege == "free"))
        pro = await session.scalar(select(func.count()).select_from(User).where(User.privilege == "pro"))
        return {
            "total": total,
            "free": free,
            "pro": pro
        }


async def init_db():
    """Асинхронная инициализация базы"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
