import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub

from app.tg_bot.config.config import Config, load_config
from app.tg_bot.middlewares.i18n import TranslatorRunnerMiddleware
from app.tg_bot.set_menu import set_main_menu
from app.tg_bot.handlers.admin import admin_router
from app.tg_bot.handlers.user import user_router
from app.tg_bot.handlers.fire_res import fire_res_router
from app.tg_bot.handlers.fire_risk import fire_risk_router
from app.tg_bot.handlers.data_base_req import data_base_req_router
from app.tg_bot.handlers.other import other_router

storage = MemoryStorage()  # для хранения вводимой информации в оперативной памяти

logger = logging.getLogger(__name__)


async def main():
    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    config: Config = load_config()

    bot = Bot(token=config.tg_bot.token,
              parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=storage)

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
                    filenames=["locales/ru/user.ftl",
                               "locales/ru/fire_resistance.ftl",
                               "locales/ru/fire_risk.ftl",
                               "locales/ru/admin.ftl",
                               "locales/ru/data_base_subs.ftl",
                               "locales/ru/other.ftl"])),
            FluentTranslator(
                locale="en",
                translator=FluentBundle.from_files(
                    locale="en-US",
                    filenames=["locales/en/user.ftl",
                               "locales/ru/fire_resistance.ftl",
                               "locales/ru/fire_risk.ftl",
                               "locales/ru/admin.ftl",
                               "locales/ru/data_base_subs.ftl",
                               "locales/ru/other.ftl"]))
        ],
    )

    logging.debug('Include routers')

    # Регистриуем роутеры в диспетчере
    dp.include_router(admin_router)
    dp.include_router(user_router)
    dp.include_router(fire_res_router)
    dp.include_router(fire_risk_router)
    dp.include_router(data_base_req_router)
    dp.include_router(other_router)

    dp.update.middleware(TranslatorRunnerMiddleware())

    # пропускаем накопившиеся апдейты, настраиваем Меню и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await set_main_menu(bot)
    await dp.start_polling(bot, _translator_hub=translator_hub)
