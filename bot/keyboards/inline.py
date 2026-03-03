from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Импортируем наши расклады из базы знаний
from data.tarot_deck import SPREADS

def get_tarot_spreads_kb() -> InlineKeyboardMarkup:
    """Генерирует инлайн-кнопки для выбора расклада Таро"""
    builder = InlineKeyboardBuilder()
    
    for spread_id, spread_info in SPREADS.items():
        # Если расклад премиальный, добавляем корону к названию
        prefix = "👑 " if spread_info["is_premium"] else "✨ "
        btn_text = f"{prefix}{spread_info['name']}"
        
        # callback_data - это то, что бот получит "под капотом" при нажатии
        builder.row(
            InlineKeyboardButton(
                text=btn_text,
                callback_data=f"tarot_spread_{spread_id}"
            )
        )
        
    return builder.as_markup()