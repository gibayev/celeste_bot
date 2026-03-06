from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    username = Column(String)
    full_name = Column(String) # Имя из профиля Telegram (может быть "Крошка Енот")
    
    # Статус подписки
    is_premium = Column(Boolean, default=False)
    premium_until = Column(DateTime, nullable=True)
    
    # Статистика и активность
    created_at = Column(DateTime, default=datetime.now)
    last_active = Column(DateTime, default=datetime.now)
    
    # Лимиты вопросов
    daily_limit_count = Column(Integer, default=0)
    last_limit_reset = Column(DateTime, default=datetime.now)

    # Эзотерические данные пользователя (АНКЕТА / ONBOARDING)
    real_name = Column(String, nullable=True)   # Настоящее имя (как обращаться)
    gender = Column(String, nullable=True)      # 'male' или 'female'
    birth_date = Column(String, nullable=True)  # Формат: "ДД.ММ.ГГГГ"

# Таблица для учета доходов (Звезды)
class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger)
    amount_stars = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)