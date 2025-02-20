from aiogram import Bot
from aiogram.types import BotCommand


LEXICON_COMMANDS_RU: dict[str, str] = {
    '/start': 'Главное меню',
    '/setlevel': 'Установить уровень доступа',
    # '/help': 'Справка по работе c ботом',
    # '/data_base': 'База данных веществ',
    '/contacts': 'Связь с разработчиком',
    # '/cansel': 'Отмена ввода даных',
    # '/bot_wiki': 'Информация о боте'
}


# Функция для настройки кнопки Menu бота
async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(
            command=command,
            description=description
        ) for command, description in LEXICON_COMMANDS_RU.items()
    ]
    await bot.set_my_commands(main_menu_commands)
