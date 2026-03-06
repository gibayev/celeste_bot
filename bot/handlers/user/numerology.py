# bot/handlers/user/numerology.py
import re
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from services.numerology_engine import calculate_life_path_number
from services.gemini_api import generate_numerology_reading
# импортируй свои клавиатуры, если нужно

router = Router()

class NumerologyState(StatesGroup):
    waiting_for_birth_date = State()

@router.message(F.text == "🔢 Нумерология") # Замени на свою кнопку
async def start_numerology(message: types.Message, state: FSMContext):
    await message.answer(
        "✨ Добро пожаловать в раздел Нумерологии!\n\n"
        "Чтобы узнать свое Число Жизненного Пути и кармические задачи, "
        "напиши свою дату рождения в формате ДД.ММ.ГГГГ (например, 15.04.1995):"
    )
    await state.set_state(NumerologyState.waiting_for_birth_date)

@router.message(NumerologyState.waiting_for_birth_date)
async def process_birth_date(message: types.Message, state: FSMContext):
    date_str = message.text.strip()
    
    # Простая валидация даты через регулярное выражение
    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", date_str):
        await message.answer("⚠️ Пожалуйста, введи дату в правильном формате: ДД.ММ.ГГГГ (например, 15.04.1995)")
        return

    # Отправляем сообщение-заглушку, пока ИИ думает
    wait_msg = await message.answer("🧮 <i>Считаю твои числа и связываюсь со Вселенной...</i>", parse_mode="HTML")
    await message.bot.send_chat_action(message.chat.id, 'typing')

    try:
        # 1. Считаем число
        life_path_number = calculate_life_path_number(date_str)
        
        # 2. Генерируем текст через Gemini
        reading = await generate_numerology_reading(date_str, life_path_number)
        
        # 3. Отправляем результат
        await wait_msg.edit_text(f"🌟 <b>Твое Число Жизненного Пути: {life_path_number}</b>\n\n{reading}", parse_mode="HTML")
        
    except Exception as e:
        await wait_msg.edit_text("Ой, космические потоки сейчас нестабильны. Попробуй еще раз чуть позже! 🌌")
        print(f"Error in numerology: {e}")
    finally:
        await state.clear() # Очищаем состояние