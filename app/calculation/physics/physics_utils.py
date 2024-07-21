import logging
# import asyncio

# import numpy as np
import math as m
from scipy.constants import physical_constants
from scipy.interpolate import RectBivariateSpline, interp1d

log = logging.getLogger(__name__)


async def get_property_fuel(subst: str):
    """Возвращает свойства горючего. Нужно получать из БД"""
    if subst == 'gasoline':
        molar_mass = 95
        boiling_point = 115
        mass_burning_rate = 0.06
        lower_flammability_limit = 1.10  # AN-93-зимний
    elif subst == 'diesel':
        boiling_point = 380
        molar_mass = 230
        mass_burning_rate = 0.04
        lower_flammability_limit = 0.52  # ДТ-"Л"
    elif subst == 'LNG':
        boiling_point = -163
        molar_mass = 16.7
        mass_burning_rate = 0.08
        lower_flammability_limit = 5.28  # Метан
    elif subst == 'LPG':
        boiling_point = -50
        molar_mass = 30.068
        mass_burning_rate = 0.10
        lower_flammability_limit = 2.0  # Пропан
    elif subst == 'liq_hydrogen':
        boiling_point = -252.87
        molar_mass = 0.002016
        mass_burning_rate = 0.17
        lower_flammability_limit = 4.12  # Водород
    else:
        molar_mass = 95
        boiling_point = 115
        mass_burning_rate = 0.06
        lower_flammability_limit = 1.10

    return molar_mass, boiling_point, mass_burning_rate, lower_flammability_limit


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


def compute_stoichiometric_coefficient_with_oxygen(n_C: int | float = 0, n_H: int | float = 0, n_X: int | float = 0, n_O: int | float = 0):
    return n_C + ((n_H - n_X) / 4) - (n_O / 2)


def compute_stoichiometric_coefficient_with_fuel(beta: int | float = 0):
    return 100 / (1 + 4.84 * beta)


def compute_specific_isobaric_heat_capacity_of_air(temperature: int | float):
    data = interp1d([223.15, 228.15, 233.15, 238.15, 243.15, 248.15, 253.15, 258.15, 263.15, 268.15, 273.15, 278.15, 283.15, 288.15, 293.15, 298.15, 303.15, 308.15, 313.15, 318.15, 323.15],
                    [1.0019, 1.0020, 1.00210, 1.00215, 1.0022, 1.0023, 1.0025, 1.0026, 1.0028, 1.0030,
                        1.0031, 1.0032, 1.0034, 1.0036, 1.0038, 1.0040, 1.0043, 1.0046, 1.0049, 1.0053, 1.0057],
                    'linear')  # Изобарная теплоемкость водуха, кДж/(кг*К)
    return data(temperature + 273.15)
