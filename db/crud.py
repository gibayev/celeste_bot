from sqlalchemy import select, update
from db.database import async_session
from db.models import User, Payment
from datetime import datetime, timedelta

async def get_or_create_user(telegram_id: int, username: str | None, full_name: str | None):
    async with async_session() as session:
        query = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            user = User(telegram_id=telegram_id, username=username, full_name=full_name)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user, True
        else:
            # Юзер зашел - обновляем его время активности
            user.last_active = datetime.now()
            await session.commit()
            return user, False
        

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

async def log_payment(telegram_id: int, amount_stars: int):
    """Записывает доход в базу"""
    async with async_session() as session:
        payment = Payment(telegram_id=telegram_id, amount_stars=amount_stars)
        session.add(payment)
        await session.commit()            