from asyncpg import Connection

from app.infrastructure.database.database.db import DB


async def create_tables(connect: Connection) -> None:
    db = DB(connect)
    await db.users.create_table()
    await db.regions.create_table_regions()
    await db.cities.create_table_cities()
    # await db.climate.create_table_climate()
