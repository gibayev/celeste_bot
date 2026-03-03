from sqlalchemy import BigInteger, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from db.database import Base

class User(Base):
    __tablename__ = "users"

    # id в нашей базе
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # id пользователя в Telegram (очень длинное число, поэтому BigInteger)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # Флаг подписки (по умолчанию False - бесплатный)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    # До какого числа действует подписка
    premium_until: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    
    # Когда человек впервые запустил бота
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())