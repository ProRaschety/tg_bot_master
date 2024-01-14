from aiogram import Bot
from environs import Env

from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.tg_bot.models.role import UserRole


class IsOwner(BaseFilter):
    async def __call__(self, message: Message, role: UserRole) -> bool:
        return role in (UserRole.OWNER)


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message, role: UserRole) -> bool:
        return role in (UserRole.ADMIN, UserRole.OWNER)


class IsComrade(BaseFilter):
    async def __call__(self, message: Message, role: UserRole) -> bool:
        return role in (UserRole.COMRADE, UserRole.ADMIN, UserRole.OWNER)


class IsSubscriber(BaseFilter):
    async def __call__(self, message: Message, role: UserRole) -> bool:
        # все кто не ниже subscriber
        return role in (UserRole.SUBSCRIBER, UserRole.COMRADE, UserRole.ADMIN, UserRole.OWNER)


class IsGuest(BaseFilter):
    async def __call__(self, message: Message, role: UserRole) -> bool:
        return role in (UserRole.GUEST, UserRole.SUBSCRIBER, UserRole.COMRADE, UserRole.ADMIN, UserRole.OWNER)
