from aiogram import Router, F, Bot
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from db.crud import set_user_premium

router = Router()

# 1. Отправляем счет на оплату
@router.message(F.text == "👑 Premium")
@router.message(F.command("premium"))
async def send_premium_invoice(message: Message, bot: Bot):
    # Цена в Звездах (Telegram Stars). Указываем XTD (это код валюты для Звезд)
    prices = [LabeledPrice(label="Premium на 30 дней", amount=150)]
    
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="👑 Premium подписка",
        description="Открой все тайны: премиальные колоды (Тота, Манара), судьбоносные расклады на 10 карт и возможность задать свой сокровенный вопрос напрямую Оракулу!",
        payload="premium_30_days", # Внутренний код нашего товара
        provider_token="", # Для Telegram Stars токен провайдера должен быть пустым!
        currency="XTD",
        prices=prices,
        # Опционально: можно добавить красивую картинку для чека
        # photo_url="ссылка_на_картинку_премиума.jpg" 
    )

# 2. Подтверждаем, что мы готовы принять платеж
@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    # Тут можно было бы проверить, не купил ли юзер уже подписку,
    # но мы просто подтверждаем сделку
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# 3. Платеж прошел успешно!
@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    # Выдаем Premium в базе данных
    await set_user_premium(message.from_user.id, is_premium=True)
    
# Благодарим пользователя
    await message.answer(
        "✨ <b>Тайные знания открыты!</b>\n\n"
        "Оплата успешно получена. Теперь ты Premium-пользователь Селесты.\n"
        "Тебе доступны все колоды, глубокие расклады и возможность задать картам свой личный вопрос. "
        "Пусть звезды благоволят тебе! 🌌"
    )