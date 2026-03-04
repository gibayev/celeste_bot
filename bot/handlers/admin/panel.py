from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import is_admin
from db.admin_crud import get_admin_stats
from bot.keyboards.admin_kb import get_admin_main_kb

router = Router()

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id): return # Тихий игнор для не-админов
    await message.answer("👑 <b>Секретная панель управления Оракулом</b>", reply_markup=get_admin_main_kb())

@router.callback_query(F.data == "admin_stats")
async def show_statistics(callback: CallbackQuery):
    if not is_admin(callback.from_user.id): return
        
    stats = await get_admin_stats()
    text = (
        f"📊 <b>Статистика проекта:</b>\n\n"
        f"👥 <b>Аудитория:</b>\n"
        f"Всего пользователей: {stats['total_users']}\n"
        f"Актив за 7 дней: {stats['active_week']}\n"
        f"Актив за 30 дней: {stats['active_month']}\n"
        f"Premium-подписчиков: {stats['premium_users']}\n\n"
        f"💰 <b>Финансы (Звезды):</b>\n"
        f"Оборот всего: {stats['total_stars']} ⭐️ (~${round(stats['total_stars'] * 0.013, 2)})\n"
        f"Оборот за месяц: {stats['month_stars']} ⭐️ (~${round(stats['month_stars'] * 0.013, 2)})"
    )
    await callback.message.edit_text(text, reply_markup=get_admin_main_kb())

# Общая кнопка отмены для любых админских действий
@router.callback_query(F.data == "admin_cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Действие отменено.", reply_markup=get_admin_main_kb())