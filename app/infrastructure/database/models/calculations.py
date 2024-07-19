import logging

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from app.infrastructure.database.models.substance import FlammableMaterialModel
from app.infrastructure.database.models.substance import SubstanceModel

log = logging.getLogger(__name__)


@dataclass
class AccidentModel:
    # общие св-ва для всех событий
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
    mass_vapor_fuel: float = 100
    # для пожара-пролива
    pool_area: float = 100

    # для огненного шара
    fire_ball_sep: float = 350.0
    fire_ball_height_center: float = None
    fire_ball_mass_fuel: float = None
    # data.setdefault("accident_fire_ball_existence_time", "10")
    # data.setdefault("accident_fire_ball_atmospheric_transmittance", "1")

    # для взрыва сосуда в очаге пожара
    bleve_mass_fuel: float = 1000.0
    bleve_temperature_liquid_phase: float = 293.0
    bleve_energy_fraction: float = 0.5

    # data.setdefault("accident_bleve_heat_capacity_liquid_phase", "2000")
    # data.setdefault("accident_bleve_overpressure_on_30m", "5.0")
    # data.setdefault("accident_bleve_impuls_on_30m", "15.0")

    # для взрыва ТВС
    class_space: float = 1
    explosion_condition: str = 'above_surface'
    explosion_state_fuel: str = 'gas'
    # data.setdefault("accident_cloud_explosion_stc_coef_oxygen", "9.953")

    # для горизонтального факела
    horizontal_jet_state: str = None
    # для вертикального факела
    jet_mass_rate: float = 5
    vertical_jet_state: str = None

    substance: SubstanceModel = None
    results: dict = None


def __post_init__(self):
    self.air_temperature = float(self.air_temperature)
    self.velocity_wind = float(self.velocity_wind)
    self.pool_area = float(self.pool_area)
    self.distance = float(self.distance)

    if self.substance == dict:
        self.substance = SubstanceModel(**self.substance)
