import io
from PIL import Image
from aiogram.types import BufferedInputFile
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from db.crud import get_or_create_user

from bot.keyboards.inline import get_categories_kb, get_spreads_by_category_kb, get_decks_kb, get_ai_recommendation_kb, get_custom_card_count_kb
from services.tarot_engine import draw_cards
from data.tarot_deck import SPREADS, DECKS
from services.gemini_api import generate_tarot_reading, analyze_custom_question
from data.tarot_deck import CATEGORIES # <--- добавили CATEGORIES

router = Router()

# Описываем шаги (состояния) для машины состояний
class TarotFSM(StatesGroup):
    choosing_category = State()
    choosing_spread = State()
    choosing_deck = State()
    entering_custom_question = State()
    choosing_custom_count = State()
    choosing_custom_deck = State()

# --- ШАГ 1: Старт (Выбор темы) ---
@router.message(F.text == "🔮 Расклад Таро")
@router.message(F.command("tarot"))
async def tarot_start(message: Message, state: FSMContext):
    # Переводим пользователя в состояние выбора категории
    await state.set_state(TarotFSM.choosing_category)
    await message.answer(
        "О чем спросим карты сегодня? 🌌\n\nВыбери тему:",
        reply_markup=get_categories_kb()
    )

# --- ШАГ 2: Выбрали тему -> Показываем расклады ---
@router.callback_query(TarotFSM.choosing_category, F.data.startswith("cat_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    cat_id = callback.data.replace("cat_", "")
    
    # Заглушка для кастомного вопроса (сделаем на следующем этапе)
    if cat_id == "custom":
        db_user, _ = await get_or_create_user(callback.from_user.id, callback.from_user.username, callback.from_user.full_name)
        if not db_user.is_premium:
            await callback.answer("👑 Свой вопрос с ИИ-анализом доступен только по Premium подписке!", show_alert=True)
            return
        
        await state.set_state(TarotFSM.entering_custom_question)
        await callback.message.edit_text(
            "✍️ <b>Напиши свой вопрос картам.</b>\n\n"
            "Чем подробнее ты опишешь ситуацию, тем точнее Селеста подберет колоду и количество карт.\n\n"
            "<i>Пример: «Стоит ли мне переезжать в другой город ради новой работы, или лучше остаться?»</i>"
        )
        return

    # Сохраняем выбранную категорию в память FSM
    await state.update_data(category_id=cat_id)
    # Переводим на следующий шаг
    await state.set_state(TarotFSM.choosing_spread)

    await callback.message.edit_text(
        "Отлично. Теперь выбери подходящий расклад:",
        reply_markup=get_spreads_by_category_kb(cat_id)
    )

# --- ШАГ 3: Выбрали расклад -> Показываем колоды ---
@router.callback_query(TarotFSM.choosing_spread, F.data.startswith("spread_"))
async def process_spread(callback: CallbackQuery, state: FSMContext):
    spread_id = callback.data.replace("spread_", "")
    spread_info = SPREADS.get(spread_id)

    # Идем в базу данных и смотрим статус текущего пользователя
    db_user, _ = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        full_name=callback.from_user.full_name
    )

    # Если расклад премиальный, А юзер НЕ премиум — блокируем
    if spread_info["is_premium"] and not db_user.is_premium:
        await callback.answer("👑 Этот расклад доступен только по Premium подписке!", show_alert=True)
        return

    # Сохраняем выбранный расклад в память
    await state.update_data(spread_id=spread_id)
    await state.set_state(TarotFSM.choosing_deck)

    await callback.message.edit_text(
        f"Расклад «{spread_info['name']}». Какую колоду будем использовать?",
        reply_markup=get_decks_kb()
    )

# --- ШАГ 4: Выбрали колоду -> Делаем магию ---
@router.callback_query(TarotFSM.choosing_deck, F.data.startswith("deck_"))
async def process_deck(callback: CallbackQuery, state: FSMContext):
    deck_id = callback.data.replace("deck_", "")
    deck_info = DECKS.get(deck_id)

    # Идем в базу данных и смотрим статус текущего пользователя
    db_user, _ = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        full_name=callback.from_user.full_name
    )

    # Если колода премиальная, А юзер НЕ премиум — блокируем
    if deck_info["is_premium"] and not db_user.is_premium:
        await callback.answer("👑 Эта колода доступна только по Premium подписке!", show_alert=True)
        return

    # Достаем данные, которые мы сохраняли на предыдущих шагах
    user_data = await state.get_data()
    spread_id = user_data["spread_id"]
    category_id = user_data["category_id"] # Достаем ID темы
    
    spread_info = SPREADS.get(spread_id)
    category_name = CATEGORIES.get(category_id, "Общие вопросы") # Получаем красивое название темы

    # Завершаем FSM
    await state.clear()

    await callback.message.edit_text(f"⏳ <i>Тасую колоду «{deck_info['name']}» для расклада «{spread_info['name']}»...</i>")
    await asyncio.sleep(1.5)

    # 1. Тянем карты
    cards = draw_cards(spread_info["cards_count"], deck_id=deck_id)

    # 2. Формируем картинки (с переворотом на лету, если нужно)
    media = []
    for card in cards:
        if card.get("is_reversed"):
            # Открываем картинку с диска
            with Image.open(card["image_path"]) as img:
                # Переворачиваем на 180 градусов
                rotated_img = img.rotate(180)
                
                # Создаем виртуальный файл в оперативной памяти
                img_byte_arr = io.BytesIO()
                rotated_img.save(img_byte_arr, format='JPEG')
                img_byte_arr.seek(0)
                
                # Отправляем виртуальный файл (BufferedInputFile вместо FSInputFile)
                filename = card["image_path"].split("/")[-1]
                media.append(InputMediaPhoto(media=BufferedInputFile(img_byte_arr.read(), filename=f"rev_{filename}")))
        else:
            # Если карта прямая, отправляем как обычно прямо с диска
            media.append(InputMediaPhoto(media=FSInputFile(card["image_path"])))
    # 3. Отправляем альбом и временное сообщение о том, что ИИ думает
    await callback.message.answer_media_group(media=media)
    
    thinking_msg = await callback.message.answer(
        "✨ <i>Селеста вглядывается в карты и слушает шепот звезд... (Генерирую ответ)</i>"
    )
    await callback.answer() # Закрываем часики на кнопке

    # 4. Обращаемся к Gemini за трактовкой
    reading_text = await generate_tarot_reading(
        spread_name=spread_info['name'],
        deck_name=deck_info['name'],
        cards=cards,
        category_name=category_name
    )

    # 5. Заменяем временное сообщение на красивую готовую трактовку
    await thinking_msg.edit_text(reading_text)

# --- КНОПКИ НАЗАД ---
@router.callback_query(F.data == "back_to_categories")
async def back_to_cats(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TarotFSM.choosing_category)
    await callback.message.edit_text("О чем спросим карты сегодня? 🌌\n\nВыбери тему:", reply_markup=get_categories_kb())

@router.callback_query(F.data == "back_to_spreads")
async def back_to_spreads(callback: CallbackQuery, state: FSMContext):
    # Достаем категорию, чтобы показать правильные расклады
    user_data = await state.get_data()
    cat_id = user_data.get("category_id", "general")
    
    await state.set_state(TarotFSM.choosing_spread)
    await callback.message.edit_text("Отлично. Теперь выбери подходящий расклад:", reply_markup=get_spreads_by_category_kb(cat_id))

 # ========================================================
# ЛОГИКА ДЛЯ "СВОЕГО ВОПРОСА" (PREMIUM)
# ========================================================

@router.message(TarotFSM.entering_custom_question, F.text)
async def process_custom_question_text(message: Message, state: FSMContext):
    user_question = message.text
    # Сохраняем вопрос юзера, чтобы ИИ потом на него ответил
    await state.update_data(user_question=user_question) 
    
    thinking_msg = await message.answer("✨ <i>Селеста вчитывается в твои слова и советуется со звездами...</i>")
    
    # 1. Отправляем вопрос в ИИ-анализатор
    recommendation = await analyze_custom_question(user_question)
    rec_deck_id = recommendation["deck"]
    rec_count = recommendation["count"]
    
    deck_name = DECKS.get(rec_deck_id, {}).get("name", "Классическое Таро Уэйта")
    
    # 2. Предлагаем выбор
    text = (
        f"Я проанализировала твою ситуацию.\n\n"
        f"🔮 <b>Моя рекомендация для лучшего ответа:</b>\n"
        f"• Колода: <b>{deck_name}</b>\n"
        f"• Количество карт: <b>{rec_count}</b>\n\n"
        f"Доверимся моему выбору или настроим вручную?"
    )
    await thinking_msg.edit_text(text, reply_markup=get_ai_recommendation_kb(rec_deck_id, rec_count))

# Обработка кнопки "Использовать рекомендацию"
@router.callback_query(F.data.startswith("ai_accept_"))
async def accept_ai_recommendation(callback: CallbackQuery, state: FSMContext):
    # Разбираем callback_data (например: ai_accept_waite_3)
    parts = callback.data.split("_")
    deck_id = parts[2]
    cards_count = int(parts[3])
    
    await generate_custom_reading(callback, state, deck_id, cards_count)

# Обработка кнопки "Выбрать вручную"
@router.callback_query(F.data == "ai_manual")
async def manual_custom_selection(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TarotFSM.choosing_custom_count)
    await callback.message.edit_text("Хорошо. Сколько карт мы достанем для ответа на твой вопрос?", reply_markup=get_custom_card_count_kb())

# Выбор количества карт вручную
@router.callback_query(TarotFSM.choosing_custom_count, F.data.startswith("ccount_"))
async def manual_custom_count(callback: CallbackQuery, state: FSMContext):
    count = int(callback.data.replace("ccount_", ""))
    await state.update_data(custom_count=count)
    await state.set_state(TarotFSM.choosing_custom_deck)
    await callback.message.edit_text(f"Количество карт: {count}.\nКакую колоду будем использовать?", reply_markup=get_decks_kb())

# Выбор колоды вручную -> Запуск
@router.callback_query(TarotFSM.choosing_custom_deck, F.data.startswith("deck_"))
async def manual_custom_deck(callback: CallbackQuery, state: FSMContext):
    deck_id = callback.data.replace("deck_", "")
    user_data = await state.get_data()
    cards_count = user_data["custom_count"]
    
    await generate_custom_reading(callback, state, deck_id, cards_count)

# ГЛАВНЫЙ ГЕНЕРАТОР КАСТОМНЫХ РАСКЛАДОВ
async def generate_custom_reading(callback: CallbackQuery, state: FSMContext, deck_id: str, cards_count: int):
    user_data = await state.get_data()
    user_question = user_data.get("user_question", "Индивидуальный вопрос")
    deck_info = DECKS.get(deck_id)
    
    await state.clear()
    
    await callback.message.edit_text(f"⏳ <i>Тасую колоду «{deck_info['name']}» для твоего личного вопроса...</i>")
    await asyncio.sleep(1.5)

    cards = draw_cards(cards_count, deck_id=deck_id)
    
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
            
    await callback.message.answer_media_group(media=media)
    thinking_msg = await callback.message.answer("✨ <i>Селеста читает знаки и слушает шепот звезд...</i>")
    await callback.answer()

    reading_text = await generate_tarot_reading(
        spread_name=f"Свой вопрос: {user_question}",
        deck_name=deck_info['name'],
        cards=cards,
        category_name="Индивидуальный вопрос"
    )
    
    await thinking_msg.edit_text(reading_text)   