from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    """Генерирует главное меню с кнопками"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            # Первый ряд кнопок
            [KeyboardButton(text="🔮 Расклад Таро"), KeyboardButton(text="✨ Матрица Судьбы")],
            # Второй ряд кнопок
            [KeyboardButton(text="🌟 Гороскоп на день"), KeyboardButton(text="👑 Premium")],
        ],
        resize_keyboard=True, # Делает кнопки аккуратными, а не на пол-экрана
        input_field_placeholder="Выбери, что подскажут звезды..."
    )
    return keyboard