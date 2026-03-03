import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Импортируем базу данных и наш роутер
from db.database import engine, Base
from bot.handlers.user.start import router as start_router
from bot.handlers.user.tarot import router as tarot_router
from bot.keyboards.set_menu import set_main_menu
from bot.handlers.payments import router as payments_router

# Загружаем переменные из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def init_db():
    """Функция для создания таблиц в базе данных при запуске"""
    async with engine.begin() as conn:
        # Эта строчка сама создаст файл celeste.sqlite3 и все таблицы из models.py
        await conn.run_sync(Base.metadata.create_all)

async def main():
    # Настраиваем логирование, чтобы видеть всё, что происходит под капотом
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    
    # Инициализируем бота. Указываем, что по умолчанию используем HTML-разметку
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Диспетчер — это главный распределитель входящих сообщений
    dp = Dispatcher()
    
    # Подключаем наш роутер с командой /start
    dp.include_router(start_router)
    # Подключаем роутер с командами для расклада Таро
    dp.include_router(tarot_router)

    dp.include_router(payments_router)
    
    # 1. Сначала запускаем базу данных
    await init_db()
    print("База данных успешно инициализирована! 💾")

    # 1.5 Устанавливаем кнопку Menu
    await set_main_menu(bot)
    print("Меню команд успешно установлено! 📋")
    
    # 2. Очищаем старые сообщения (чтобы бот не отвечал на то, что ему писали, пока он был выключен)
    await bot.delete_webhook(drop_pending_updates=True)
    
    # 3. Запускаем бота
    print("Оракул Селеста проснулась и ждет сообщений... 🔮")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        # asyncio.run() - запускает нашу асинхронную функцию main()
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nСелеста уснула. До связи! 🌙")