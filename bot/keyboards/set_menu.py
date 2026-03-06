from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

async def set_main_menu(bot: Bot):
    """
    Устанавливает кнопку 'Menu' слева от поля ввода.
    """
    main_menu_commands = [
        BotCommand(command='/start', description='🔮 Перезапустить оракула'),
        BotCommand(command='/tarot', description='🃏 Расклад Таро'),
        BotCommand(command='/numerology', description='🔢 Нумерология'),
        BotCommand(command='/horoscope', description='🌟 Гороскоп на день'),
        BotCommand(command='/premium', description='👑 Управление Premium'),
    ]
    
    # Отправляем список команд серверам Telegram
    await bot.set_my_commands(main_menu_commands, BotCommandScopeDefault())