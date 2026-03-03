from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.tarot_deck import CATEGORIES, SPREADS, DECKS

def get_categories_kb() -> InlineKeyboardMarkup:
    """Шаг 1: Выбор категории (темы)"""
    builder = InlineKeyboardBuilder()
    for cat_id, cat_name in CATEGORIES.items():
        builder.row(InlineKeyboardButton(text=cat_name, callback_data=f"cat_{cat_id}"))
    return builder.as_markup()

def get_spreads_by_category_kb(category_id: str) -> InlineKeyboardMarkup:
    """Шаг 2: Выбор расклада (показывает только те, что относятся к выбранной теме)"""
    builder = InlineKeyboardBuilder()
    for spread_id, spread_info in SPREADS.items():
        if spread_info["category"] == category_id:
            prefix = "👑 " if spread_info["is_premium"] else "✨ "
            builder.row(InlineKeyboardButton(
                text=f"{prefix}{spread_info['name']}",
                callback_data=f"spread_{spread_id}"
            ))
    # Добавляем кнопку "Назад"
    builder.row(InlineKeyboardButton(text="⬅️ Назад к темам", callback_data="back_to_categories"))
    return builder.as_markup()

def get_decks_kb() -> InlineKeyboardMarkup:
    """Шаг 3: Выбор колоды"""
    builder = InlineKeyboardBuilder()
    for deck_id, deck_info in DECKS.items():
        prefix = "👑 " if deck_info["is_premium"] else "🃏 "
        builder.row(InlineKeyboardButton(
            text=f"{prefix}{deck_info['name']}",
            callback_data=f"deck_{deck_id}"
        ))
    builder.row(InlineKeyboardButton(text="⬅️ Назад к раскладам", callback_data="back_to_spreads"))
    return builder.as_markup()

def get_ai_recommendation_kb(deck_id: str, count: int) -> InlineKeyboardMarkup:
    """Кнопки после того, как ИИ порекомендовал расклад"""
    builder = InlineKeyboardBuilder()
    # В callback_data зашиваем ID колоды и количество карт
    builder.row(InlineKeyboardButton(text="✨ Использовать рекомендацию", callback_data=f"ai_accept_{deck_id}_{count}"))
    builder.row(InlineKeyboardButton(text="⚙️ Выбрать другую комбинацию", callback_data="ai_manual"))
    return builder.as_markup()

def get_custom_card_count_kb() -> InlineKeyboardMarkup:
    """Ручной выбор количества карт для своего вопроса"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="1 карта", callback_data="ccount_1"),
        InlineKeyboardButton(text="3 карты", callback_data="ccount_3")
    )
    builder.row(
        InlineKeyboardButton(text="5 карт", callback_data="ccount_5"),
        InlineKeyboardButton(text="10 карт", callback_data="ccount_10")
    )
    return builder.as_markup()