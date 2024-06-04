import logging

# import numpy as np
import math as m
from scipy.constants import physical_constants
from scipy.interpolate import RectBivariateSpline, interp1d

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


def compute_stoichiometric_coefficient_with_oxygen(n_C: int | float = 0, n_H: int | float = 0, n_X: int | float = 0, n_O: int | float = 0):
    return n_C + ((n_H - n_X) / 4) - (n_O / 2)


def compute_stoichiometric_coefficient_with_fuel(beta: int | float = 0):
    return 100 / (1 + 4.84 * beta)


def compute_specific_isobaric_heat_capacity_of_air(temperature: int | float):
    data = interp1d([223.15, 228.15, 233.15, 238.15, 243.15, 248.15, 253.15, 258.15, 263.15, 268.15, 273.15, 278.15, 283.15, 288.15, 293.15, 298.15, 303.15, 308.15, 313.15, 318.15, 323.15],
                    [0.10019, 0.10020, 0.100210, 0.100215, 0.10022, 0.10023, 0.10025, 0.10026, 0.10028, 0.10030,
                        0.10031, 0.10032, 0.10034, 0.10036, 0.10038, 0.10040, 0.10043, 0.10046, 0.10049, 0.10053, 0.10057],
                    'linear')  # Изобарная теплоемкость водуха, кДж/(кг*К)
    return data(temperature + 273.15)


def get_distance_at_sep(x_values, y_values, sep):
    func_sep = interp1d(y_values, x_values, kind='linear',
                        bounds_error=False, fill_value=0)
    return func_sep(sep)


def get_sep_at_distance(x_values, y_values, distance):
    func_distance = interp1d(x_values, y_values, kind='linear',
                             bounds_error=False, fill_value=0)
    return func_distance(distance)
