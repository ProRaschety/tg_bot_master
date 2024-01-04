import logging
import json

import math as m
import numpy as np

from scipy import constants as const
from scipy.interpolate import RectBivariateSpline
from scipy.stats import norm

from ._const import Const
from app.calculation.equipment.equipment_param import Equipment

log = logging.getLogger(__name__)


class FuelProperties:
    """Свойства веществ из справочных данных"""

    def __init__(self):
        self.temperature_celsius: int | float = Const
        self.temperature_kelvin: int | float = const.zero_Celsius + self.temperature_celsius
        self.pressure_ambient: int | float = const.atm

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
                            "const_ant_ca": sub_dict.get("const_ant_ca")[-1],
                            }

        return property_species


class FuelParameters(FuelProperties):
    """Параметры веществ в оборудовании и окружающей среде"""

    def __init__(self):
        super().__init__()
        self.sub_property = self.get_property_species(name_sub=name_sub)

    def calc_stoichiometric_concentration(self):
        nC = self.sub_property.get("nC", 0)
        nH = self.sub_property.get("nH", 0)
        nO = self.sub_property.get("nO", 0)
        nX = self.sub_property.get("nX", 0)
        betta = nC + ((nH - nX) / 4) - (nO/2)
        return 100 / (1 + 4.84 * betta)

    def calc_density_gas(self, temperature_gas: int | float = 333) -> float:
        """Возвращает значение плотности газовой фазы вещества при заданной температуре"""
        molar_mass = self.sub_property.get("molar_mass", None)
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

    def calc_evaporation_intencity_liquid(self, coefficient_eta: int | float = 0, saturated_vapor_pressure: int | float = 0) -> float:
        """Возвращает интенсивность испарения паров жидкости"""
        evaporation_intencity = 10 ** -6 * coefficient_eta * \
            m.sqrt(self.sub_property.get("molar_mass", None)) * \
            saturated_vapor_pressure
        return evaporation_intencity

    def calc_evaporation_mass(self, evaporation_intencity, area_evap: float = 10, time_evap: int | float = 3600, vent_multiplicity: int | float = 0) -> float:
        # evaporation_intencity = self.calc_evaporation_intencity_liquid()
        evaporation_mass = evaporation_intencity * area_evap * time_evap
        if vent_multiplicity > 0:
            evaporation_mass = evaporation_mass / \
                (vent_multiplicity * time_evap + 1)
        elif vent_multiplicity == 0:
            evaporation_mass = evaporation_mass
        return evaporation_mass

    def calc_saturated_vapor_pressure(self, temperature: int | float = None) -> float:
        """Возвращает давление насыщенных паров в кПа при заданной температуре в С"""
        a = self.sub_property.get("const_ant_a", 0)
        b = self.sub_property.get("const_ant_b", 0)
        ca = self.sub_property.get("const_ant_ca", 0)
        if temperature == None:
            temp = self.temperature_celsius
        else:
            temp = temperature
        return 10 ** (a - (b / (temp + ca)))

    def calc_concentration_saturated_vapors_at_temperature(self):
        """Возвращает концентрацию насыщенного пара при температуре С"""
        pressure_atm = self.pressure_ambient * 0.001  # kPa
        pressure_s = self.calc_saturated_vapor_pressure()  # kPa
        return 100 * (self.calc_saturated_vapor_pressure() / pressure_atm)

    def get_allowed_concentr_variations(self):
        # определяется по табл. Д.1 СП 12
        return 0.05

    def calc_pre_exponential_factor(self):
        velocity_air = 0
        mass_vap = 0
        allowed_concentr_variations = 0
        pre_exponential_factor = 0

    def calc_coef_z(self):
        h_space = 0
        w_space = 0
        l_space = 0
        velocity_air = 0
        pre_exponential_factor = 0
        x_LCL = 0
        y_LCL = 0
        z_LCL = 0

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


class AccidentParameters(FlowParameters):
    def __init__(self):
        super().__init__()

    def calc_radius_LCl(self):
        pass

    def calc_overpres_inclosed(name_sub: str,
                               evaporation_intencity: int | float,
                               area_evap: int | float,
                               mass: int | float,
                               vol: int | float,
                               temp: int | float,
                               time_evap: int | float = 3600,
                               vent_multiplicity: int | float = 0) -> float:
        """Вычисляет значение избыточного давления при сгорании паров горючих веществ"""
        sub = FuelParameters()
        type_sub = sub.sub_property.get("type_sub", None)
        if name_sub == "Водород":
            coef_z = 1
        elif type_sub == "ГГ":
            coef_z = 0.5
        elif type_sub == "ГЖ" or "ЛВЖ":
            coef_z = 0.0648
        else:
            coef_z = 0
        m_vap = sub.calc_evaporation_mass(time_evap=time_evap,
                                          vent_multiplicity=vent_multiplicity,
                                          evaporation_intencity=evaporation_intencity,
                                          area_evap=area_evap)
        log.info(f"Масса паров,кг: {m_vap:.2f}")
        vol_free = vol
        exp_pres_max = sub.sub_property.get("exp_pres_max_kPa", 900)
        pres_atm = 101.325  # кПа
        coef_kn = 3
        density_vap = sub.calc_density_gas(temperature_gas=temp + 273)
        stoichiometric_concentration = sub.calc_stoichiometric_concentration()
        overpres_inclosed = (exp_pres_max - pres_atm) * ((m_vap * coef_z) / (vol_free * density_vap)) * (100 / stoichiometric_concentration) * (
            1 / coef_kn)
        return overpres_inclosed

    def calc_overpres_inopen(self) -> float:
        overpres_inopen = 1
        return overpres_inopen

    def calc_(self):
        pass
