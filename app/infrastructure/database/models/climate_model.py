from dataclasses import dataclass
from datetime import datetime

from app.infrastructure.database.models.base import BaseModel


@dataclass
class ClimateModel(BaseModel):
    id: int
    region_id: int
    region: str
    city_id: int
    city: str
    longitude: float
    latitude: float
    pwindn: float
    pwindne: float
    pwinde: float
    pwindse: float
    pwinds: float
    pwindsw: float
    pwindw: float
    pwindnw: float
    cwind: float
    windvelocity: float
    temperature: float
