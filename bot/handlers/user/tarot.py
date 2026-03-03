import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from bot.keyboards.inline import get_categories_kb, get_spreads_by_category_kb, get_decks_kb
from services.tarot_engine import draw_cards
from data.tarot_deck import SPREADS, DECKS

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
    spread_info = SPREADS.get(spread_id)

    # Завершаем FSM (очищаем память состояний)
    await state.clear()

    await callback.message.edit_text(f"⏳ <i>Тасую колоду «{deck_info['name']}» для расклада «{spread_info['name']}»...</i>")
    await asyncio.sleep(1.5)

    # Используем наш движок. Обрати внимание, мы передаем deck_id
    cards = draw_cards(spread_info["cards_count"], deck_id=deck_id)

    media = []
    for card in cards:
        # Если бот упадет тут с ошибкой, значит он не нашел картинку по указанному пути!
        media.append(InputMediaPhoto(media=FSInputFile(card["image_path"])))

    text_result = f"🔮 <b>Твой расклад: {spread_info['name']}</b>\nКолода: {deck_info['name']}\n\n"
    for i, card in enumerate(cards, 1):
        text_result += f"Карта {i}: <b>{card['full_name']}</b>\n"
        
    text_result += "\n<i>(Скоро здесь будет трактовка ИИ...)</i>"

    await callback.message.answer_media_group(media=media)
    await callback.message.answer(text_result)
    await callback.answer()

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