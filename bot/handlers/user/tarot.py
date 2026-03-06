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
    get_categories_kb, get_post_reading_kb, get_premium_plans_kb
)
# Сервисы
from services.tarot_engine import draw_cards
from services.gemini_api import generate_tarot_reading, analyze_custom_question
from services.helpers import calculate_dynamic_age, get_zodiac_sign
from data.tarot_deck import DECKS, CATEGORIES

router = Router()

class TarotFSM(StatesGroup):
    choosing_category = State()
    entering_question = State()

def split_message(text, max_length=4000):
    """Режет текст на куски для Telegram"""
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

# Контекстные подсказки в зависимости от выбранной темы
CATEGORY_PROMPTS = {
    "cat_love": "❤️ <b>Любовь и отношения</b>\n\nНапиши свой вопрос. Если спрашиваешь про конкретного человека, обязательно укажи его <b>имя и дату рождения (или знак зодиака)</b>, если знаешь. Чем больше деталей, тем точнее Селеста считает энергию между вами.",
    "cat_career": "💼 <b>Работа и финансы</b>\n\nНапиши свой вопрос. Для максимально точного ответа вкратце опиши: <b>в какой сфере ты работаешь</b>, какой у тебя опыт и что сейчас происходит (ищешь работу, конфликт с боссом, ждешь повышения или открываешь бизнес)?",
    "cat_health": "🌿 <b>Здоровье и энергия</b>\n\nОпиши свое текущее внутреннее состояние. Что тебя сейчас тревожит, выматывает или забирает силы?",
    "cat_timing": "⏳ <b>Тайминг (Когда это случится?)</b>\n\nОпиши событие, которого ты ждешь. Укажи контекст (например: 'когда я перееду в другой город?' или 'когда мне ответят после собеседования?').",
    "cat_general": "🌌 <b>Общие вопросы</b>\n\nНапиши свой вопрос Оракулу. Чем подробнее ты опишешь ситуацию, тем точнее Селеста сможет прочитать знаки судьбы.",
    "cat_other": "✨ <b>Другое / Свой вопрос</b>\n\nСпроси о чем угодно! Опиши ситуацию максимально подробно, чтобы карты настроились на твою волну."
}

# --- ШАГ 1: Старт (Выбор темы) ---
@router.message(F.text == "🔮 Расклад Таро")
@router.message(F.command("tarot"))
async def tarot_start(message: Message, state: FSMContext):
    await state.set_state(TarotFSM.choosing_category)
    await message.answer(
        "О чем спросим карты сегодня? 🌌\n\nВыбери сферу вопроса:",
        reply_markup=get_categories_kb()
    )

# --- ШАГ 2: Выбор категории -> Пропускаем пол -> Запрос вопроса ---
@router.callback_query(TarotFSM.choosing_category, F.data.startswith("cat_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    cat_id_full = callback.data
    cat_id_clean = cat_id_full.replace("cat_", "")
    await state.update_data(category_id=cat_id_clean)
    
    # Берем нужную подсказку из словаря
    prompt_text = CATEGORY_PROMPTS.get(cat_id_full, CATEGORY_PROMPTS["cat_general"])
    
    await state.set_state(TarotFSM.entering_question)
    await callback.message.edit_text(prompt_text, parse_mode="HTML")

# --- ШАГ 3: ГЛАВНЫЙ ОБРАБОТЧИК ВОПРОСА ---
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
            reply_markup=get_premium_plans_kb(),
            parse_mode="HTML"
        )
        await state.clear()
        return

    user_data = await state.get_data()
    question = message.text
    category_id = user_data.get("category_id", "general")
    category_name = CATEGORIES.get(category_id, "Общие вопросы")

    # 2. ДОСТАЕМ ВСЕ ДАННЫЕ ЮЗЕРА (ОНБОРДИНГ)
    db_user, _ = await get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    
    user_name = db_user.real_name or message.from_user.first_name
    user_gender = db_user.gender or "neutral"
    user_age = calculate_dynamic_age(db_user.birth_date) if db_user.birth_date else None
    user_zodiac = get_zodiac_sign(db_user.birth_date) if db_user.birth_date else None
    
    thinking_msg = await message.answer(f"✨ <i>{user_name}, Селеста вчитывается в твои слова и советуется со звездами...</i>", parse_mode="HTML")

    # 3. Логика выбора колоды и количества карт
    if not db_user.is_premium:
        deck_id = "waite"
        cards_count = 1 if category_id == "timing" else 3
        explanation = "Для твоего вопроса я выбрала классическую колоду Уэйта и 3 карты для базового анализа."
    else:
        analysis = await analyze_custom_question(question)
        deck_id = analysis.get("deck", "waite")
        cards_count = analysis.get("count", 3)
        explanation = analysis.get("explanation", "Подобрала карты под твою энергию.")

    deck_name = DECKS.get(deck_id, {}).get("name", "Классика")
    await thinking_msg.edit_text(
        f"🔮 <b>Выбор Оракула:</b>\n"
        f"• {explanation}\n\n"
        f"⏳ <i>Тасую колоду «{deck_name}» ({cards_count} шт.)...</i>",
        parse_mode="HTML"
    )
    
    await asyncio.sleep(2) 
    await state.clear()

    # 4. Тянем карты
    cards = draw_cards(cards_count, deck_id=deck_id)

    # 5. Обработка изображений
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

    await message.answer_media_group(media=media)
    final_thinking_msg = await message.answer("🌌 <i>Селеста читает узоры карт...</i>", parse_mode="HTML")

    # 6. Генерация текста (ПЕРЕДАЕМ ИМЯ И ВСЕ ДАННЫЕ В ИИ!)
    reading_text = await generate_tarot_reading(
        spread_name=f"Индивидуальный запрос: {question}",
        deck_name=deck_name,
        cards=cards,
        category_name=category_name,
        user_name=user_name,     # <--- НОВОЕ: Передаем имя
        user_gender=user_gender,
        user_age=user_age,
        user_zodiac=user_zodiac
    )

    # 7. Безопасная отправка (разбивка длинных текстов)
    if len(reading_text) <= 4096:
        await final_thinking_msg.edit_text(reading_text, reply_markup=get_post_reading_kb(), parse_mode="HTML")
    else:
        parts = split_message(reading_text)
        await final_thinking_msg.edit_text(parts[0], parse_mode="HTML")
        for part in parts[1:-1]:
            await message.answer(part, parse_mode="HTML")
        await message.answer(parts[-1], reply_markup=get_post_reading_kb(), parse_mode="HTML")

# --- КНОПКИ НАЗАД ---
@router.callback_query(F.data == "back_to_categories")
async def back_to_cats(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(TarotFSM.choosing_category)
    await callback.message.edit_text("О чем спросим карты сегодня? 🌌\n\nВыбери тему:", reply_markup=get_categories_kb())