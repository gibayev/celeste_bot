from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Мы оставляем импорт данных на случай использования в ручных режимах
from data.tarot_deck import CATEGORIES, SPREADS, DECKS

def get_categories_kb() -> InlineKeyboardMarkup:
    """Шаг 1: Выбор сферы (категории) вопроса"""
    builder = InlineKeyboardBuilder()
    
    # Расширенный список категорий для более точной настройки ИИ
    cats = [
        ("🌌 Общие вопросы", "cat_general"),
        ("❤️ Любовь и отношения", "cat_love"),
        ("💼 Работа и финансы", "cat_career"),
        ("🌿 Здоровье и энергия", "cat_health"),
        ("⏳ Тайминг (Когда?)", "cat_timing"),
        ("✨ Другое / Свой вопрос", "cat_other")
    ]
    
    for text, callback_data in cats:
        builder.row(InlineKeyboardButton(text=text, callback_data=callback_data))
        
    return builder.as_markup()

def get_gender_kb() -> InlineKeyboardMarkup:
    """Шаг 2: Выбор пола для корректного обращения Селесты"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🙋‍♂️ Мужчина", callback_data="gender_male"),
        InlineKeyboardButton(text="🙋‍♀️ Женщина", callback_data="gender_female")
    )
    builder.row(InlineKeyboardButton(text="✨ Пропустить / Не важно", callback_data="gender_neutral"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories"))
    
    return builder.as_markup()

def get_ai_recommendation_kb(deck_id: str, count: int) -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения выбора ИИ (для Premium)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✨ Использовать рекомендацию", callback_data=f"ai_accept_{deck_id}_{count}"))
    builder.row(InlineKeyboardButton(text="⚙️ Выбрать вручную", callback_data="ai_manual"))
    
    return builder.as_markup()

def get_post_reading_kb() -> InlineKeyboardMarkup:
    """Кнопки после завершения расклада"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔮 Задать новый вопрос", callback_data="back_to_categories"))
    
    return builder.as_markup()

# --- СЛЕДУЮЩИЕ ФУНКЦИИ МЫ СОХРАНЯЕМ ДЛЯ РУЧНОГО РЕЖИМА И АДМИНКИ ---

def get_spreads_by_category_kb(category_id: str) -> InlineKeyboardMarkup:
    """Выбор расклада (если пользователь захочет выбрать сам)"""
    builder = InlineKeyboardBuilder()
    for spread_id, spread_info in SPREADS.items():
        if spread_info["category"] == category_id:
            prefix = "👑 " if spread_info["is_premium"] else "✨ "
            builder.row(InlineKeyboardButton(
                text=f"{prefix}{spread_info['name']}",
                callback_data=f"spread_{spread_id}"
            ))
    builder.row(InlineKeyboardButton(text="⬅️ Назад к темам", callback_data="back_to_categories"))
    return builder.as_markup()

def get_decks_kb() -> InlineKeyboardMarkup:
    """Выбор колоды"""
    builder = InlineKeyboardBuilder()
    for deck_id, deck_info in DECKS.items():
        prefix = "👑 " if deck_info["is_premium"] else "🃏 "
        builder.row(InlineKeyboardButton(
            text=f"{prefix}{deck_info['name']}",
            callback_data=f"deck_{deck_id}"
        ))
    return builder.as_markup()

def get_custom_card_count_kb() -> InlineKeyboardMarkup:
    """Выбор количества карт"""
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

def get_premium_plans_kb() -> InlineKeyboardMarkup:
    """Тарифы Premium"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="1 неделя (1 ⭐️)", callback_data="buy_premium_7"))
    builder.row(InlineKeyboardButton(text="1 месяц (150 ⭐️)", callback_data="buy_premium_30"))
    builder.row(InlineKeyboardButton(text="3 месяца (400 ⭐️) 🔥", callback_data="buy_premium_90"))
    builder.row(InlineKeyboardButton(text="6 месяцев (750 ⭐️) 💎", callback_data="buy_premium_180"))
    builder.row(InlineKeyboardButton(text="1 год (1400 ⭐️) 👑", callback_data="buy_premium_365"))
    
    return builder.as_markup()