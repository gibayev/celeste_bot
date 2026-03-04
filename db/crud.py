from sqlalchemy import select, update
from db.database import async_session
from db.models import User
from datetime import datetime, timedelta

async def get_or_create_user(telegram_id: int, username: str | None, full_name: str | None):
    """Ищет пользователя в базе. Если его нет — создает нового."""
    async with async_session() as session:
        # Ищем пользователя по telegram_id
        query = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            # Пользователя нет, создаем
            user = User(
                telegram_id=telegram_id,
                username=username,
                full_name=full_name
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user, True # True означает, что юзер новый
        
        return user, False # False означает, что юзер уже был в базе

async def set_user_premium(telegram_id: int, is_premium: bool = True, days: int = 30):
    """Выдает или продлевает подписку пользователя"""
    async with async_session() as session:
        # Сначала находим пользователя, чтобы узнать его текущий статус
        query = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user:
            if is_premium:
                # Если подписка УЖЕ активна, прибавляем дни к остатку
                if user.premium_until and user.premium_until > datetime.now():
                    new_until = user.premium_until + timedelta(days=days)
                # Если подписки не было или она истекла, считаем от сегодня
                else:
                    new_until = datetime.now() + timedelta(days=days)
                
                stmt = update(User).where(User.telegram_id == telegram_id).values(
                    is_premium=True, 
                    premium_until=new_until
                )
            else:
                # Забираем подписку
                stmt = update(User).where(User.telegram_id == telegram_id).values(
                    is_premium=False, 
                    premium_until=None
                )
                
            await session.execute(stmt)
            await session.commit()