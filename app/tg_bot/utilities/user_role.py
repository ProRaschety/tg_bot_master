import logging
import os

from aiogram import BaseMiddleware
from aiogram.types import Update, User

from app.infrastructure.database.database.db import DB
from app.tg_bot.models.role import UserRole

from app.tg_bot.utilities.check_sub_admin import check_sub_admin
from app.tg_bot.utilities.check_sub_member import check_sub_member


log = logging.getLogger(__name__)


async def get_user_role(db: DB, event: Update, data) -> UserRole:
    bot = event.bot
    user: User = data.get('event_from_user')
    user_id = user.id
    user_lang = user.language_code
    user_record: UsersModel = await db.users.get_user_record(user_id=user_id)
    if user_record is None:
        if user_id in list(map(int, os.getenv("OWNER_IDS").split(","))):
            await db.users.add(user_id=user_id, language=user_lang, role=UserRole.OWNER)
            role = UserRole.OWNER
        elif await check_sub_admin(bot=bot, user_id=user_id):
            await db.users.add(user_id=user_id, language=user_lang, role=UserRole.ADMIN)
            role = UserRole.ADMIN
        elif await check_sub_member(bot=bot, user_id=user_id):
            await db.users.add(user_id=user_id, language=user_lang, role=UserRole.SUBSCRIBER)
            role = UserRole.SUBSCRIBER
        else:
            await db.users.add(user_id=user_id, language=user_lang, role=UserRole.GUEST)
            role = UserRole.GUEST
    else:
        role = user_record.role
    log.info(f'role: {role}')
    return role
