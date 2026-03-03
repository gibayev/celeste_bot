from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.keyboards.reply import get_main_menu

# Импортируем нашу функцию для работы с БД
from db.crud import get_or_create_user

# Создаем роутер (это как отдельный маршрутизатор для этой части логики)
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    # Получаем данные о пользователе из Telegram
    tg_user = message.from_user
    
    # Идем в базу данных: регистрируем или просто получаем инфу
    db_user, is_new = await get_or_create_user(
        telegram_id=tg_user.id,
        username=tg_user.username,
        full_name=tg_user.full_name
    )
    
    # Формируем ответ в зависимости от того, новый это юзер или нет
    if is_new:
        text = (
            f"Привет, {tg_user.first_name}! 🌌\n\n"
            f"Я — Селеста, твой личный цифровой оракул. Я читаю карты Таро, "
            f"расшифровываю Матрицу Судьбы и знаю, о чем шепчутся звезды.\n\n"
            f"Я добавила тебя в свою базу. Готов заглянуть в будущее?"
        )
    else:
        text = f"С возвращением, {tg_user.first_name}! ✨ Селеста скучала. Что посмотрим сегодня?"
        
    # Отправляем сообщение и прикрепляем клавиатуру
    await message.answer(text, reply_markup=get_main_menu())