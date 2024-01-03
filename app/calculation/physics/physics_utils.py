import logging

import numpy as np
import math as m

log = logging.getLogger(__name__)


def calc_characteristic_diameter(area):
    return m.sqrt((4 * area) / m.pi)


def calc_reynolds_number(diameter, velocity, kinematic_viscosity=1.62 * 10 ** -5):
    # kinematic_viscosity=1.62 * 10 ** -5 кинематическая вязкость воздуха м2 / c = 18.5 * 10 ** -6 Па*с
    return (velocity * diameter) / kinematic_viscosity


def parse_phase_key(key):
    """
    Convert phase string identifier into value for phys library.
    All values besides 'gas' and 'liquid' will be converted to None

    Parameters
    ----------
    key : str
        Phase identifier key

    Returns
    -------
    str or None

    """
    return key if key in ['gas', 'liquid'] else None


def compute_tank_mass_param(species, phase=None, temp=None, pres=None, vol=None, mass=None):
    log.info("Tank Mass calculation requested")
    phase = parse_phase_key(phase)
    if (temp is not None or phase is not None) and pres is not None and vol is not None and mass is not None:
        msg = 'Too many inputs provided - three of [temperature (or phase), pressure, volume, mass] required'
        raise ValueError(msg)

    if vol is not None and mass is not None:
        density = mass / vol  # kg/m3
    else:
        density = None

    fluid = create_fluid(species, temp, pres, density, phase)

    if density is None:
        if vol is None:
            result1 = mass / fluid.rho
        else:
            result1 = vol * fluid.rho
    elif pres is None:
        result1 = fluid.P
    else:
        result1 = fluid.T

    if phase is not None:  # saturated phase
        result2 = fluid.T
    else:
        result2 = None

    log.info("Tank Mass calculation complete")
    return mass
