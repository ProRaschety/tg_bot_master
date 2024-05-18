import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.enums import ParseMode
# from aiogram.utils.i18n import ConstI18nMiddleware, I18n

from fluentogram import TranslatorHub

from app.infrastructure.database.utils.connect_to_pg import get_pg_pool
from app.infrastructure.database.utils.create_tables import create_tables
from app.infrastructure.cash.utils.connect_to_redis import get_redis_storage
from app.tg_bot.utilities.i18n import create_translator_hub
from app.tg_bot.config.config import Config, load_config
from app.tg_bot.middlewares.database import DataBaseMiddleware
from app.tg_bot.middlewares.role_mv import RoleMiddleware
from app.tg_bot.middlewares.i18n import TranslatorRunnerMiddleware
from app.tg_bot.set_menu import set_main_menu
from app.tg_bot.handlers.owner import owner_router
from app.tg_bot.handlers.admin import admin_router
from app.tg_bot.handlers.user import user_router
from app.tg_bot.handlers.fire_res import fire_res_router
from app.tg_bot.handlers.fire_risk import fire_risk_router
from app.tg_bot.handlers.fire_category import fire_category_router
from app.tg_bot.handlers.data_base_req import data_base_req_router
from app.tg_bot.handlers.handbooks import handbooks_router
from app.tg_bot.handlers.tools import tools_router
from app.tg_bot.handlers.fire_accident import fire_accident_router
from app.tg_bot.handlers.fds_tools import fds_tools_router
from app.tg_bot.handlers.other import other_router


log = logging.getLogger(__name__)


async def main():
    # Выводим в консоль информацию о начале запуска бота
    log.info('Starting bot')

    config: Config = load_config()

    storage: RedisStorage = get_redis_storage(db=config.redis.database,
                                              host=config.redis.host,
                                              port=config.redis.port,
                                              username=config.redis.username,
                                              password=config.redis.password)

    bot = Bot(token=config.tg_bot.token,
              parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=storage)

    translator_hub: TranslatorHub = create_translator_hub()

    db_pool = await get_pg_pool(
        db_name=config.pg.db_name,
        host=config.pg.host,
        port=config.pg.port,
        user=config.pg.username,
        password=config.pg.password
    )

    async with db_pool.acquire() as connect:
        try:
            await create_tables(connect)
        except Exception as e:
            log.exception(e)
            await db_pool.close()

    log.debug('Include routers')

    # Регистриуем роутеры в диспетчере
    dp.include_router(owner_router)
    dp.include_router(admin_router)
    dp.include_router(user_router)
    dp.include_router(fire_res_router)
    dp.include_router(fire_risk_router)
    dp.include_router(fire_category_router)
    dp.include_router(handbooks_router)
    dp.include_router(tools_router)
    dp.include_router(data_base_req_router)
    dp.include_router(fire_accident_router)
    dp.include_router(fds_tools_router)
    dp.include_router(other_router)

    # i18n = I18n(path="locales", default_locale="ru", domain="i18n_example_bot")

    dp.update.middleware(DataBaseMiddleware())
    dp.update.middleware(RoleMiddleware())
    # dp.update.middleware(ConstI18nMiddleware(locale='en', i18n=i18n))
    dp.update.middleware(TranslatorRunnerMiddleware())

    # пропускаем накопившиеся апдейты, настраиваем Меню и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await set_main_menu(bot)
    await dp.start_polling(bot, _translator_hub=translator_hub, _db_pool=db_pool)
