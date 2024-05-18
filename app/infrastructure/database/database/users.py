import logging
from datetime import datetime

from asyncpg import Connection

from app.infrastructure.database.models.users import UsersModel
from app.tg_bot.models.role import UserRole

logger = logging.getLogger(__name__)


class _UsersDB:
    __table_name__ = "users"

    def __init__(self, connect: Connection):
        self.connect = connect

    async def create_table(self) -> None:
        # async with self.connect.transaction():
        await self.connect.execute('''
            CREATE TABLE IF NOT EXISTS users(
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL UNIQUE,
                created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                language VARCHAR(10),
                is_alive BOOLEAN NOT NULL,
                is_blocked BOOLEAN NOT NULL,
                role VARCHAR(20) NOT NULL,
                role_update TIMESTAMP NOT NULL DEFAULT NOW(),
                promocode VARCHAR(20)
            );
        ''')
        logger.info("Created table '%s'", self.__table_name__)

    async def add(
            self,
            *,
            user_id: int,
            language: str,
            is_alive: bool = True,
            is_blocked: bool = False,
            role: UserRole
    ) -> None:

        # async with self.connect.transaction():
        await self.connect.execute('''
            INSERT INTO users(user_id, language, is_alive, is_blocked, role, role_update)
            VALUES($1, $2, $3, $4, $5, $6) ON CONFLICT DO NOTHING;
        ''', user_id, language, is_alive, is_blocked, role, datetime.utcnow()
                                   )

        logger.info(
            "User added. db='%s', user_id=%d, date_time='%s', "
            "language='%s', is_alive=%s, is_blocked=%s, role=%s, date_time='%s'",
            self.__table_name__, user_id, datetime.utcnow(), language,
            is_alive, is_blocked, role, datetime.utcnow()
        )

    async def update(
            self,
            *,
            user_id: int,
            role: UserRole,
            # role_update: datetime.utcnow()
    ) -> None:
        role_update = datetime.utcnow()
        # async with self.connect.transaction():
        await self.connect.execute('''
            UPDATE users SET role = $1, role_update=$2 WHERE user_id = $3;
        ''', role, datetime.utcnow(), user_id
                                   )
        logger.info(
            "User update. db='%s', role=%s, date_time='%s', user_id=%d",
            self.__table_name__, role.value, datetime.utcnow(), user_id
        )

    async def update_promocode(
            self,
            *,
            user_id: int,
            promocode: str,
    ) -> None:
        # async with self.connect.transaction():
        await self.connect.execute('''
            UPDATE users SET promocode = $1 WHERE user_id = $2;
        ''', promocode, user_id
                                   )
        logger.info(
            "User update. db='%s', promocode=%s, date_time='%s', user_id=%d",
            self.__table_name__, promocode, datetime.utcnow(), user_id
        )

    async def delete(self, *, user_id: int) -> None:
        # async with self.connect.transaction():
        await self.connect.execute('''
                DELETE FROM users WHERE user_id = $1;
            ''', user_id
                                   )
        logger.info(
            "User deleted. db='%s', user_id='%d'", self.__table_name__, user_id
        )

    async def get_user_record(self, *, user_id: int) -> UsersModel | None:
        # async with self.connect.transaction():
        cursor = await self.connect.cursor('''
            SELECT id,
                user_id,
                created,
                language,
                is_alive,
                is_blocked,
                role,
                role_update,
                promocode
            FROM users
            WHERE users.user_id = $1
        ''', user_id
                                           )
        data = await cursor.fetchrow()
        return UsersModel(**data) if data else None
