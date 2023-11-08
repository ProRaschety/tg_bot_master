from dataclasses import dataclass
from environs import Env


def check_sub_admin(user_id):
    """_summary_

    Args:
        user_id (_type_): _description_

    Returns:
        _type_: _description_
    """
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
