import logging

# import numpy as np
import math as m
from scipy.constants import physical_constants

log = logging.getLogger(__name__)


def get_property_fuel(subst: str):
    """Возвращает свойства горючего. Нужно получать из БД"""
    if subst == 'gasoline':
        molar_mass = 95
        boiling_point = 115
        m = 0.06
    elif subst == 'diesel':
        boiling_point = 380
        molar_mass = 230
        m = 0.04
    elif subst == 'LNG':
        boiling_point = -163
        molar_mass = 16.7
        m = 0.08
    elif subst == 'LPG':
        boiling_point = -50
        molar_mass = 30.068
        m = 0.10
    elif subst == 'liq_hydrogen':
        boiling_point = -252.87
        molar_mass = 0.002016
        m = 0.17
    return molar_mass, boiling_point, m


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


def compute_density_vapor_at_boiling(molar_mass: int | float, boiling_point: int | float):
    V = physical_constants.get(
        'molar volume of ideal gas (273.15 K, 101.325 kPa)')[0]  # 0.02241396954 m^3 mol^-1
    return molar_mass / ((V * 1000) * ((boiling_point + 273.15)/273.15))
