import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto

from bot.keyboards.inline import get_tarot_spreads_kb
from services.tarot_engine import draw_cards
from data.tarot_deck import SPREADS

router = Router()

# Ловим текстовое сообщение с клавиатуры или команду из меню
@router.message(F.text == "🔮 Расклад Таро")
@router.message(F.command("tarot"))
async def tarot_menu(message: Message):
    await message.answer(
        "Карты готовы говорить с тобой. 🃏\n\n"
        "Выбери, какой расклад ты хочешь сделать сегодня:",
        reply_markup=get_tarot_spreads_kb()
    )

# Ловим нажатия на инлайн-кнопки (всё, что начинается с tarot_spread_)
@router.callback_query(F.data.startswith("tarot_spread_"))
async def process_tarot_spread(callback: CallbackQuery):
    # Достаем ID расклада (например, "cards_3")
    spread_id = callback.data.replace("tarot_spread_", "")
    spread_info = SPREADS.get(spread_id)

    if not spread_info:
        await callback.answer("Упс! Карты рассыпались. Попробуй еще раз.", show_alert=True)
        return
    
    # СЕНЬОРСКАЯ ЗАГЛУШКА НА БУДУЩЕЕ: Проверка Premium
    if spread_info["is_premium"]:
        await callback.answer(
            "👑 Этот расклад — тайное знание. Оно доступно только по Premium подписке!", 
            show_alert=True
        )
        return

    # 1. Даем юзеру понять, что процесс пошел (меняем текст сообщения)
    await callback.message.edit_text(f"⏳ <i>Тасую колоду для расклада «{spread_info['name']}»...</i>")
    
    # Имитируем небольшую задержку для реализма "тасования"
    await asyncio.sleep(1.5)
    
    # 2. Тянем карты с помощью нашего движка
    cards = draw_cards(spread_info["cards_count"])
    
    # 3. Готовим картинки для отправки (Группируем их в альбом)
    media = []
    for card in cards:
        # FSInputFile берет файл прямо с твоего жесткого диска
        media.append(InputMediaPhoto(media=FSInputFile(card["image_path"])))
        
    # 4. Формируем текст ответа
    text_result = f"🔮 <b>Твой расклад: {spread_info['name']}</b>\n\n"
    for i, card in enumerate(cards, 1):
        text_result += f"Карта {i}: <b>{card['full_name']}</b>\n"
        
    text_result += "\n<i>(Здесь Селеста скоро напишет свою подробную трактовку от нейросети...)</i>"

    # 5. Отправляем альбом с картами и следом текст
    await callback.message.answer_media_group(media=media)
    await callback.message.answer(text_result)
    
    # Обязательно "закрываем" callback, чтобы часики на кнопке пропали
    await callback.answer()