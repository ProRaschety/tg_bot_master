import logging
from datetime import datetime

from asyncpg import Connection

from app.infrastructure.database.models.substance import FlammableMaterialModel

log = logging.getLogger(__name__)


class _FlammableMaterial:
    __table_flammable_materials__ = "flammable_material"

    def __init__(self, connect: Connection):
        self.connect = connect

    async def create_table_flammable_materials(self) -> None:
        # async with self.connect.transaction():
        await self.connect.execute('''
            CREATE TABLE IF NOT EXISTS flammable_material(
                id SERIAL PRIMARY KEY,
                substance_name VARCHAR(50) NOT NULL
                description VARCHAR(50) NOT NULL
                data_source VARCHAR(50) NOT NULL
                combustibility VARCHAR(50) NOT NULL
                density REAL
                conductivity REAL
                emissivity REAL
                specific_heat REAL
                absorption_coefficient REAL
                lower_heat_of_combustion REAL
                linear_flame_velocity REAL
                specific_burnout_rate REAL
                smoke_forming_ability REAL
                oxygen_consumption REAL
                carbon_dioxide_output REAL
                carbon_monoxide_output REAL
                hydrogen_chloride_output REAL
                substance_type VARCHAR(50) NOT NULL
                molecular_weight REAL
                combustion_efficiency REAL
                critical_heat_flux REAL
            );
        ''')
        log.info("Created table '%s'", self.__table_flammable_materials__)
