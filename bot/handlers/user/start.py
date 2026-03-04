from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.keyboards.reply import get_main_menu

# Импортируем наши функции для работы с БД (ОБЕ ФУНКЦИИ НАВЕРХУ)
from db.crud import get_or_create_user, set_user_premium

# Создаем роутер
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

# Секретная команда для разработчика
@router.message(F.text == "Селеста, дай мне силу")
async def secret_premium_command(message: Message):
    # Выдаем статус в БД
    await set_user_premium(message.from_user.id, is_premium=True)
    
    await message.answer(
        "✨ <b>Тайные знания открыты!</b>\n\n"
        "Теперь ты Premium-пользователь. Тебе доступны все колоды и глубокие расклады.",
        show_alert=True
    )

# Секретная команда для снятия подписки (для тестов)
@router.message(F.text == "Селеста, забери силу")
async def secret_remove_premium(message: Message):
    # Устанавливаем is_premium = False. 
    # Наша функция set_user_premium автоматически обнулит дату!
    await set_user_premium(message.from_user.id, is_premium=False)
    
    await message.answer(
        "📉 <b>Связь с Космосом прервана...</b>\n\n"
        "Твоя Premium-подписка аннулирована. Теперь ты обычный смертный.",
        show_alert=True
    )    