from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.keyboards.admin_kb import get_admin_main_kb, get_cancel_kb
from db.crud import set_user_premium
from config import is_admin

router = Router()

class ManageFSM(StatesGroup):
    waiting_for_id = State()
    waiting_for_days = State()

@router.callback_query(F.data == "admin_manage")
async def start_manage(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    await state.set_state(ManageFSM.waiting_for_id)
    await callback.message.edit_text("Отправь Telegram ID пользователя:", reply_markup=get_cancel_kb())

@router.message(ManageFSM.waiting_for_id)
async def get_user_id(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id) or not message.text.isdigit(): return
    await state.update_data(target_id=int(message.text))
    await state.set_state(ManageFSM.waiting_for_days)
    await message.answer("На сколько дней выдать? (Напиши 0, чтобы забрать подписку)", reply_markup=get_cancel_kb())

@router.message(ManageFSM.waiting_for_days)
async def process_grant_premium(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id) or not message.text.isdigit(): return
    
    days = int(message.text)
    data = await state.get_data()
    target_id = data["target_id"]
    await state.clear()
    
    if days == 0:
        await set_user_premium(target_id, is_premium=False)
        await message.answer(f"✅ Premium снят с пользователя {target_id}.", reply_markup=get_admin_main_kb())
    else:
        await set_user_premium(target_id, is_premium=True, days=days)
        await message.answer(f"✅ Выдан Premium на {days} дней!", reply_markup=get_admin_main_kb())