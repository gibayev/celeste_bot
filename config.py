# config.py
ADMIN_IDS = [382003586] # Замени на свой реальный Telegram ID

def is_admin(telegram_id: int) -> bool:
    """Проверяет, является ли пользователь админом"""
    return telegram_id in ADMIN_IDS