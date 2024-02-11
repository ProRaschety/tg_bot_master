from dataclasses import dataclass, field
from datetime import datetime, date

from app.infrastructure.database.models.base import BaseModel


@dataclass
class PromocodeModel(BaseModel):
    id: int
    promocode: str
    # created: datetime
    # valid_until: date


@dataclass
class PromocodeList(BaseModel):
    promocode: list[str] = field(default_factory=list)
    # promocode: list[promocode.value]
