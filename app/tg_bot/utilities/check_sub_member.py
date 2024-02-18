import os
from aiogram import Bot


async def check_sub_member(bot: Bot, user_id: int = None):
    for ID in list(map(int, os.getenv("CHANNEL_IDS").split(","))):
        user = await bot.get_chat_member(chat_id=ID, user_id=user_id)
        if user.status in ['member', 'administrator', 'creator']:
            continue
        else:
            return False
    return True
