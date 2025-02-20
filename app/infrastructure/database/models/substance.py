import logging

from dataclasses import dataclass
# from typing import NamedTuple

from app.infrastructure.database.models.base import BaseModel
# from pydantic import validator

log = logging.getLogger(__name__)


@dataclass
class SubstanceModel(BaseModel):
    id: int | None = None
    substance_name: str | None = None
    description: str | None = None
    data_source: str | None = None
    density: float = 0
    molar_mass: float = 0
    boiling_point: float = 0
    mass_burning_rate: float = 0
    heat_of_combustion: float = 44000  # Дж
    lower_flammability_limit: float = 0
    upper_flammability_limit: float = 0
    class_fuel: int = 1
    # beta
    correction_parameter: float = 1.0
    # коэффициент участия горючего во взрыве Z
    coefficient_participation_in_explosion: float = 0.1

    def __post_init__(self):
        self.density = float(self.density)
        self.molar_mass = float(self.molar_mass)
        self.boiling_point = float(self.boiling_point)
        self.mass_burning_rate = float(self.mass_burning_rate)
        self.heat_of_combustion = float(self.heat_of_combustion)
        self.lower_flammability_limit = float(self.lower_flammability_limit)
        self.upper_flammability_limit = float(self.upper_flammability_limit)
        self.class_fuel = int(self.class_fuel)
        self.correction_parameter = float(self.correction_parameter)
        self.coefficient_participation_in_explosion = float(
            self.coefficient_participation_in_explosion)


@dataclass
class FlammableMaterialModel(BaseModel):
    substance_name: str | None | None = None
    description: str | None | None = None
    data_source: str | None = None
    combustibility: str | None = None
    density: float = 0
    conductivity: float = 0
    emissivity: float = 0
    specific_heat: float = 0
    absorption_coefficient: float = 0
    lower_heat_of_combustion: float = 0
    linear_flame_velocity: float = 0
    specific_burnout_rate: float = 0
    smoke_forming_ability: float = 0
    oxygen_consumption: float = 0
    carbon_dioxide_output: float = 0
    carbon_monoxide_output: float = 0
    hydrogen_chloride_output: float = 0
    substance_type: str | None = None
    molecular_weight: float = 0
    combustion_efficiency: float = 0
    critical_heat_flux: float = 8.0

    def __post_init__(self):
        self.density = float(self.density)
        self.conductivity = float(self.conductivity)
        self.emissivity = float(self.emissivity)
        self.specific_heat = float(self.specific_heat)
        self.absorption_coefficient = float(self.absorption_coefficient)
        self.lower_heat_of_combustion = float(self.lower_heat_of_combustion)
        self.linear_flame_velocity = float(self.linear_flame_velocity)
        self.specific_burnout_rate = float(self.specific_burnout_rate)
        self.smoke_forming_ability = float(self.smoke_forming_ability)
        self.oxygen_consumption = float(self.oxygen_consumption)
        self.carbon_dioxide_output = float(self.carbon_dioxide_output)
        self.carbon_monoxide_output = float(self.carbon_monoxide_output)
        self.hydrogen_chloride_output = float(self.hydrogen_chloride_output)
        self.molecular_weight = float(self.molecular_weight)
        self.combustion_efficiency = float(self.combustion_efficiency)
        self.critical_heat_flux = float(self.critical_heat_flux)
