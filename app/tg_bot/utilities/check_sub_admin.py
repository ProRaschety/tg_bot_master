from aiogram import Bot
from environs import Env


async def check_sub_admin(bot: Bot, path: str | None = None, user_id: int = None):
    env = Env()
    env.read_env(path)
    CHANNEL_ID = list(map(int, env.list('CHANNEL_IDS')))

    for ID in CHANNEL_ID:
        user = await bot.get_chat_member(chat_id=ID, user_id=user_id)
        if user.status in ['administrator', 'creator']:
            continue
        else:
            return False
    return True
