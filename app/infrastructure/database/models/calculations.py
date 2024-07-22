import logging

from dataclasses import dataclass, field, InitVar
from datetime import datetime
from enum import Enum

from app.infrastructure.database.models.substance import FlammableMaterialModel
from app.infrastructure.database.models.substance import SubstanceModel

log = logging.getLogger(__name__)


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
    fire_ball_mass_fuel: float = 0
    # data.setdefault("accident_fire_ball_existence_time", "10")
    # data.setdefault("accident_fire_ball_atmospheric_transmittance", "1")

    # для взрыва сосуда в очаге пожара
    bleve_mass_fuel: float = 1000.0
    bleve_temperature_liquid_phase: float = 293.0
    bleve_energy_fraction: float = 0.5
    bleve_heat_capacity_liquid_phase: float = 2000
    # data.setdefault("accident_bleve_overpressure_on_30m", "5.0")
    # data.setdefault("accident_bleve_impuls_on_30m", "15.0")

    # для взрыва ТВС
    class_space: int = 1
    explosion_condition: str = 'above_surface'
    explosion_state_fuel: str = 'gas'
    # data.setdefault("accident_cloud_explosion_stc_coef_oxygen", "9.953")

    # для горизонтального факела
    horizontal_jet_state: str = None

    # для вертикального факела
    jet_mass_rate: float = 5
    vertical_jet_state: str = None

    substance: SubstanceModel = None
    # substance: SubstanceModel = field(
    #     # init=True,
    #     default_factory=SubstanceModel
    # )
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
        self.fire_ball_sep = float(self.fire_ball_sep)
        self.fire_ball_height_center = float(self.fire_ball_height_center)
        self.fire_ball_mass_fuel = float(self.fire_ball_mass_fuel)
        self.bleve_mass_fuel = float(self.bleve_mass_fuel)
        self.bleve_temperature_liquid_phase = float(
            self.bleve_temperature_liquid_phase)
        self.bleve_energy_fraction = float(self.bleve_energy_fraction)
        self.bleve_heat_capacity_liquid_phase = float(
            self.bleve_heat_capacity_liquid_phase)
        self.class_space = int(self.class_space)
        self.jet_mass_rate = float(self.jet_mass_rate)

        if isinstance(self.substance, dict):
            self.substance = SubstanceModel(**self.substance)
