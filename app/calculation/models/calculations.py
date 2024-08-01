import logging

from dataclasses import dataclass, field, InitVar
# from datetime import datetime
# from enum import Enum

from app.infrastructure.database.models.substance import FlammableMaterialModel
from app.infrastructure.database.models.substance import SubstanceModel

log = logging.getLogger(__name__)


@dataclass
class FireRiskAssessment:
    pass


@dataclass
class AccidentModel:
    # общие св-ва для всех событий
    description: str = None
    substance_state: str = None
    substance_name: str = None
    air_temperature: float = 20
    fuel_temperature: float = 20
    velocity_wind: float = 0
    distance: float = 30
    evaporation_duration: float = 3600
    liquid_spill_radius: float = 1.0
    methodology: str = 'methodology_404'

    # для пожара-вспышки
    mass_vapor_fuel: float = 10

    # для пожара-пролива
    pool_area: float = 100
    pool_distance: float = 30

    # для огненного шара
    fire_ball_sep: float = 350.0
    fire_ball_height_center: float = 0
    fire_ball_mass_fuel: float = 10000
    fire_ball_distance: float = 30
    # data.setdefault("accident_fire_ball_existence_time", "10")
    # data.setdefault("accident_fire_ball_atmospheric_transmittance", "1")

    # для взрыва сосуда в очаге пожара
    bleve_mass_fuel: float = 1000.0
    bleve_temperature_liquid_phase: float = 293.0
    bleve_energy_fraction: float = 0.5
    bleve_heat_capacity_liquid_phase: float = 2000
    bleve_distance: float = 30
    # data.setdefault("accident_bleve_overpressure_on_30m", "5.0")
    # data.setdefault("accident_bleve_impuls_on_30m", "15.0")

    # для взрыва ТВС
    class_space: int = 1
    explosion_condition: str = 'above_surface'
    explosion_state_fuel: str = 'gas'
    explosion_stc_coef_oxygen: float = 9.953
    explosion_mass_fuel: float = 1000.0
    explosion_distance: float = 30

    # для факельного горения
    jet_mass_rate: float = 5
    jet_state_fuel: str = 'jet_state_liquid'

    # для факельного сжигания газа
    flare_mass_rate: float = 5

    # для запросов из БД
    substance: SubstanceModel = None

    results: dict = None

    def __post_init__(self):
        self.air_temperature = float(self.air_temperature)
        self.fuel_temperature = float(self.fuel_temperature)
        self.velocity_wind = float(self.velocity_wind)
        self.distance = float(self.distance)
        self.evaporation_duration = float(self.evaporation_duration)
        self.liquid_spill_radius = float(self.liquid_spill_radius)
        self.mass_vapor_fuel = float(self.mass_vapor_fuel)
        self.pool_area = float(self.pool_area)
        self.pool_distance = float(self.pool_distance)
        self.fire_ball_sep = float(self.fire_ball_sep)
        self.fire_ball_height_center = float(self.fire_ball_height_center)
        self.fire_ball_mass_fuel = float(self.fire_ball_mass_fuel)
        self.fire_ball_distance = float(self.fire_ball_distance)
        self.bleve_mass_fuel = float(self.bleve_mass_fuel)
        self.bleve_temperature_liquid_phase = float(
            self.bleve_temperature_liquid_phase)
        self.bleve_energy_fraction = float(self.bleve_energy_fraction)
        self.bleve_heat_capacity_liquid_phase = float(
            self.bleve_heat_capacity_liquid_phase)
        self.bleve_distance = float(self.bleve_distance)
        self.class_space = int(self.class_space)
        self.jet_mass_rate = float(self.jet_mass_rate)
        self.flare_mass_rate = float(self.flare_mass_rate)
        self.explosion_stc_coef_oxygen = float(self.explosion_stc_coef_oxygen)
        self.explosion_mass_fuel = float(self.explosion_mass_fuel)
        self.explosion_distance = float(self.explosion_distance)
        # self. = float(self.)
        if isinstance(self.substance, dict):
            self.substance = SubstanceModel(**self.substance)


@dataclass
class SectionModel:
    section_length: float = 1
    section_width: float = 1
    share_fire_load_area: float = 1
    distance_to_ceiling: float = 0
    distance_to_section: float = 0
    section_area: float = 0
    material: list = field(
        init=True, default_factory=list[FlammableMaterialModel])
    mass: list = field(init=True, default_factory=list)

    def __post_init__(self):
        self.section_length = float(self.section_length)
        self.section_width = float(self.section_width)
        # self.section_area = self.section_length * self.section_width

        if isinstance(self.material, dict):
            self.material.append(FlammableMaterialModel(**self.material))
        if isinstance(self.material, list):
            for m in self.material:
                # print(m)
                for n in m:
                    self.material.append(FlammableMaterialModel(**n))

        # if self.material:
        #     self.material = [FlammableMaterialModel(**self.material)]
        # else:
        #     self.material = [FlammableMaterialModel()]

        # if self.mass is not None and isinstance(self.mass, int) or isinstance(self.mass, float):
        #     self.mass = [self.mass]
        # else:
        #     self.mass = self.mass


@dataclass
class RoomModel:
    height: float = 3
    width: float = 0
    length: float = 0
    area: float = 0
    air_temperature: float = 20
    air_changes_per_hour: int = 0
    leakage_factor_room: int = 0
    volume: float = 0
    free_volume_fraction: float = 0
    # free_volume_fraction: float = field(init=False)
    sections: list = field(default_factory=list[SectionModel])

    def __post_init__(self):
        self.height = float(self.height)
        self.width = float(self.width)
        self.length = float(self.length)
        self.area = float(self.area)
        self.air_temperature = float(self.air_temperature)
        self.air_changes_per_hour = int(self.air_changes_per_hour)
        self.leakage_factor_room = int(self.leakage_factor_room)
        self.volume = float(self.volume)
        self.free_volume_fraction = float(self.free_volume_fraction)

        if isinstance(self.sections, dict):
            self.sections.append(SectionModel(**self.sections))

        if isinstance(self.sections, list):
            for d in self.sections:
                self.sections.append(SectionModel(**d))

        # if isinstance(self.sections, dict):
        #     print('################')
        #     self.sections = [SectionModel(**self.sections)]


# def from_dict(data: dict) -> RoomModel:
#     sections = [
#         SectionModel(
#             distance_to_ceiling=section['distance_to_ceiling'],
#             distance_to_section=section['distance_to_section'],
#             mass=section['mass'],
#             material=[
#                 FlammableMaterialModel(**material) for material in section['material']
#             ],
#             section_area=section['section_area'],
#             section_length=section['section_length'],
#             section_width=section['section_width'],
#             share_fire_load_area=section['share_fire_load_area']
#         ) for section in data['sections']
#     ]

#     return RoomModel(
#         air_changes_per_hour=data['air_changes_per_hour'],
#         air_temperature=data['air_temperature'],
#         area=data['area'],
#         free_volume_fraction=data['free_volume_fraction'],
#         height=data['height'],
#         leakage_factor_room=data['leakage_factor_room'],
#         length=data['length'],
#         sections=sections
#     )
