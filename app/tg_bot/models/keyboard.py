# from typing import Any
from dataclasses import dataclass, field, InitVar, FrozenInstanceError, asdict, astuple


@dataclass
class InlineKeyboardModel:
    width: int = 1
    buttons: str | None = None
    penultimate: str | None = None
    ultimate: str | None = None
    reference: str | None = None
