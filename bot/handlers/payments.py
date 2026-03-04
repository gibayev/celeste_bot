from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from db.crud import get_or_create_user, set_user_premium
from bot.keyboards.inline import get_premium_plans_kb
from datetime import datetime

router = Router()

# 1. Главное меню Premium
@router.message(F.text == "👑 Premium")
@router.message(F.command("premium"))
async def premium_menu(message: Message):
    db_user, _ = await get_or_create_user(
        message.from_user.id, 
        message.from_user.username, 
        message.from_user.full_name
    )
    
    # Формируем статус
    status_text = "❌ <b>Нет активной подписки</b>"
    if db_user.is_premium:
        if db_user.premium_until:
            days_left = (db_user.premium_until - datetime.now()).days
            status_text = f"✅ <b>Подписка активна!</b>\n⏳ Осталось дней: <b>{max(0, days_left)}</b>"
        else:
            status_text = "👑 <b>Подписка активна (Бессрочный доступ)</b>"

    # Единое красивое меню
    text = (
        f"👑 <b>Управление подпиской Premium</b>\n\n"
        f"Текущий статус: {status_text}\n\n"
        f"<b>Что дает Premium-доступ?</b>\n"
        f"🃏 Доступ к закрытым колодам (Таро Тота, Манара).\n"
        f"🌌 Глубокие судьбоносные расклады (Кельтский крест и др.).\n"
        f"✍️ <b>Свой вопрос</b>: возможность описать свою ситуацию текстом и получить персональный расклад от Оракула.\n\n"
        f"Выбери тариф для оформления или продления подписки (скидки до 20%):"
    )
    
    await message.answer(text, reply_markup=get_premium_plans_kb())

# 2. Обработка выбора тарифа (выставление счета)
@router.callback_query(F.data.startswith("buy_premium_"))
async def send_invoice_for_plan(callback: CallbackQuery, bot: Bot):
    # Достаем количество дней из callback_data (например: buy_premium_90)
    days = int(callback.data.split("_")[2])
    
    # Прайс-лист
    prices_map = {
        7: {"amount": 1, "label": "Premium на 1 неделю"},
        30: {"amount": 150, "label": "Premium на 1 месяц"},
        90: {"amount": 400, "label": "Premium на 3 месяца"},
        180: {"amount": 750, "label": "Premium на 6 месяцев"},
        365: {"amount": 1400, "label": "Premium на 1 год"}
    }
    
    plan = prices_map.get(days)
    if not plan:
        return
        
    prices = [LabeledPrice(label=plan["label"], amount=plan["amount"])]
    
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=f"👑 {plan['label']}",
        description="Открой все тайны: премиальные колоды, судьбоносные расклады и свой личный вопрос Оракулу!",
        payload=f"premium_{days}", # Передаем количество дней в payload, чтобы потом знать, сколько начислить
        provider_token="", 
        currency="XTR",
        prices=prices,
    )
    # Убираем "часики" с кнопки
    await callback.answer()

# 3. Подтверждаем готовность принять платеж
@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# 4. Платеж прошел успешно!
@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    # Читаем payload, который мы передали при создании счета (например: premium_90)
    payload = message.successful_payment.invoice_payload
    days_purchased = int(payload.split("_")[1])
    
    # Начисляем дни (если подписка уже была, дни прибавятся!)
    await set_user_premium(message.from_user.id, is_premium=True, days=days_purchased)
    
    await message.answer(
        f"✨ <b>Тайные знания открыты!</b>\n\n"
        f"Оплата успешно получена. Твоя подписка продлена на <b>{days_purchased} дней</b>.\n"
        f"<i>(Официальная квитанция от Telegram сохранена выше в истории чата).</i>\n\n"
        f"Пусть звезды благоволят тебе! 🌌"
    )