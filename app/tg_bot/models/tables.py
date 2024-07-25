import logging

from typing import Any
from dataclasses import dataclass, field, InitVar, FrozenInstanceError, asdict, astuple


@dataclass
class DataFrameModel:
    label: str
    headers: list[str]
    dataframe: list[list[str | Any]]
