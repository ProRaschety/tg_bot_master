import logging

from aiogram.fsm.storage.redis import Redis, RedisStorage

logger = logging.getLogger(__name__)


def get_redis_storage(
    db: str,
    host: str,
    port: int,
    username: str,
    password: str,

) -> RedisStorage:

    redis = Redis(
        host=host,
        port=port,
        db=db,
        username=username,
        password=password
    )

    logger.debug("Connected to Redis")

    return RedisStorage(redis=redis)
