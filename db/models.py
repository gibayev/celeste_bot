from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    username = Column(String)
    full_name = Column(String)
    is_premium = Column(Boolean, default=False)
    premium_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    last_active = Column(DateTime, default=datetime.now) # <--- Новое поле активности

# Новая таблица для учета доходов
class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger)
    amount_stars = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)