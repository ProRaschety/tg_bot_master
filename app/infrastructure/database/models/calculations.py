from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from app.infrastructure.database.models.substance import FlammableMaterialModel
from app.tg_bot.models.role import UserRole
from app.infrastructure.database.models.substance import SubstanceModel


@dataclass
class AccidentModel:
    substance_state: str = None
    substance_name: str = None
    air_temperature: float = 20
    velocity_wind: float = 0
    pool_area: float = 100

    distance: float = 30

    sub: SubstanceModel = None

    def __post_init__(self):
        self.air_temperature = float(self.air_temperature)
        self.velocity_wind = float(self.velocity_wind)
        self.pool_area = float(self.pool_area)
        self.distance = float(self.distance)

        if self.sub == dict:
            self.sub = SubstanceModel(**self.sub)

    # data.setdefault("edit_accident_fire_pool_param", "1")
    # data.setdefault("accident_fire_pool_sub", "gasoline")
    # data.setdefault("accident_fire_pool_molar_mass_fuel", "100")
    # data.setdefault("accident_fire_pool_boiling_point_fuel", "180")
    # data.setdefault("accident_fire_pool_mass_burning_rate", "0.06")
    # data.setdefault("accident_fire_pool_heat_of_combustion", "36000")

    # data.setdefault("accident_fire_pool_temperature", "20")
    # data.setdefault("accident_fire_pool_wind", "0")
    # data.setdefault("accident_fire_pool_pool_area", "314")
    # data.setdefault("accident_fire_pool_distance", "30")
