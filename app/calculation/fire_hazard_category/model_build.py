from dataclasses import dataclass

from app.infrastructure.database.models.base import BaseModel


@dataclass
class FCBuildModel(BaseModel):
    id: int
    height: int | float
    category: str
