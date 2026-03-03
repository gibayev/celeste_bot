import io
from PIL import Image
from aiogram.types import BufferedInputFile
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from bot.keyboards.inline import get_categories_kb, get_spreads_by_category_kb, get_decks_kb
from services.tarot_engine import draw_cards
from data.tarot_deck import SPREADS, DECKS
from services.gemini_api import generate_tarot_reading
from data.tarot_deck import CATEGORIES # <--- добавили CATEGORIES

router = Router()

# Описываем шаги (состояния) для машины состояний
class TarotFSM(StatesGroup):
    choosing_category = State()
    choosing_spread = State()
    choosing_deck = State()

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
        await callback.answer("Эта функция с ИИ-аналитиком скоро появится! 🛠", show_alert=True)
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

    if spread_info["is_premium"]:
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

    if deck_info["is_premium"]:
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