import io
import os
from PIL import Image
from aiogram.types import BufferedInputFile
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime

# База и CRUD
from db.crud import get_or_create_user, check_and_update_limit
# Клавиатуры
from bot.keyboards.inline import (
    get_categories_kb, get_gender_kb, get_post_reading_kb, get_premium_plans_kb
)
# Сервисы
from services.tarot_engine import draw_cards
from services.gemini_api import generate_tarot_reading, analyze_custom_question
from data.tarot_deck import DECKS, CATEGORIES

router = Router()

class TarotFSM(StatesGroup):
    choosing_category = State()
    choosing_gender = State()
    entering_question = State()

def split_message(text, max_length=4000):
    """Режет текст на куски для Telegram"""
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

# --- ШАГ 1: Старт (Выбор темы) ---
@router.message(F.text == "🔮 Расклад Таро")
@router.message(F.command("tarot"))
async def tarot_start(message: Message, state: FSMContext):
    await state.set_state(TarotFSM.choosing_category)
    await message.answer(
        "О чем спросим карты сегодня? 🌌\n\nВыбери сферу вопроса:",
        reply_markup=get_categories_kb()
    )

# --- ШАГ 2: Выбор категории -> Переход к полу ---
@router.callback_query(TarotFSM.choosing_category, F.data.startswith("cat_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    cat_id = callback.data.replace("cat_", "")
    await state.update_data(category_id=cat_id)
    
    await state.set_state(TarotFSM.choosing_gender)
    await callback.message.edit_text(
        "Чтобы я могла лучше настроиться на твою энергию, укажи свой пол:",
        reply_markup=get_gender_kb()
    )

# --- ШАГ 3: Выбор пола -> Запрос вопроса ---
@router.callback_query(TarotFSM.choosing_gender, F.data.startswith("gender_"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    gender = callback.data.replace("gender_", "")
    await state.update_data(user_gender=gender)
    
    await state.set_state(TarotFSM.entering_question)
    await callback.message.edit_text(
        "✨ <b>Напиши свой вопрос Оракулу.</b>\n\n"
        "Чем подробнее ты опишешь ситуацию, тем точнее Селеста сможет прочитать знаки судьбы."
    )

# --- ШАГ 4: ГЛАВНЫЙ ОБРАБОТЧИК ВОПРОСА ---
@router.message(TarotFSM.entering_question, F.text)
async def handle_tarot_question(message: Message, state: FSMContext):
    # 1. Проверяем лимиты в базе
    can_ask = await check_and_update_limit(message.from_user.id)
    if not can_ask:
        await message.answer(
            "🚫 <b>Дневной лимит исчерпан.</b>\n\n"
            "Обычный доступ: 2 вопроса в день.\n"
            "Premium доступ: 15 вопросов в день.\n\n"
            "Лимиты обновляются в полночь по МСК.",
            reply_markup=get_premium_plans_kb()
        )
        await state.clear()
        return

    user_data = await state.get_data()
    question = message.text
    category_id = user_data.get("category_id", "general")
    user_gender = user_data.get("user_gender", "neutral")
    category_name = CATEGORIES.get(category_id, "Общие вопросы")

    # Получаем данные пользователя для проверки Premium
    db_user, _ = await get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    
    thinking_msg = await message.answer("✨ <i>Селеста вчитывается в твои слова и советуется со звездами...</i>")

    # 2. Логика выбора колоды и количества карт
    if not db_user.is_premium:
        # Для обычных: только Уэйт и 3 карты (или 1 если вопрос "когда")
        deck_id = "waite"
        cards_count = 1 if category_id == "timing" else 3
        explanation = "Для твоего вопроса я выбрала классическую колоду Уэйта и 3 карты для базового анализа."
    else:
        # Для Premium: ИИ делает глубокий анализ
        analysis = await analyze_custom_question(question)
        deck_id = analysis["deck"]
        cards_count = analysis["count"]
        explanation = analysis["explanation"]

    # Обновляем сообщение для пользователя
    deck_name = DECKS.get(deck_id, {}).get("name", "Классика")
    await thinking_msg.edit_text(
        f"🔮 <b>Выбор Оракула:</b>\n"
        f"• {explanation}\n\n"
        f"⏳ <i>Тасую колоду «{deck_name}» ({cards_count} шт.)...</i>"
    )
    
    await asyncio.sleep(2) # Пауза для атмосферы
    await state.clear()

    # 3. Тянем карты
    cards = draw_cards(cards_count, deck_id=deck_id)

    # 4. Обработка изображений (твоя логика PIL)
    media = []
    for card in cards:
        if card.get("is_reversed"):
            with Image.open(card["image_path"]) as img:
                rotated_img = img.rotate(180)
                img_byte_arr = io.BytesIO()
                rotated_img.save(img_byte_arr, format='JPEG')
                img_byte_arr.seek(0)
                filename = card["image_path"].split("/")[-1]
                media.append(InputMediaPhoto(media=BufferedInputFile(img_byte_arr.read(), filename=f"rev_{filename}")))
        else:
            media.append(InputMediaPhoto(media=FSInputFile(card["image_path"])))

    # 5. Отправка результата
    await message.answer_media_group(media=media)
    
    final_thinking_msg = await message.answer("🌌 <i>Селеста читает узоры карт...</i>")

    # 6. Генерация текста (с учетом пола!)
    reading_text = await generate_tarot_reading(
        spread_name=f"Индивидуальный запрос: {question}",
        deck_name=deck_name,
        cards=cards,
        category_name=category_name,
        user_gender=user_gender
    )

    # 7. Безопасная отправка (разбивка длинных текстов)
    if len(reading_text) <= 4096:
        await final_thinking_msg.edit_text(reading_text, reply_markup=get_post_reading_kb())
    else:
        parts = split_message(reading_text)
        await final_thinking_msg.edit_text(parts[0])
        for part in parts[1:-1]:
            await message.answer(part)
        await message.answer(parts[-1], reply_markup=get_post_reading_kb())

# --- КНОПКИ НАЗАД ---
@router.callback_query(F.data == "back_to_categories")
async def back_to_cats(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(TarotFSM.choosing_category)
    await callback.message.edit_text("О чем спросим карты сегодня? 🌌\n\nВыбери тему:", reply_markup=get_categories_kb())