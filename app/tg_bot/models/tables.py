import logging

from typing import Any
from dataclasses import dataclass, field, InitVar, FrozenInstanceError, asdict, astuple


@dataclass
class DataFrameModel:
    label: str = None
    headers: list[str] = None
    dataframe: list[list[str | Any]] = None
