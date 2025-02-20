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
        self.share_fire_load_area = float(self.share_fire_load_area)
        self.distance_to_ceiling = float(self.distance_to_ceiling)
        self.distance_to_section = float(self.distance_to_section)
        self.section_area = float(self.section_area)


@dataclass
class RoomModel:
    room_height: float = 3
    room_width: float = 0
    room_length: float = 0
    room_area: float = 0
    room_air_temperature: float = 20
    room_air_changes_per_hour: int = 0
    room_leakage_factor: int = 0
    room_volume: float = 0
    room_free_volume_fraction: float = 0
    # free_volume_fraction: float = field(init=False)
    sections: list = field(default_factory=list[SectionModel])

    def __post_init__(self):
        self.room_height = float(self.room_height)
        self.room_width = float(self.room_width)
        self.room_length = float(self.room_length)
        self.room_area = float(self.room_area)
        self.room_air_temperature = float(self.room_air_temperature)
        self.room_air_changes_per_hour = int(self.room_air_changes_per_hour)
        self.room_leakage_factor = int(self.room_leakage_factor)
        self.room_volume = float(self.room_volume)
        self.room_free_volume_fraction = float(self.room_free_volume_fraction)


def from_dict(data: dict) -> RoomModel:
    sections = [
        SectionModel(
            distance_to_ceiling=section['distance_to_ceiling'],
            distance_to_section=section['distance_to_section'],
            mass=section['mass'],
            material=[
                FlammableMaterialModel(**material) for material in section['material']
            ],
            section_area=section['section_area'],
            section_length=section['section_length'],
            section_width=section['section_width'],
            share_fire_load_area=section['share_fire_load_area']
        ) for section in data['sections']
    ]

    return RoomModel(
        room_air_changes_per_hour=data['room_air_changes_per_hour'],
        room_air_temperature=data['room_air_temperature'],
        room_area=data['room_area'],
        room_free_volume_fraction=data['room_free_volume_fraction'],
        room_height=data['room_height'],
        room_leakage_factor=data['room_leakage_factor'],
        room_length=data['room_length'],
        sections=sections
    )
