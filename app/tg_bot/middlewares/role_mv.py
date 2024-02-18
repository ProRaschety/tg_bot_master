import logging

from typing import Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import Update

from app.infrastructure.database.database.db import DB
from app.tg_bot.utilities.user_role import get_user_role


log = logging.getLogger(__name__)


class RoleMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, any]], Awaitable[None]],
        event: Update,
        data: dict[str, any],
    ) -> any:
        db: DB = data.get('db')
        role = await get_user_role(db=db, event=event, data=data)
        data['role'] = role
        await handler(event, data)
