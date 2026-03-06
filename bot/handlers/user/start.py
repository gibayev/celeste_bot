import re
from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from db.crud import get_or_create_user, set_user_premium, update_user_onboarding
from bot.keyboards.reply import get_main_menu
from bot.keyboards.inline import get_onboarding_gender_kb
from services.helpers import calculate_dynamic_age, get_zodiac_sign

router = Router()

# ==========================================
# СОСТОЯНИЯ ДЛЯ ОНБОРДИНГА
# ==========================================
class OnboardingState(StatesGroup):
    waiting_for_name = State()
    waiting_for_gender = State()
    waiting_for_birth_date = State()

# ==========================================
# ХЭНДЛЕР СТАРТА
# ==========================================
@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    # Получаем данные о пользователе из Telegram
    tg_user = message.from_user
    
    # Идем в базу данных: регистрируем или просто получаем инфу
    db_user, is_new = await get_or_create_user(
        telegram_id=tg_user.id,
        username=tg_user.username,
        full_name=tg_user.full_name
    )
    
    # ПРОДУКТОВАЯ ЛОГИКА: Проверяем, заполнена ли анкета (онбординг)
    if not db_user.birth_date:
        await message.answer(
            "Привет! 🌌 Я — Селеста. Твоя личная подруга-оракул.\n\n"
            "Чтобы я могла давать тебе точные советы, делать глубокие расклады и "
            "понимать твою энергию матриц, давай познакомимся поближе.\n\n"
            "<b>Как мне к тебе обращаться?</b> (Напиши свое имя)",
            parse_mode="HTML"
        )
        await state.set_state(OnboardingState.waiting_for_name)
        return

    # Если юзер уже давно с нами — вычисляем его динамический возраст и знак
    age = calculate_dynamic_age(db_user.birth_date)
    zodiac = get_zodiac_sign(db_user.birth_date)
    
    # Обращаемся по реальному имени, если оно есть
    name_to_use = db_user.real_name or tg_user.first_name
    
    text = f"С возвращением, {name_to_use}! ✨ Селеста скучала.\n"
    if age and zodiac:
        text += f"<i>(Вижу твою энергию: {zodiac}, {age})</i>\n\n"
    
    text += "Что посмотрим сегодня?"
        
    await message.answer(text, parse_mode="HTML", reply_markup=get_main_menu())

# ==========================================
# ШАГИ ОНБОРДИНГА
# ==========================================
@router.message(OnboardingState.waiting_for_name)
async def process_onboarding_name(message: types.Message, state: FSMContext):
    real_name = message.text.strip()
    
    # Сохраняем имя временно в память FSM
    await state.update_data(real_name=real_name)
    
    await message.answer(
        f"Очень приятно, {real_name}! ✨\n\n"
        f"Теперь подскажи, как мне к тебе обращаться в текстах раскладов?",
        reply_markup=get_onboarding_gender_kb()
    )
    await state.set_state(OnboardingState.waiting_for_gender)

@router.callback_query(OnboardingState.waiting_for_gender, F.data.startswith("onboard_gender_"))
async def process_onboarding_gender(callback: types.CallbackQuery, state: FSMContext):
    # Вытаскиваем 'male', 'female' или 'neutral' из callback_data
    gender_code = callback.data.replace("onboard_gender_", "")
    await state.update_data(gender=gender_code)
    
    await callback.message.edit_text(
        "Супер! И последний, самый важный шаг.\n\n"
        "Напиши свою <b>дату рождения</b> в формате ДД.ММ.ГГГГ (например, 15.04.1995).\n"
        "Она нужна мне для нумерологии, астрологии и расчета твоей матрицы:",
        parse_mode="HTML"
    )
    await state.set_state(OnboardingState.waiting_for_birth_date)

@router.message(OnboardingState.waiting_for_birth_date)
async def process_onboarding_birth_date(message: types.Message, state: FSMContext):
    date_str = message.text.strip()
    
    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", date_str):
        return await message.answer("⚠️ Пожалуйста, введи дату в правильном формате: <b>ДД.ММ.ГГГГ</b> (например, 15.04.1995)", parse_mode="HTML")
        
    # Достаем все собранные данные
    data = await state.get_data()
    real_name = data.get("real_name")
    gender = data.get("gender")
    
    # Сохраняем все разом в Базу Данных!
    await update_user_onboarding(message.from_user.id, real_name, gender, date_str)
    
    # Вычисляем плюшки для вау-эффекта
    age = calculate_dynamic_age(date_str)
    zodiac = get_zodiac_sign(date_str)
    
    await message.answer(
        f"Готово! 🎉 Значит, по знаку ты <b>{zodiac}</b>, и тебе <b>{age}</b>!\n\n"
        f"Теперь мы на одной волне. Можешь спрашивать меня о чем угодно, я буду учитывать твою матрицу и энергию.\n\n"
        f"Выбирай, с чего начнем 👇",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )
    await state.clear()

# ==========================================
# СЕКРЕТНЫЕ КОМАНДЫ РАЗРАБОТЧИКА
# ==========================================
@router.message(F.text == "Селеста, дай мне силу")
async def secret_premium_command(message: types.Message):
    await set_user_premium(message.from_user.id, is_premium=True)
    await message.answer(
        "✨ <b>Тайные знания открыты!</b>\n\n"
        "Теперь ты Premium-пользователь. Тебе доступны все колоды и глубокие расклады.",
        parse_mode="HTML"
    )

@router.message(F.text == "Селеста, забери силу")
async def secret_remove_premium(message: types.Message):
    await set_user_premium(message.from_user.id, is_premium=False)
    await message.answer(
        "📉 <b>Связь с Космосом прервана...</b>\n\n"
        "Твоя Premium-подписка аннулирована. Теперь ты обычный смертный.",
        parse_mode="HTML"
    )