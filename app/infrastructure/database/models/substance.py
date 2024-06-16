from dataclasses import dataclass
# from typing import NamedTuple

from app.infrastructure.database.models.base import BaseModel
# from pydantic import validator


@dataclass
class SubstanceModel(BaseModel):
    id: int


@dataclass
class FlammableMaterialModel:
    substance_name: str
    description: str
    data_source: str
    combustibility: str
    density: float
    conductivity: float
    emissivity: float
    specific_heat: float
    absorption_coefficient: float
    lower_heat_of_combustion: float
    linear_flame_velocity: float
    specific_burnout_rate: float
    smoke_forming_ability: float
    oxygen_consumption: float
    carbon_dioxide_output: float
    carbon_monoxide_output: float
    hydrogen_chloride_output: float
    substance_type: str
    molecular_weight: float
    combustion_efficiency: float
    critical_heat_flux: float

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
