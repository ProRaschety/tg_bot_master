import logging

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from app.infrastructure.database.models.substance import FlammableMaterialModel
from app.tg_bot.models.role import UserRole
from app.infrastructure.database.models.substance import SubstanceModel

log = logging.getLogger(__name__)


@dataclass
class AccidentModel:
    substance_state: str = None
    substance_name: str = None
    air_temperature: float = 20
    velocity_wind: float = 0
    pool_area: float = 100
    distance: float = 30

    substance: SubstanceModel = None
    results: dict = None

    def __post_init__(self):
        self.air_temperature = float(self.air_temperature)
        self.velocity_wind = float(self.velocity_wind)
        self.pool_area = float(self.pool_area)
        self.distance = float(self.distance)

        if self.substance == dict:
            self.substance = SubstanceModel(**self.substance)
