import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub

from app.tg_bot.config.config import Config, load_config
from app.tg_bot.handlers.user import user_router
from app.tg_bot.middlewares.i18n import TranslatorRunnerMiddleware
from app.tg_bot.set_menu import set_main_menu

logger = logging.getLogger(__name__)


async def main():
    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    config: Config = load_config()

    bot = Bot(token=config.tg_bot.token,
              parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    translator_hub = TranslatorHub(
        {
            "ru": ("ru", "en"),
            "en": ("ru", "en")
        },
        [
            FluentTranslator(
                locale="ru",
                translator=FluentBundle.from_files(
                    locale="ru-RU",
                    filenames=["locales/ru/txt.ftl"])),
            FluentTranslator(
                locale="en",
                translator=FluentBundle.from_files(
                    locale="en-US",
                    filenames=["locales/en/txt.ftl"]))
        ],
    )

    logging.debug('Include routers')

    # Регистриуем роутеры в диспетчере
    dp.include_router(user_router)

    dp.update.middleware(TranslatorRunnerMiddleware())

    # пропускаем накопившиеся апдейты, настраиваем Меню и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await set_main_menu(bot)
    await dp.start_polling(bot, _translator_hub=translator_hub)
