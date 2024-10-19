from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import String, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config import DB_USER, DB_PASSWORD, DB_NAME, DB_PORT, DB_HOST

# Use your PostgreSQL database URL
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создаём бд и подключаемся к ней
engine = create_async_engine(url=DATABASE_URL)
async_session = async_sessionmaker(engine)


# Создаём родительский класс для построения моделей
class Base(AsyncAttrs, DeclarativeBase):
    pass


# Таблица с забаненными пользователями


class BannedUser(Base):
    __tablename__ = "banned_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer)


# Таблица с пользователями, которые находятся в рассылке


class UserInMailing(Base):
    __tablename__ = "users_in_mailing"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer)


# Таблица с айди чата администраторов


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer)


# Таблица для мероприятий


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60))
    date: Mapped[datetime] = mapped_column(TIMESTAMP)  # Using TIMESTAMP for events
    limit: Mapped[int] = mapped_column(Integer, default=40)
    description: Mapped[str] = mapped_column(String(150))
    is_signup_open: Mapped[int] = mapped_column(Integer)


# Таблица для записавшихся на меропрития пользователей


class EventSingUp(Base):
    __tablename__ = "event_singup"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    chat_id: Mapped[int] = mapped_column(Integer)
    event_status: Mapped[int] = mapped_column(Integer)
    level: Mapped[int] = mapped_column(Integer)
    event_id: Mapped[int] = mapped_column(ForeignKey(Event.id))
    username: Mapped[str] = mapped_column(String(100), nullable=True)


# Таблица профилей


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer, unique=True)
    nickname: Mapped[str] = mapped_column(String(100))
    is_itmo: Mapped[bool] = mapped_column(Boolean)
    level: Mapped[int] = mapped_column(Integer)


# При запуске главного файла создаём таблицы


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
