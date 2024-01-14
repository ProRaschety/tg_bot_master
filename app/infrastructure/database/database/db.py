from asyncpg import Connection

from app.infrastructure.database.database.users import _UsersDB
from app.infrastructure.database.database.climate import _ClimateDB

# все таблицы которые создаются


class DB:
    def __init__(self, connect: Connection) -> None:
        self.users = _UsersDB(connect=connect)
        self.regions = _ClimateDB(connect=connect)
        self.cities = _ClimateDB(connect=connect)
        self.climate = _ClimateDB(connect=connect)
        # self.subs = _SubDB()
