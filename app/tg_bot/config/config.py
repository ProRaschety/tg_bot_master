from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str
    owner_ids: list[int]
    admin_ids: list[int]
    channel_ids: list[int]


@dataclass
class PostgresConfig:
    db_name: str
    host: str
    port: int
    username: str
    password: str


@dataclass
class RedisConfig:
    database: int
    host: str
    port: int
    username: str
    password: str
    state_ttl: int
    data_ttl: int


@dataclass
class Config:
    tg_bot: TgBot
    pg: PostgresConfig
    redis: RedisConfig


# def load_config(path: str | None = None) -> Config:
def load_config() -> Config:
    env = Env()
    # env.read_env(path)
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            owner_ids=list(map(int, env.list('OWNER_IDS'))),
            admin_ids=list(map(int, env.list('ADMIN_IDS'))),
            channel_ids=list(map(int, env.list('CHANNEL_IDS')))
        ),
        pg=PostgresConfig(
            db_name=env('POSTGRES_NAME'),
            host=env('POSTGRES_HOST'),
            port=env('POSTGRES_PORT'),
            username=env('POSTGRES_USER'),
            password=env('POSTGRES_PASSWORD')
        ),
        redis=RedisConfig(
            database=env('REDIS_DATABASE'),
            host=env('REDIS_HOST'),
            port=env('REDIS_PORT'),
            username=env('REDIS_USERNAME'),
            password=env('REDIS_PASSWORD'),
            state_ttl=env('REDIS_TTL_STATE'),
            data_ttl=env('REDIS_TTL_DATA'),
        )
    )
