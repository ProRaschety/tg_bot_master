from asyncpg import Connection

from app.infrastructure.database.database.users import _UsersDB
from app.infrastructure.database.database.promocode import _PromocodeDB
from app.infrastructure.database.database.climate import _ClimateDB

# все таблицы которые создаются


class DB:
    def __init__(self, connect: Connection) -> None:
        self.users = _UsersDB(connect=connect)
        self.promocode = _PromocodeDB(connect=connect)
        self.climate_tables = _ClimateDB(connect=connect)
