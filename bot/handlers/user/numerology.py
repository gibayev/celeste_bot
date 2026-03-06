import re
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from services.numerology_engine import calculate_life_path_number
from services.gemini_api import generate_numerology_reading
from db.crud import get_user, update_user_birth_date
from bot.keyboards.inline import get_numerology_main_kb, get_numerology_post_kb, get_premium_plans_kb

router = Router()

class NumerologyState(StatesGroup):
    waiting_for_my_date = State()
    waiting_for_other_date = State()

# ==========================================
# 1. ВХОД В МЕНЮ НУМЕРОЛОГИИ
# ==========================================

@router.message(Command("numerology"))
@router.message(F.text == "🔢 Нумерология")
async def numerology_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    # Получаем юзера из БД для проверки наличия даты рождения
    user = await get_user(message.from_user.id)
    has_date = bool(user and user.birth_date)
    
    await message.answer(
        "✨ <b>Нумерология | Оракул</b>\n\n"
        "Числа хранят в себе код нашей судьбы. Здесь ты можешь узнать свои скрытые таланты, "
        "кармические задачи и истинный путь души.\n\n"
        "<i>Выбери действие ниже:</i>",
        parse_mode="HTML",
        reply_markup=get_numerology_main_kb(has_date)
    )

@router.callback_query(F.data == "back_to_numerology")
async def back_to_numerology_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user = await get_user(callback.from_user.id)
    has_date = bool(user and user.birth_date)
    
    await callback.message.edit_text(
        "✨ <b>Нумерология | Оракул</b>\n\n"
        "Числа хранят в себе код нашей судьбы. Здесь ты можешь узнать свои скрытые таланты, "
        "кармические задачи и истинный путь души.\n\n"
        "<i>Выбери действие ниже:</i>",
        parse_mode="HTML",
        reply_markup=get_numerology_main_kb(has_date)
    )

# ==========================================
# 2. ОБРАБОТКА ИНЛАЙН КНОПОК
# ==========================================

@router.callback_query(F.data.in_(["num_my_path_new", "num_change_date"]))
async def ask_my_date(callback: types.CallbackQuery, state: FSMContext):
    """Спрашиваем дату для самого пользователя (сохраним в БД)"""
    await callback.message.edit_text(
        "✨ Напиши свою дату рождения в формате <b>ДД.ММ.ГГГГ</b> (например, 15.04.1995):",
        parse_mode="HTML"
    )
    await state.set_state(NumerologyState.waiting_for_my_date)

@router.callback_query(F.data == "num_my_path_saved")
async def calculate_saved_date(callback: types.CallbackQuery):
    """Считаем нумерологию по уже сохраненной дате (Бесплатно)"""
    user = await get_user(callback.from_user.id)
    
    if not user or not user.birth_date:
        return await callback.answer("⚠️ Твоя дата не найдена. Нажми 'Изменить мою дату'.", show_alert=True)
    
    await callback.message.delete()
    await process_and_send_reading(callback.message, user.birth_date)

@router.callback_query(F.data == "num_other_path")
async def ask_other_date(callback: types.CallbackQuery, state: FSMContext):
    """Спрашиваем дату другого человека (ПРОВЕРКА PREMIUM)"""
    user = await get_user(callback.from_user.id)
    
    if not user or not user.is_premium:
        await callback.answer("👑 Доступно только с Premium", show_alert=True)
        await callback.message.answer(
            "👑 <b>Расчет для другого человека — это Premium-функция.</b>\n\n"
            "Оформи подписку, чтобы проверять даты рождения партнеров, друзей, начальника или бывших без ограничений!\n"
            "А еще Premium дает глубокие расклады Таро.",
            parse_mode="HTML",
            reply_markup=get_premium_plans_kb()
        )
        return
        
    await callback.message.edit_text(
        "👑 <b>Premium-расчет</b>\n\n"
        "Напиши дату рождения человека в формате <b>ДД.ММ.ГГГГ</b> (например, 22.08.1990):",
        parse_mode="HTML"
    )
    await state.set_state(NumerologyState.waiting_for_other_date)

# ==========================================
# 3. ВВОД ДАТЫ (FSM) И ГЕНЕРАЦИЯ ОТВЕТА
# ==========================================

@router.message(NumerologyState.waiting_for_my_date)
@router.message(NumerologyState.waiting_for_other_date)
async def process_date_input(message: types.Message, state: FSMContext):
    date_str = message.text.strip()
    
    # Жесткая валидация формата
    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", date_str):
        return await message.answer("⚠️ Пожалуйста, введи дату точно в формате: <b>ДД.ММ.ГГГГ</b> (например, 15.04.1995)", parse_mode="HTML")
    
    current_state = await state.get_state()
    
    # Если это дата самого юзера — сохраняем в базу на будущее
    if current_state == NumerologyState.waiting_for_my_date:
        await update_user_birth_date(message.from_user.id, date_str)
        
    await state.clear()
    
    # Запускаем тяжелую логику расчета и ИИ
    await process_and_send_reading(message, date_str)


async def process_and_send_reading(message: types.Message, date_str: str):
    """Вспомогательная функция: крутит спиннер, считает цифры, стучится в ИИ и выдает результат"""
    wait_msg = await message.answer("🧮 <i>Считаю числа судьбы и связываюсь со Вселенной...</i>", parse_mode="HTML")
    await message.bot.send_chat_action(message.chat.id, 'typing')

    try:
        # 1. Чистая математика
        life_path_number = calculate_life_path_number(date_str)
        
        # 2. Магия нейросети
        reading = await generate_numerology_reading(date_str, life_path_number)
        
        # 3. Красивый вывод с кнопкой "Назад"
        result_text = (
            f"🌟 <b>Твое Число Жизненного Пути: {life_path_number}</b> "
            f"(по дате {date_str})\n\n"
            f"{reading}"
        )
        await wait_msg.edit_text(result_text, parse_mode="HTML", reply_markup=get_numerology_post_kb())
        
    except Exception as e:
        await wait_msg.edit_text(
            "Ой, космические потоки сейчас нестабильны. Попробуй еще раз чуть позже! 🌌", 
            reply_markup=get_numerology_post_kb()
        )
        print(f"Error in numerology generation: {e}")