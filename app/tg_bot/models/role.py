from enum import Enum
from pydantic import BaseModel


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    COMRADE = "comrade"
    SUBSCRIBER = "subscriber"
    GUEST = "guest"


class User(BaseModel):
    username: str
    password: str
    role: UserRole
