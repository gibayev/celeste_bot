from sqlalchemy import select, func
from db.database import async_session
from db.models import User, Payment
from datetime import datetime, timedelta

async def get_admin_stats():
    async with async_session() as session:
        now = datetime.now()
        
        # Юзеры
        total_users = await session.scalar(select(func.count(User.id))) or 0
        premium_users = await session.scalar(select(func.count(User.id)).where(User.is_premium == True)) or 0
        
        # Активность
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        active_week = await session.scalar(select(func.count(User.id)).where(User.last_active >= week_ago)) or 0
        active_month = await session.scalar(select(func.count(User.id)).where(User.last_active >= month_ago)) or 0
        
        # Финансы
        total_stars = await session.scalar(select(func.sum(Payment.amount_stars))) or 0
        month_stars = await session.scalar(select(func.sum(Payment.amount_stars)).where(Payment.created_at >= month_ago)) or 0
        
        return {
            "total_users": total_users,
            "premium_users": premium_users,
            "active_week": active_week,
            "active_month": active_month,
            "total_stars": total_stars,
            "month_stars": month_stars
        }

async def get_all_users_ids():
    async with async_session() as session:
        result = await session.execute(select(User.telegram_id))
        return [row[0] for row in result.all()]