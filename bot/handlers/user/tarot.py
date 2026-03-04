import io
import os # Добавили os для проверки путей
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
from data.tarot_deck import CATEGORIES 

router = Router()

class TarotFSM(StatesGroup):
    choosing_category = State()
    choosing_spread = State()
    choosing_deck = State()
    entering_custom_question = State()
    choosing_custom_count = State()
    choosing_custom_deck = State()

# --- ШАГ 1 ---
@router.message(F.text == "🔮 Расклад Таро")
@router.message(F.command("tarot"))
async def tarot_start(message: Message, state: FSMContext):
    await state.set_state(TarotFSM.choosing_category)
    await message.answer(
        "О чем спросим карты сегодня? 🌌\n\nВыбери тему:",
        reply_markup=get_categories_kb()
    )

# --- ШАГ 2 ---
@router.callback_query(TarotFSM.choosing_category, F.data.startswith("cat_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer() # ОТВЕЧАЕМ СРАЗУ
    cat_id = callback.data.replace("cat_", "")
    
    if cat_id == "custom":
        db_user, _ = await get_or_create_user(callback.from_user.id, callback.from_user.username, callback.from_user.full_name)
        if not db_user.is_premium:
            # Если не премиум, то тут используем show_alert=True внутри answer
            await callback.answer("Прямой диалог с Оракулом и личные вопросы доступны только по Premium подписке!", show_alert=True)
            return
        
        await state.set_state(TarotFSM.entering_custom_question)
        await callback.message.edit_text(
            "✍️ <b>Напиши свой вопрос картам.</b>\n\n"
            "Чем подробнее ты опишешь ситуацию, тем точнее я смогу подобрать нужную колоду и прочитать послание звезд."
        )
        return

    await state.update_data(category_id=cat_id)
    await state.set_state(TarotFSM.choosing_spread)
    await callback.message.edit_text(
        "Отлично. Теперь выбери подходящий расклад:",
        reply_markup=get_spreads_by_category_kb(cat_id)
    )

# --- ШАГ 3 ---
@router.callback_query(TarotFSM.choosing_spread, F.data.startswith("spread_"))
async def process_spread(callback: CallbackQuery, state: FSMContext):
    await callback.answer() # ОТВЕЧАЕМ СРАЗУ
    spread_id = callback.data.replace("spread_", "")
    spread_info = SPREADS.get(spread_id)

    db_user, _ = await get_or_create_user(callback.from_user.id, callback.from_user.username, callback.from_user.full_name)

    if spread_info["is_premium"] and not db_user.is_premium:
        await callback.answer("👑 Этот расклад доступен только по Premium подписке!", show_alert=True)
        return

    await state.update_data(spread_id=spread_id)
    await state.set_state(TarotFSM.choosing_deck)

    await callback.message.edit_text(
        f"Расклад «{spread_info['name']}». Какую колоду будем использовать?",
        reply_markup=get_decks_kb()
    )

# --- ШАГ 4 ---
@router.callback_query(TarotFSM.choosing_deck, F.data.startswith("deck_"))
async def process_deck(callback: CallbackQuery, state: FSMContext):
    # КРИТИЧЕСКИЙ МОМЕНТ: Сначала отвечаем Telegram, чтобы убрать часики
    await callback.answer() 
    
    deck_id = callback.data.replace("deck_", "")
    deck_info = DECKS.get(deck_id)

    # Проверка на наличие папки с колодой
    deck_path = f"assets/tarot/{deck_id}/"
    if not os.path.exists(deck_path):
        await callback.answer("⏳ Колода еще в пути. Выбери Классику!", show_alert=True)
        return

    db_user, _ = await get_or_create_user(callback.from_user.id, callback.from_user.username, callback.from_user.full_name)

    if deck_info["is_premium"] and not db_user.is_premium:
        await callback.answer("👑 Эта колода доступна только по Premium подписке!", show_alert=True)
        return

    user_data = await state.get_data()
    spread_id = user_data["spread_id"]
    category_id = user_data["category_id"]
    spread_info = SPREADS.get(spread_id)
    category_name = CATEGORIES.get(category_id, "Общие вопросы")

    await state.clear()

    # Информируем юзера, что процесс пошел
    await callback.message.edit_text(f"⏳ <i>Тасую колоду «{deck_info['name']}»...</i>")
    
    # Тянем карты
    cards = draw_cards(spread_info["cards_count"], deck_id=deck_id)

    # Обработка картинок
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

    # Отправляем альбом
    await callback.message.answer_media_group(media=media)
    
    thinking_msg = await callback.message.answer(
        "✨ <i>Селеста вглядывается в карты и слушает шепот звезд...</i>"
    )

    # Запускаем Gemini (самый долгий процесс)
    reading_text = await generate_tarot_reading(
        spread_name=spread_info['name'],
        deck_name=deck_info['name'],
        cards=cards,
        category_name=category_name
    )

    await thinking_msg.edit_text(reading_text)

# --- КНОПКИ НАЗАД ---
@router.callback_query(F.data == "back_to_categories")
async def back_to_cats(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(TarotFSM.choosing_category)
    await callback.message.edit_text("О чем спросим карты сегодня? 🌌\n\nВыбери тему:", reply_markup=get_categories_kb())

@router.callback_query(F.data == "back_to_spreads")
async def back_to_spreads(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
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
    await state.update_data(user_question=user_question) 
    
    thinking_msg = await message.answer("✨ <i>Селеста вчитывается в твои слова...</i>")
    recommendation = await analyze_custom_question(user_question)
    rec_deck_id = recommendation["deck"]
    rec_count = recommendation["count"]
    deck_name = DECKS.get(rec_deck_id, {}).get("name", "Классика")
    
    text = (
        f"Я проанализировала твою ситуацию.\n\n"
        f"🔮 <b>Моя рекомендация:</b>\n"
        f"• Колода: <b>{deck_name}</b>\n"
        f"• Количество карт: <b>{rec_count}</b>\n\n"
        f"Доверимся моему выбору или настроим вручную?"
    )
    await thinking_msg.edit_text(text, reply_markup=get_ai_recommendation_kb(rec_deck_id, rec_count))

@router.callback_query(F.data.startswith("ai_accept_"))
async def accept_ai_recommendation(callback: CallbackQuery, state: FSMContext):
    await callback.answer() # ОТВЕЧАЕМ СРАЗУ
    parts = callback.data.split("_")
    deck_id = parts[2]
    cards_count = int(parts[3])
    await generate_custom_reading(callback, state, deck_id, cards_count)

@router.callback_query(F.data == "ai_manual")
async def manual_custom_selection(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(TarotFSM.choosing_custom_count)
    await callback.message.edit_text("Сколько карт мы достанем?", reply_markup=get_custom_card_count_kb())

@router.callback_query(TarotFSM.choosing_custom_count, F.data.startswith("ccount_"))
async def manual_custom_count(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    count = int(callback.data.replace("ccount_", ""))
    await state.update_data(custom_count=count)
    await state.set_state(TarotFSM.choosing_custom_deck)
    await callback.message.edit_text(f"Количество карт: {count}.\nКакую колоду будем использовать?", reply_markup=get_decks_kb())

@router.callback_query(TarotFSM.choosing_custom_deck, F.data.startswith("deck_"))
async def manual_custom_deck(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    deck_id = callback.data.replace("deck_", "")
    user_data = await state.get_data()
    cards_count = user_data["custom_count"]
    await generate_custom_reading(callback, state, deck_id, cards_count)

async def generate_custom_reading(callback: CallbackQuery, state: FSMContext, deck_id: str, cards_count: int):
    # Здесь мы уже вызвали callback.answer() в вызывающей функции
    user_data = await state.get_data()
    user_question = user_data.get("user_question", "Индивидуальный вопрос")
    deck_info = DECKS.get(deck_id)
    await state.clear()
    
    await callback.message.edit_text(f"⏳ <i>Тасую колоду «{deck_info['name']}»...</i>")
    await asyncio.sleep(1.0)

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
    thinking_msg = await callback.message.answer("✨ <i>Селеста читает знаки...</i>")

    reading_text = await generate_tarot_reading(
        spread_name=f"Свой вопрос: {user_question}",
        deck_name=deck_info['name'],
        cards=cards,
        category_name="Индивидуальный вопрос"
    )
    
    await thinking_msg.edit_text(reading_text)