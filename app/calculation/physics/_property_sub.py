import logging
import json

import math as m
import numpy as np

from scipy import constants as const
from scipy.interpolate import RectBivariateSpline
from scipy.stats import norm

from ._const import Const

log = logging.getLogger(__name__)


class FuelProperties:
    """Свойства веществ из справочных данных"""

    def __init__(self):
        self.temperature_celsius: int | float = Const
        self.temperature_kelvin: int | float = const.zero_Celsius + self.temperature_celsius
        self.pressure_ambient: int | float = const.atm

    def get_property_species(self, name_sub: str = '') -> dict:
        try:
            with open(file="C:/Users\ACADEMIK\YandexDisk\Python_МетодМатериалы\combustible_liquid.json", mode='r', encoding='utf-8') as file_db_liq:
                combustible_liquid = json.load(file_db_liq)
            sub_dict = combustible_liquid.get(name_sub, None)
            log.info(f"Свойства вещества: {name_sub} {sub_dict.keys()}")

        except:
            log.info(f"Вещество [{name_sub}] отсутствует в базе")

        p_max = sub_dict.get("pressure_expl_max")[-1]
        if p_max == None:
            p_max = 900
        property_species = {"type_sub": sub_dict.get("substance_type")[-1],
                            "molar_mass": sub_dict.get("molecular_weight")[-1],
                            "n_C": sub_dict.get("atoms_nC")[-1],
                            "n_H": sub_dict.get("atoms_nH")[-1],
                            "n_X": sub_dict.get("atoms_nX")[-1],
                            "n_O": sub_dict.get("atoms_nO")[-1],
                            "exp_pres_max_kPa": p_max,
                            "const_ant_a": sub_dict.get("const_ant_a")[-1],
                            "const_ant_b": sub_dict.get("const_ant_b")[-1],
                            "const_ant_ca": sub_dict.get("const_ant_ca")[-1],
                            }
        return property_species
