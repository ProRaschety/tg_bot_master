from dataclasses import dataclass, field, InitVar, FrozenInstanceError

from app.infrastructure.database.models.base import BaseModel
from app.infrastructure.database.models.substance import FlammableMaterialModel


@dataclass
class ModelSection:
    material: list = field(
        init=False, default_factory=list[FlammableMaterialModel])
    mass: list = field(init=False, default_factory=list[int | float])
    length: float = 0
    width: float = 0
    area: float = 0
    share_fire_load_area: float = 1
    distance_to_ceiling: float = 0
    distance_to_section: float = 0


@dataclass
class ModelRoom:
    height: int | float
    area: int | float = 0
    air_changes_per_hour: int = 0
    leakage_factor_room: int = 0
    length: float = field(init=False, default=None)
    width: float = field(init=False, default=None)
    volume: float = field(init=False, default=None)
    free_volume_fraction: float = field(init=False)
    sections: list = field(init=False, default_factory=list[ModelSection])

    def __post_init__(self):
        if self.volume == None:
            self.volume = self.area * self.height
        if self.length == None:
            self.length = (self.volume / self.height) * 0.5
        if self.width == None:
            self.width = (self.volume / self.height) * 0.5
        self.free_volume_fraction = 0.8 * self.volume

    # def compute_area(self, area):
    #     print(f'area: {area}')
    #     if self.area == 0:
    #         print(f'area1 : {area}')
    #         area = []
    #         for sec in self.sections:
    #             print(f'sec: {sec}')
    #             area.append(sec.lenght * sec.width)
    #         self.area = sum(area)
    #     else:
    #         print(f'area: {self.area}')
    #         self.area = self.area
