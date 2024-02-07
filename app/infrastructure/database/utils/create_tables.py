from asyncpg import Connection

from app.infrastructure.database.database.db import DB


async def create_tables(connect: Connection) -> None:
    db = DB(connect)
    await db.users.create_table()
    await db.promocode.create_table_promocodes()
    await db.promocode.add_promocode_start()
    await db.climate_tables.create_table_regions()
    await db.climate_tables.create_table_cities()
    await db.climate_tables.create_table_climate()
    await db.climate_tables.add_regions()
    await db.climate_tables.add_cities()
    await db.climate_tables.add_climates()
