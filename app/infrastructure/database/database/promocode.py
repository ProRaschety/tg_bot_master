import logging
from datetime import datetime

from asyncpg import Connection

from app.infrastructure.database.models.promocode_model import PromocodeModel, PromocodeList

log = logging.getLogger(__name__)

promocodes = [
    {'PROMO': 'cobra_tester'},
    {'PROMO': 'fireenginstudent'},
    {'PROMO': 'fireengin2024'},
]


class _PromocodeDB:
    __table_name__ = "promocodes"

    def __init__(self, connect: Connection):
        self.connect = connect

    async def create_table_promocodes(self) -> None:
        async with self.connect.transaction():
            await self.connect.execute('''
                CREATE TABLE IF NOT EXISTS promocodes(
                    id SERIAL PRIMARY KEY,
                    promocode VARCHAR(20) UNIQUE,
                    created TIMESTAMPTZ DEFAULT NOW(),
                    valid_until DATE
                );
            ''')
            log.info("Created table '%s'", self.__table_name__)

    async def update_promocode_start(self) -> None:
        async with self.connect.transaction():
            for promocode in promocodes:
                await self.connect.execute('''
                    INSERT INTO promocodes(promocode, created, valid_until)
                    VALUES($1, $2, $3) ON CONFLICT DO NOTHING;
                ''', promocode['PROMO'], datetime.utcnow(), datetime.utcnow()
                )
                log.info(
                    "Promocode update. db='%s', promocode=%s",
                    self.__table_name__, promocode
                )

    async def add_promocode(
            self,
            *,
            promocode: str
    ) -> None:
        async with self.connect.transaction():
            await self.connect.execute('''
                INSERT INTO promocodes(promocode, created, valid_until)
                VALUES($1, $2, $3) ON CONFLICT DO NOTHING;
            ''', promocode, datetime.utcnow(), datetime.utcnow()
                                       )
            log.info(
                "Promocode added. db='%s', promocode=%s, date_time='%s'",
                self.__table_name__, promocode, datetime.utcnow()
            )

    async def get_promocode_user(self) -> PromocodeModel | None:
        async with self.connect.transaction():
            cursor = await self.connect.cursor('''
                SELECT id,
                    promocode,
                    created,
                    valid_until
                FROM promocodes;
            '''
                                               )
            data = await cursor.fetchrow()
            return PromocodeModel(*data) if data else None

    async def get_promocode_list(self) -> PromocodeList | None:
        async with self.connect.transaction():
            cursor = await self.connect.cursor('''
                SELECT *
                FROM promocodes;
            '''
                                               )
            data = await cursor.fetch(50)
            # return PromocodeList(data) if data else None
            return data

    async def get_valid_promocode_user(self, promocode: str) -> bool:
        async with self.connect.transaction():
            cursor = await self.connect.cursor('''
                SELECT COUNT(DISTINCT promocode)
                FROM promocodes
                WHERE promocode = $1;
            ''', promocode
                                               )
            data = await cursor.fetchrow()
            # log.info(data)
            return data

    async def delete(self) -> None:
        async with self.connect.transaction():
            await self.connect.execute('''
                    DELETE FROM promocodes;
                '''
                                       )
            log.info(
                "Promocodes clear. db='%s'", self.__table_name__
            )

    # async def get_promocode_user(self, *, promocode: str) -> PromocodeModel | None:
    #     async with self.connect.transaction():
    #         cursor = await self.connect.cursor('''
    #             SELECT id,
    #                 promocode,
    #                 created,
    #                 valid_until
    #             FROM promocodes
    #             WHERE promocodes.promocode = $1;
    #         ''', promocode
    #                                            )
    #         data = await cursor.fetchrow()
    #         return PromocodeModel(**data) if data else None
