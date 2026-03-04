import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from db.models import Base # Импортируем Базу из твоего файла моделей

# Загружаем настройки из .env
load_dotenv()
DB_URL = os.getenv("DB_URL")

# --- ТВОЯ СЕНЬОРСКАЯ ЗАЩИТА ---
if not DB_URL:
    raise ValueError("🚨 СТОП! Переменная DB_URL пустая. Убедись, что файл .env существует и в нем есть строка DB_URL=...")
# -------------------------

# Создаем асинхронный движок
engine = create_async_engine(DB_URL, echo=False)

# Фабрика сессий
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    # КРИТИЧЕСКИЙ МОМЕНТ:
    # Мы импортируем модели ПРЯМО ТУТ. 
    # Это заставляет Python прочитать файл models.py ДО того, как сработает create_all.
    # Без этого SQLAlchemy "не видит" таблицы User и Payment и создает пустую базу.
    import db.models 
    
    async with engine.begin() as conn:
        # Создаем все таблицы, которые "увидела" Base
        await conn.run_sync(Base.metadata.create_all)