import logging
from datetime import datetime

from asyncpg import Connection

from app.infrastructure.database.models.climate_model import ClimateModel

log = logging.getLogger(__name__)


class _ClimateDB:
    __table_regions__ = "regions"
    __table_cities__ = "cities"
    __table_climate__ = "climate"

    def __init__(self, connect: Connection):
        self.connect = connect

    async def create_table_regions(self) -> None:
        async with self.connect.transaction():
            await self.connect.execute('''
                CREATE TABLE IF NOT EXISTS regions(
                    id SERIAL PRIMARY KEY,
                    region VARCHAR(30) NOT NULL UNIQUE
                );
            ''')
            log.info("Created table '%s'", self.__table_regions__)

    async def create_table_cities(self) -> None:
        async with self.connect.transaction():
            await self.connect.execute('''
                CREATE TABLE IF NOT EXISTS cities(
                    id SERIAL PRIMARY KEY,
                    regionid INTEGER NOT NULL, I
                    city VARCHAR(30) NOT NULL,
                    longitude VARCHAR(20) NOT NULL,
                    latitude VARCHAR(20) NOT NULL
                );
            ''')
            log.info("Created table '%s'", self.__table_cities__)

    async def create_table_climate(self) -> None:
        async with self.connect.transaction():
            await self.connect.execute('''
                CREATE TABLE IF NOT EXISTS cities(
                    id SERIAL PRIMARY KEY,
                    cityid INTEGER NOT NULL,
                    PWindN REAL NOT NULL,
                    PWindNE REAL NOT NULL,
                    PWindE REAL NOT NULL,
                    PWindSE REAL NOT NULL,
                    PWindS REAL NOT NULL,
                    PWindSW REAL NOT NULL,
                    PWindW REAL NOT NULL,
                    PWindNW REAL NOT NULL,
                    CWind REAL NOT NULL,
                    WindVelocity REAL NOT NULL,
                    Temperature REAL NOT NULL
                );
            ''')
            log.info("Created table '%s'", self.__table_climate__)

    async def get_climate_record(self, *, user_id: int) -> ClimateModel | None:
        async with self.connect.transaction():
            cursor = await self.connect.cursor('''
                SELECT * FROM climate.Cities;
            ''', user_id
                                               )
            data = await cursor.fetchrow()
            return ClimateModel(**data) if data else None
