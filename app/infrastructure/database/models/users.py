from dataclasses import dataclass
from datetime import datetime

from app.infrastructure.database.models.base import BaseModel


@dataclass
class UsersModel(BaseModel):
    id: int
    user_id: int
    created: datetime
    language: str
    is_alive: bool
    is_blocked: bool
    is_admin: bool
