import logging
import json

import math as m
import numpy as np

from scipy import constants as const
from scipy.interpolate import RectBivariateSpline
from scipy.stats import norm

from app.calculation.equipment.equipment_param import Equipment

log = logging.getLogger(__name__)


class FuelProperties:
    """Свойства вещества из справочных данных"""

    def __init__(self, type_sub):
        self.temperature_celsius: int | float = 0
        self.temperature_kelvin: int | float = const.zero_Celsius + self.temperature_celsius
        self.pressure_ambient: int | float = const.atm
        self.type_sub = type_sub

    def get_property_species(self, name_sub: str = '') -> dict:
        try:
            with open(file="combustible_liquid.json", mode='r', encoding='utf-8') as file_db_liq:
                combustible_liquid = json.load(file_db_liq)
            sub_dict = combustible_liquid.get(name_sub, None)
            log.info(f"Свойства вещества: {name_sub} {sub_dict.keys()}")
        except:
            log.info(f"Вещество [{name_sub}] отсутствует в базе")

        property_species = {"type_sub": sub_dict.get("substance_type")[-1],
                            "molar_mass": sub_dict.get("molecular_weight")[-1],
                            "n_C": sub_dict.get("atoms_nC")[-1],
                            "n_H": sub_dict.get("atoms_nH")[-1],
                            "n_X": sub_dict.get("atoms_nX")[-1],
                            "n_O": sub_dict.get("atoms_nO")[-1],
                            "exp_pres_max_kPa": sub_dict.get("pressure_expl_max")[-1],
                            "const_ant_a": sub_dict.get("const_ant_a")[-1],
                            "const_ant_b": sub_dict.get("const_ant_b")[-1],
                            "const_ant_ca": sub_dict.get("const_ant_ca")[-1], }
        return property_species


class FuelParameters(FuelProperties):
    """Параметры веществ в оборудовании и окружающей среде"""

    def __init__(self):
        super().__init__(self)
        self.sub_property = self.get_property_species(name_sub=name_sub)

    def calc_stoichiometric_concentration(self):
        nC = self.sub_property.get("nC", 0)
        nH = self.sub_property.get("nH", 0)
        nO = self.sub_property.get("nO", 0)
        nX = self.sub_property.get("nX", 0)
        betta = nC + ((nH - nX) / 4) - (nO/2)
        return 100 / (1 + 4.84 * betta)

    def calc_density_gas(self, temperature_gas: int | float = 333, molar_mass: int | float = 0) -> float:
        """Возвращает значение плотности газовой фазы вещества при заданной температуре"""
        temperature_gas_C = temperature_gas - 273
        density_gas = molar_mass / (22.413 * (1 + 0.00367 * temperature_gas_C))
        log.info(f"Плотность газа,кг/м3: {density_gas:.2f}")
        return density_gas

    def get_coefficient_eta(self, velocity_air_flow: int | float = 0, temp_air: int | float = None) -> float:
        if temp_air == None:
            temp_air = self.temperature_celsius
        x_temp = [10.0, 15.0, 20.0, 30.0, 35.0]
        y_vel = [0.0, 0.1, 0.2, 0.5, 1.0]
        eta = np.array([(1.0, 1.0, 1.0, 1.0, 1.0),
                        (3.0, 2.6, 2.4, 1.8, 1.6),
                        (4.6, 3.8, 3.5, 2.4, 2.3),
                        (6.6, 5.7, 5.4, 3.6, 3.2),
                        (10.0, 8.7, 7.7, 5.6, 4.6)])
        f_eta = RectBivariateSpline(x_temp, y_vel, eta.T, kx=4, ky=4, s=1)
        coefficient_eta = f_eta(temp_air, velocity_air_flow)
        log.info(
            f"При температуре: {temp_air} и скорости: {velocity_air_flow}, eta: {coefficient_eta[-1][-1]:.2f}")
        return coefficient_eta[-1][-1]

    def calc_evaporation_intencity_liquid(self, coefficient_eta: int | float = 0, molar_mass: int | float = 0, saturated_vapor_pressure: int | float = 0) -> float:
        """Возвращает интенсивность испарения паров жидкости"""
        return 10 ** -6 * coefficient_eta * m.sqrt(molar_mass) * saturated_vapor_pressure

    def calc_evaporation_mass(self, evaporation_intencity, area_evap: float = 10, time_evap: int | float = 3600, vent_multiplicity: int | float = 0) -> float:
        # evaporation_intencity = self.calc_evaporation_intencity_liquid()
        evaporation_mass = evaporation_intencity * area_evap * time_evap
        if vent_multiplicity > 0:
            evaporation_mass = evaporation_mass / \
                (vent_multiplicity * time_evap + 1)
        elif vent_multiplicity == 0:
            evaporation_mass = evaporation_mass
        return evaporation_mass

    def calc_saturated_vapor_pressure(self, temperature: int | float = None, const_ant_a:int | float = None,const_ant_b:int | float = None,const_ant_ca:int | float = None,) -> float:
        """Возвращает давление насыщенных паров в кПа при заданной температуре в С"""
        if temperature == None:
            temp = self.temperature_celsius
        else:
            temp = temperature

        return 10 ** (const_ant_a - (const_ant_b / (temp + const_ant_ca)))

    def calc_concentration_saturated_vapors_at_temperature(self) -> float:
        """Возвращает концентрацию насыщенного пара при температуре в С"""
        pressure_atm = self.pressure_ambient * 0.001  # kPa
        pressure_s = self.calc_saturated_vapor_pressure()  # kPa
        return 100 * (self.calc_saturated_vapor_pressure() / pressure_atm)

    def get_allowed_concentr_variations(self) -> float:
        # определяется по табл. Д.1 СП 12
        return 0.05

    def calc_reduced_mass(self,
                            type_substance: str = None,
                            specific_heat_combustion: float,
                            coefficient_part_combustion: float,
                            fuel_mass: float) -> float:
        const_H = 4_520_000  # J/kg
        if type_substance != "ГП":
            reduced_mass = (specific_heat_combustion/const_H) * coefficient_part_combustion * fuel_mass
        else:
            reduced_mass = (fuel_mass * coefficient_part_combustion * specific_heat_combustion) / const_H

        return reduced_mass

    def calc_pre_exponential_factor(self) -> float:
        velocity_air = 0
        mass_vap = 0
        allowed_concentr_variations = 0
        pre_exponential_factor = 0
        return pre_exponential_factor

    def get_coef_part_comb_inopen(self,
                                  type_substance: str = None,
                                  temperature_flash: int | float = None,
                                  temperature_substance: int | float = None,
                                  aerosol_formation: bool = False) -> float:
        """"Возвращает значение коэффициента Z участия горючих газов и паров в горении (при отсутствии аргументов - Водород)"""
        if type_substance == "ГГ":
            coef_part_comb = 0.5
        elif type_substance == "ГП":
            coef_part_comb = 0.1
        elif type_substance == ("ГЖ" or "ЛВЖ") and (temperature_substance >= temperature_flash):
            coef_part_comb = 0.3
        elif type_substance == ("ГЖ" or "ЛВЖ") and (temperature_substance < temperature_flash) and (aerosol_formation == True):
            coef_part_comb = 0.3
        elif type_substance == ("ГЖ" or "ЛВЖ") and (temperature_substance < temperature_flash) and (aerosol_formation == False):
            coef_part_comb = 0.3
        else:
            coef_part_comb = 1.0

        return coef_part_comb

    def calc_coef_part_comb_inclosed(self) -> float:
        """Расчет по приложению Д. СП12"""
        h_space = 0
        w_space = 0
        l_space = 0
        velocity_air = 0
        pre_exponential_factor = 0
        x_LCL = 0
        y_LCL = 0
        z_LCL = 0
        coef_part_comb = 0.1
        return coef_part_comb

    def calc_time_continuance_evaporation(self):
        pass

    def calc_mass_evaporated_substance(self):
        pass

    def calc_total_mass_substance_in_environment(self):
        pass


class FlowParameters(Equipment, FuelParameters):
    """Параметры выхода веществ из оборудования"""

    def __init__(self):
        super().__init__()

    def calc_expense_liquid(self):
        pass

    def calc_expense_gas(self):
        pass

    def calc_expense_liq_vapour(self, area: int | float):
        """Возвращает расход паров при испарении с открытой поверхности жидкости"""
        return area * self.calc_evaporation_intencity_liquid()

    def calc_(self):
        pass
