from dataclasses import dataclass, field
from datetime import datetime

from app.infrastructure.database.models.base import BaseModel


@dataclass
class ClimateModel(BaseModel):
    # id: int
    # regionid: int
    region: str
    city: str
    # longitude: float
    # latitude: float
    cwind: int | float
    pwinde: int | float
    pwindn: int | float
    pwindne: int | float
    pwindnw: int | float
    pwinds: int | float
    pwindse: int | float
    pwindsw: int | float
    pwindw: int | float
    temperature: int | float
    windvelocity: int | float


@dataclass
class ClimateRegion(BaseModel):
    region: dict[str, str] = field(default_factory=dict)
