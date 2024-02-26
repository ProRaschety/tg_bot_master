import logging
import os

from aiogram.types import Update, User

from app.infrastructure.database.database.db import DB
from app.infrastructure.database.models.users import UsersModel
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
            role = UserRole.OWNER.value
        elif await check_sub_admin(bot=bot, user_id=user_id):
            await db.users.add(user_id=user_id, language=user_lang, role=UserRole.ADMIN)
            role = UserRole.ADMIN.value
        elif await check_sub_member(bot=bot, user_id=user_id):
            await db.users.add(user_id=user_id, language=user_lang, role=UserRole.SUBSCRIBER)
            role = UserRole.SUBSCRIBER.value
        else:
            await db.users.add(user_id=user_id, language=user_lang, role=UserRole.GUEST)
            role = UserRole.GUEST.value
    elif user_record:
        role = user_record.role
        if user_id in list(map(int, os.getenv("OWNER_IDS").split(","))):
            if role != UserRole.OWNER.value:
                await db.users.update(role=UserRole.OWNER, user_id=user_id)
                role = UserRole.OWNER.value
        elif await check_sub_admin(bot=bot, user_id=user_id):
            if role != UserRole.ADMIN.value:
                await db.users.update(role=UserRole.ADMIN, user_id=user_id)
                role = UserRole.ADMIN.value
        elif user_record.promocode != None:
            user_promocode = dict(await db.promocode.get_valid_promocode_user(promocode=user_record.promocode))
            if user_promocode.get('count') != 0:
                if role != UserRole.COMRADE.value:
                    await db.users.update(role=UserRole.COMRADE, user_id=user_id)
                    role = UserRole.COMRADE.value
            else:
                if await check_sub_member(bot=bot, user_id=user_id):
                    if role != UserRole.SUBSCRIBER.value:
                        await db.users.update(role=UserRole.SUBSCRIBER, user_id=user_id)
                        role = UserRole.SUBSCRIBER.value
                elif role != UserRole.GUEST.value:
                    await db.users.update(role=UserRole.GUEST, user_id=user_id)
                    role = UserRole.GUEST.value

        elif await check_sub_member(bot=bot, user_id=user_id):
            if role != UserRole.SUBSCRIBER.value:
                await db.users.update(role=UserRole.SUBSCRIBER, user_id=user_id)
                role = UserRole.SUBSCRIBER.value
            else:
                role = user_record.role

        else:
            if role != UserRole.GUEST.value:
                await db.users.update(role=UserRole.GUEST, user_id=user_id)
                role = UserRole.GUEST.value
    else:
        await db.users.add(user_id=user_id, language=user_lang, role=UserRole.GUEST)
        role = UserRole.GUEST.value
        await db.users.update(role=UserRole.GUEST, user_id=user_id)
        role = UserRole.GUEST.value
    log.info(f'Уроень доступа: {role}')
    return role
