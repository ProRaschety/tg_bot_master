import logging

# import numpy as np
import math as m
from scipy.constants import physical_constants

log = logging.getLogger(__name__)


def compute_characteristic_diameter(area: int | float):
    return m.sqrt((4 * area) / m.pi)


def compute_area_circle(diameter: int | float):
    return (m.pi * diameter ** 2) / 4


def compute_reynolds_number(diameter: int | float, velocity: int | float, kinematic_viscosity: int | float = 1.62 * 10 ** -5):
    # kinematic_viscosity=1.62 * 10 ** -5 кинематическая вязкость воздуха м2 / c = 18.5 * 10 ** -6 Па*с
    return (velocity * diameter) / kinematic_viscosity


def compute_density_gas_phase(molar_mass: int | float, temperature: int | float):
    V = physical_constants.get(
        'molar volume of ideal gas (273.15 K, 101.325 kPa)')[0]  # 0.02241396954 m^3 mol^-1
    return molar_mass / ((V * 1000) * (1 + 0.00367 * temperature))
