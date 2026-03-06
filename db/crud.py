from sqlalchemy import select, update
from db.database import async_session
from db.models import User, Payment
from datetime import datetime, timedelta

async def get_or_create_user(telegram_id: int, username: str | None, full_name: str | None):
    """Находит или создает пользователя, обновляя время его активности"""
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
            # Обновляем время последнего входа
            user.last_active = datetime.now()
            await session.commit()
            return user, False

async def check_and_update_limit(telegram_id: int) -> bool:
    """
    Проверяет дневной лимит вопросов. 
    Возвращает True, если лимит не исчерпан, и увеличивает счетчик.
    """
    async with async_session() as session:
        query = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            return False

        now = datetime.now()
        
        # 1. Проверяем, нужно ли сбросить счетчик (если наступил новый календарный день)
        if user.last_limit_reset.date() < now.date():
            user.daily_limit_count = 0
            user.last_limit_reset = now

        # 2. Определяем порог лимита
        # Обычный юзер: 2 вопроса | Premium: 15 вопросов
        max_limit = 15 if user.is_premium else 2

        # 3. Проверяем доступность
        if user.daily_limit_count < max_limit:
            user.daily_limit_count += 1
            await session.commit()
            return True
        
        return False

async def set_user_premium(telegram_id: int, is_premium: bool = True, days: int = 30):
    """Выдает, продлевает или забирает Premium статус"""
    async with async_session() as session:
        query = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user:
            if is_premium:
                # Если подписка еще активна — прибавляем дни, если нет — считаем от сейчас
                if user.premium_until and user.premium_until > datetime.now():
                    new_until = user.premium_until + timedelta(days=days)
                else:
                    new_until = datetime.now() + timedelta(days=days)
                
                stmt = update(User).where(User.telegram_id == telegram_id).values(
                    is_premium=True, 
                    premium_until=new_until
                )
            else:
                # Отключаем премиум
                stmt = update(User).where(User.telegram_id == telegram_id).values(
                    is_premium=False, 
                    premium_until=None
                )
                
            await session.execute(stmt)
            await session.commit()

async def log_payment(telegram_id: int, amount_stars: int):
    """Фиксирует транзакцию в таблице платежей"""
    async with async_session() as session:
        payment = Payment(telegram_id=telegram_id, amount_stars=amount_stars)
        session.add(payment)
        await session.commit()

# ==========================================
# ФУНКЦИИ ДЛЯ ЭЗОТЕРИКИ И ОНБОРДИНГА
# ==========================================

async def get_user(telegram_id: int) -> User | None:
    """
    Легкая функция чтения данных пользователя (без обновления last_active).
    Идеально подходит для проверок статуса (premium, birth_date и т.д.)
    """
    async with async_session() as session:
        query = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

async def update_user_birth_date(telegram_id: int, birth_date: str):
    """
    Точечное обновление даты рождения.
    """
    async with async_session() as session:
        stmt = update(User).where(User.telegram_id == telegram_id).values(birth_date=birth_date)
        await session.execute(stmt)
        await session.commit()

async def update_user_onboarding(telegram_id: int, real_name: str, gender: str, birth_date: str):
    """
    Сохраняет данные стартовой анкеты (имя, пол, дата рождения) при первом знакомстве.
    """
    async with async_session() as session:
        stmt = update(User).where(User.telegram_id == telegram_id).values(
            real_name=real_name,
            gender=gender,
            birth_date=birth_date
        )
        await session.execute(stmt)
        await session.commit()