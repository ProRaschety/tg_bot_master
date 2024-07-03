from dataclasses import dataclass
# from typing import NamedTuple

from app.infrastructure.database.models.base import BaseModel
# from pydantic import validator


@dataclass
class SubstanceModel(BaseModel):
    id: int = None
    substance_name: str = None
    density: float = 0
    molar_mass: float = 0
    boiling_point: float = 0
    mass_burning_rate: float = 0
    heat_of_combustion: float = 0
    boiling_point: float = 0

    def __post_init__(self):
        self.density = float(self.density)


@dataclass
class FlammableMaterialModel:
    # substance_name: str
    # description: str
    # data_source: str
    # combustibility: str
    # density: float
    # conductivity: float
    # emissivity: float
    # specific_heat: float
    # absorption_coefficient: float
    # lower_heat_of_combustion: float
    # linear_flame_velocity: float
    # specific_burnout_rate: float
    # smoke_forming_ability: float
    # oxygen_consumption: float
    # carbon_dioxide_output: float
    # carbon_monoxide_output: float
    # hydrogen_chloride_output: float
    # substance_type: str
    # molecular_weight: float
    # combustion_efficiency: float
    # critical_heat_flux: float
    substance_name: str = None
    description: str = None
    data_source: str = None
    combustibility: str = None
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
    substance_type: str = None
    molecular_weight: float = 0
    combustion_efficiency: float = 0
    critical_heat_flux: float = 0

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
