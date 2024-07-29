import logging

from typing import Any
from dataclasses import dataclass, field, InitVar, FrozenInstanceError, asdict, astuple


@dataclass
class DataPlotterModel:
    label: str = None
    x_values: list[str] = None
    y_values: list[str] = None
    x_label: str = None
    y_label: str = None
    plot_label: str = None
    ylim: int | float = None
    ymin: int | float = 0.0
    ylim_tick: bool = False
    add_annotate: bool = False
    text_annotate: list[str] = None
    x_ann: int | float = None
    y_ann: int | float = None
    add_annotate_nd: bool = False
    text_annotate_nd: list[str] = None
    x_ann_nd: int | float = None
    y_ann_nd: int | float = None
    add_legend: bool = False
    loc_legend: int = 1
    add_fill_between: bool = False
    param_fill: int | float = None
    label_fill: str = None
    add_axhline: bool = False
    label_axline: str = None

    # headers: list[str] = None
    # dataframe: list[list[str | Any]]
