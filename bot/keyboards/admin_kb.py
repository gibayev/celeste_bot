from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_admin_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📊 Статистика и Финансы", callback_data="admin_stats"))
    builder.row(InlineKeyboardButton(text="📢 Сделать рассылку", callback_data="admin_broadcast"))
    builder.row(InlineKeyboardButton(text="👑 Управление Premium", callback_data="admin_manage"))
    return builder.as_markup()

def get_cancel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel"))
    return builder.as_markup()