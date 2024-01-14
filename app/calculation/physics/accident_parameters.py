import logging
import json

import math as m
import numpy as np

from scipy import constants as const
from scipy.interpolate import RectBivariateSpline
from scipy.stats import norm

from app.calculation.physics._property_sub import FlowParameters


log = logging.getLogger(__name__)


class AccidentParameters(FlowParameters):
    def __init__(self):
        self.pressure_ambient = 101.325  # кПа
        self.heat_capacity_air = 1010  # Дж/кг*К

    def calc_radius_LCl(self):
        pass

    def calc_overpres_inclosed(self,
                               type_substance: str,
                               evaporation_mass: int | float,
                               free_volume: int | float, ) -> float:
        """Вычисляет значение избыточного давления при сгорании паров горючих веществ"""
        sub = FuelParameters()

        m_vap = evaporation_mass

        vol_free = vol
        exp_pres_max = sub.sub_property.get("exp_pres_max_kPa", 900)
        coef_kn = 3
        density_vap = sub.calc_density_gas(temperature_gas=temp + 273)
        stoichiometric_concentration = sub.calc_stoichiometric_concentration()
        overpres_inclosed = (exp_pres_max - self.pressure_ambient) * ((m_vap * coef_z) / (vol_free * density_vap)) * (100 / stoichiometric_concentration) * (
            1 / coef_kn)

        return overpres_inclosed

    def calc_overpres_inopen(self,
                             distance: int | float = 30,
                             reduced_mass: int | float = 30,
                             ) -> float:
        """форм.(В.14) и (В.22) СП12 и форм.(П3.47) М404"""
        pi_1 = (0.8 * (reduced_mass ** 0.33)) / distance
        pi_2 = (3.0 * (reduced_mass ** 0.66)) / distance ** 2
        pi_3 = (5.0 * reduced_mass) / distance ** 3
        overpres_inopen = self.pressure_ambient * (pi_1 + pi_2 + pi_3)

        impuls_inopen = (123 * reduced_mass) / distance

        log.info(
            f"dP = {overpres_inopen:.2f} kPa, i+ = {impuls_inopen:.2f} Pa*c")

        return overpres_inopen, impuls_inopen
