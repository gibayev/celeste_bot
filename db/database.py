import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

# Загружаем настройки из .env
load_dotenv()
DB_URL = os.getenv("DB_URL")

# --- СЕНЬОРСКАЯ ЗАЩИТА ---
if not DB_URL:
    raise ValueError("🚨 СТОП! Переменная DB_URL пустая. Убедись, что файл .env существует, называется именно '.env' и в нем есть строка DB_URL=...")
# -------------------------

# Создаем асинхронный движок
engine = create_async_engine(DB_URL, echo=False)

# Фабрика сессий
async_session = async_sessionmaker(engine, expire_on_commit=False)

# Базовый класс
class Base(AsyncAttrs, DeclarativeBase):
    pass