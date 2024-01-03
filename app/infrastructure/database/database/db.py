from asyncpg import Connection

from app.infrastructure.database.database.users import _UsersDB

# все таблицы которые создаются


class DB:
    def __init__(self, connect: Connection) -> None:
        self.users = _UsersDB(connect=connect)
        # self.subs = _SubDB()
