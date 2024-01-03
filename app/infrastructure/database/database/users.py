import logging
from datetime import datetime

from asyncpg import Connection

from app.infrastructure.database.models.users import UsersModel

logger = logging.getLogger(__name__)


class _UsersDB:
    __table_name__ = "users"

    def __init__(self, connect: Connection):
        self.connect = connect

    async def create_table(self) -> None:
        async with self.connect.transaction():
            await self.connect.execute('''
                CREATE TABLE IF NOT EXISTS users(
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL UNIQUE,
                    created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    language VARCHAR(10),
                    is_alive BOOLEAN NOT NULL,
                    is_blocked BOOLEAN NOT NULL,
                    is_admin BOOLEAN NOT NULL
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
            is_admin: bool = False
    ) -> None:

        async with self.connect.transaction():
            await self.connect.execute('''
                INSERT INTO users(user_id, language, is_alive, is_blocked, is_admin)
                VALUES($1, $2, $3, $4, $5) ON CONFLICT DO NOTHING;
            ''', user_id, language, is_alive, is_blocked, is_admin
                                       )

            logger.info(
                "User added. db='%s', user_id=%d, date_time='%s', "
                "language='%s', is_alive=%s, is_blocked=%s, is_admin=%s",
                self.__table_name__, user_id, datetime.utcnow(), language,
                is_alive, is_blocked, is_admin
            )

    async def delete(self, *, user_id: int) -> None:
        async with self.connect.transaction():
            await self.connect.execute('''
                    DELETE FROM users WHERE user_id = $1;
                ''', user_id
                                       )
            logger.info(
                "User deleted. db='%s', user_id='%d'", self.__table_name__, user_id
            )

    async def get_user_record(self, *, user_id: int) -> UsersModel | None:
        async with self.connect.transaction():
            cursor = await self.connect.cursor('''
                SELECT id,
                    user_id,
                    created,
                    language,
                    is_alive,
                    is_blocked,
                    is_admin
                FROM users
                WHERE users.user_id = $1
            ''', user_id
                                               )
            data = await cursor.fetchrow()
            return UsersModel(**data) if data else None
