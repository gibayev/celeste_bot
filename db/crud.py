from sqlalchemy import select, update
from db.database import async_session
from db.models import User

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

async def set_user_premium(telegram_id: int, is_premium: bool = True):
    """Меняет статус подписки пользователя"""
    async with async_session() as session:
        # Ищем юзера и обновляем поле is_premium
        stmt = update(User).where(User.telegram_id == telegram_id).values(is_premium=is_premium)
        await session.execute(stmt)
        await session.commit()