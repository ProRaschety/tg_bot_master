from dataclasses import dataclass

from app.infrastructure.database.models.base import BaseModel


@dataclass
class FCPremisesModel(BaseModel):
    id: int
    area: int | float
    category: str
    efs: bool
