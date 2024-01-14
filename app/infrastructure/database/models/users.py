from dataclasses import dataclass
from datetime import datetime

from app.infrastructure.database.models.base import BaseModel
from app.tg_bot.models.role import UserRole


@dataclass
class UsersModel(BaseModel):
    id: int
    user_id: int
    created: datetime
    language: str
    is_alive: bool
    is_blocked: bool
    role: UserRole
