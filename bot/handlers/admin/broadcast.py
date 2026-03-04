from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db.admin_crud import get_all_users_ids
from bot.keyboards.admin_kb import get_admin_main_kb, get_cancel_kb
from config import is_admin
import asyncio

router = Router()

class BroadcastFSM(StatesGroup):
    waiting_for_message = State()

@router.callback_query(F.data == "admin_broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    await state.set_state(BroadcastFSM.waiting_for_message)
    await callback.message.edit_text("📢 <b>Отправь пост для рассылки.</b>\nМожно текст с картинкой.", reply_markup=get_cancel_kb())

@router.message(BroadcastFSM.waiting_for_message)
async def process_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await state.clear()
    
    users = await get_all_users_ids()
    await message.answer(f"⏳ Начинаю рассылку для {len(users)} пользователей...")
    
    success = 0
    for user_id in users:
        try:
            await message.copy_to(chat_id=user_id)
            success += 1
            await asyncio.sleep(0.05) # Лимит Telegram
        except Exception: pass # Юзер заблокировал бота
            
    await message.answer(f"✅ Рассылка завершена!\nДоставлено: {success} из {len(users)}", reply_markup=get_admin_main_kb())