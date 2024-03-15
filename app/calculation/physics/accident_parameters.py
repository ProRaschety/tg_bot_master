import logging
import io
import json

import math as m
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from scipy.constants import physical_constants
from scipy.interpolate import RectBivariateSpline, interp1d


# from app.calculation.physics.physics_utils import compute_density_gas_phase

log = logging.getLogger(__name__)


class AccidentParameters:
    def __init__(self, type_accident: str | None = None) -> None:
        self.type_accident = type_accident
        self.pressure_ambient = physical_constants.get(
            'standard atmosphere')[0]  # Па
        self.heat_capacity_air = 1010  # Дж/кг*К
        self.R = physical_constants.get('molar gas constant')[0]  # Дж/моль*К
        self.K = 273.15  # К
        self.g = physical_constants.get('standard acceleration of gravity')[0]

    def get_init_data(self, *args, **kwargs):
        head = ('Наименование', 'Параметр', 'Значение', 'Ед.изм.')
        if self.type_accident == 'fire_pool':
            label = 'Пожар-пролива'
            # data_table = [
            #     {'id': 'Площадь пролива', 'var': 'F',  'unit_1': kwargs.get(
            #         'accident_fire_pool_pool_area'), 'unit_2': 'м\u00B2'},
            #     {'id': 'Скорость ветра', 'var': 'wₒ',
            #         'unit_1': f"{float((kwargs.get('accident_fire_pool_vel_wind'))):.1f}", 'unit_2': 'м/с'},
            #     {'id': 'Плотность окружающего воздуха', 'var': 'ρₒ',
            #         'unit_1': 1.25, 'unit_2': 'кг/м\u00B3'},
            #     {'id': 'Темепература окружающей среды', 'var': 'tₒ', 'unit_1': kwargs.get(
            #         'accident_fire_pool_temperature'), 'unit_2': '\u00B0С'},
            #     {'id': 'Плотность насыщенных паров топлива\nпри температуре кипения',
            #         'var': 'ρп', 'unit_1': 0.82, 'unit_2': 'кг/м\u00B3'},
            #     {'id': 'Удельная массовая скорость выгорания топлива',
            #         'var': 'm', 'unit_1': 0.06, 'unit_2': 'кг/(м\u00B2×с)'},
            #     {'id': 'Удельная теплота сгорания', 'var': 'Hсг',
            #         'unit_1': 36000, 'unit_2': 'кДж/кг'},
            #     {'id': 'Вещество', 'var': '-', 'unit_1': f"{kwargs.get('accident_fire_pool_sub')}", 'unit_2': '-'}]

        elif self.type_accident == 'fire_flash':
            label = 'Пожар-вспышка'
            data_table = [
                {'id': 'Радиус пролива над которым образуется\nвзрывоопасная зона', 'var': 'r',
                    'unit_1': kwargs.get('accident_fire_flash_radius_pool'), 'unit_2': 'м'},
                {'id': 'Масса горючих газов (паров)\nпоступивших в окружающее пространство', 'var': 'mг',  'unit_1': kwargs.get(
                    'accident_fire_flash_mass_fuel'), 'unit_2': 'кг'},
                {'id': 'Нижний концентрационный предел\nраспространения пламени',
                    'var': 'Cнкпр', 'unit_1': kwargs.get('accident_fire_flash_nkpr'), 'unit_2': '% об.'},
                {'id': 'Плотность окружающего воздуха', 'var': 'ρₒ',
                    'unit_1': 1.25, 'unit_2': 'кг/м\u00B3'},
                {'id': 'Темепература окружающей среды', 'var': 'tₒ', 'unit_1': kwargs.get(
                    'accident_fire_flash_temperature'), 'unit_2': '\u00B0С'},
                {'id': 'Вещество', 'var': '-', 'unit_1': kwargs.get('accident_fire_flash_sub'), 'unit_2': '-'}]

        elif self.type_accident == 'cloud_explosion':
            label = 'Взрыв облака паров'
            data_table = [
                {'id': 'Масса горючих газов (паров)\nсодержащегося в облаке', 'var': 'mг',  'unit_1': kwargs.get(
                    'accident_cloud_explosion_mass_fuel'), 'unit_2': 'кг'},
                {'id': 'Расположение облака паров горючего\nотносительно поверхности земли', 'var': '-',
                    'unit_1': 'Над\nповерхностью' if kwargs.get('accident_cloud_explosion_expl_cond') == 'above_surface' else 'На\nповерхности', 'unit_2': '-'},
                {'id': 'Класс пространства\nпо степени загроможденности',
                    'var': '-', 'unit_1': kwargs.get('accident_cloud_explosion_class_space'), 'unit_2': '-'},
                {'id': 'Класс горючего вещества', 'var': 'β', 'unit_1': kwargs.get(
                    'accident_cloud_explosion_class_fuel'), 'unit_2': '-'},
                {'id': 'Вещество', 'var': '-', 'unit_1': f"{kwargs.get('accident_cloud_explosion_sub')}", 'unit_2': '-'}]

        elif self.type_accident == 'horizontal_jet':
            label = 'Горизонтальный факел'
            jet = kwargs.get('accident_horizontal_jet_state')
            data_table = [
                {'id': 'Расстояние до облучаемого объекта', 'var': 'r',  'unit_1': kwargs.get(
                    'accident_horizontal_jet_human_distance'), 'unit_2': 'м'},
                {'id': 'Расход сжатого газа, паровой\nили жидкой фазы сжиженного газа',
                    'var': 'G',  'unit_1': kwargs.get('accident_horizontal_jet_mass_rate'), 'unit_2': 'кг/с'},
                {'id': 'Агрегатное состояние горючего вещества', 'var': 'K',
                    'unit_1': 'Жидкая фаза' if jet == 'jet_state_liquid' else 'Паровая фаза' if jet == 'jet_state_liq_gas_vap' else 'Сжатый газ', 'unit_2': '-'},
                {'id': 'Вещество', 'var': '-', 'unit_1': f"{kwargs.get('accident_horizontal_jet_sub')}", 'unit_2': '-'}]

        elif self.type_accident == 'vertical_jet':
            label = 'Вертикальный факел'
            jet = kwargs.get(
                'accident_vertical_jet_state')
            data_table = [
                {'id': 'Расстояние до облучаемого объекта', 'var': 'r',  'unit_1': kwargs.get(
                    'accident_vertical_jet_human_distance'), 'unit_2': 'м'},
                {'id': 'Расход сжатого газа, паровой\nили жидкой фазы сжиженного газа',
                    'var': 'G',  'unit_1': kwargs.get('accident_vertical_jet_mass_rate'), 'unit_2': 'кг/с'},
                {'id': 'Агрегатное состояние горючего вещества', 'var': 'K', 'unit_1': 'Жидкая фаза' if jet ==
                    'jet_state_liquid' else 'Паровая фаза' if jet == 'jet_state_liq_gas_vap' else 'Сжатый газ', 'unit_2': '-'},
                {'id': 'Вещество', 'var': '-', 'unit_1': f"{kwargs.get('accident_vertical_jet_sub')}", 'unit_2': '-'}]

        elif self.type_accident == 'fire_ball':
            label = 'Огненный шар'
            data_table = [
                {'id': 'Расстояние от облучаемого объекта до точки\nна поверхности земли непосредственно\nпод центром огненного шара', 'var': 'r',  'unit_1': kwargs.get(
                    'accident_fire_ball_human_distance'), 'unit_2': 'м'},
                {'id': 'Масса горючих газов (паров)\nсодержащегося в облаке', 'var': 'mг',  'unit_1': kwargs.get(
                    'accident_fire_ball_mass_fuel'), 'unit_2': 'кг'},
                {'id': 'Высота центра огненного шара', 'var': 'H', 'unit_1': kwargs.get(
                    'accident_fire_ball_center'), 'unit_2': '-'},
                {'id': 'Вещество', 'var': '-', 'unit_1': f"{kwargs.get('accident_fire_ball_sub')}", 'unit_2': '-'}]

        return data_table, head, label

    def compute_radius_LFL(self, density: int | float, mass: int | float, clfl: int | float):
        return 7.80 * (mass / (density * clfl)) ** 0.33

    def compute_height_LFL(self, density: int | float, mass: int | float, clfl: int | float):
        return 0.26 * (mass / (density * clfl)) ** 0.33

    def compute_overpres_inclosed(self,
                                  type_substance: str,
                                  evaporation_mass: int | float,
                                  free_volume: int | float, ) -> float:
        """Вычисляет значение избыточного давления при сгорании паров горючих веществ"""
        # m_vap = evaporation_mass

        # vol_free = vol
        # exp_pres_max = sub.sub_property.get("exp_pres_max_kPa", 900)
        # coef_kn = 3
        # density_vap = sub.calc_density_gas(temperature_gas=temp + self.K)
        stoichiometric_concentration = sub.calc_stoichiometric_concentration()
        overpres_inclosed = (exp_pres_max - self.pressure_ambient / 1000) * ((m_vap * coef_z) / (vol_free * density_vap)) * (100 / stoichiometric_concentration) * (
            1 / coef_kn)

        return overpres_inclosed

    def compute_overpres_inopen(self,
                                distance: int | float = 30,
                                reduced_mass: int | float = 30,
                                ) -> float:
        """форм.(В.14) и (В.22) СП12 и форм.(П3.47) М404"""
        pi_1 = (0.8 * (reduced_mass ** 0.33)) / distance
        pi_2 = (3.0 * (reduced_mass ** 0.66)) / distance ** 2
        pi_3 = (5.0 * reduced_mass) / distance ** 3
        overpres_inopen = self.pressure_ambient * (pi_1 + pi_2 + pi_3)
        impuls_inopen = (123 * reduced_mass) / distance

        return overpres_inopen, impuls_inopen

    def compute_redused_mass(self, expl_energy: int | float):
        return (expl_energy / 4.52) / 1_000_000

    def compute_expl_energy(self, k: int | float, Cp: int | float, mass: int | float, temp_liquid: int | float, boiling_point: int | float):
        return k * Cp * mass * (temp_liquid - (boiling_point + self.K))

    def _get_cloud_combustion_mode(self, fuel_class: int = 1, space_class: int = 1):
        if fuel_class == 1 and space_class == 1:
            cloud_combustion_mode = 1
        elif fuel_class == 1 and space_class == 2:
            cloud_combustion_mode = 1
        elif fuel_class == 1 and space_class == 3:
            cloud_combustion_mode = 2
        elif fuel_class == 1 and space_class == 4:
            cloud_combustion_mode = 3
        elif fuel_class == 2 and space_class == 1:
            cloud_combustion_mode = 1
        elif fuel_class == 2 and space_class == 2:
            cloud_combustion_mode = 2
        elif fuel_class == 2 and space_class == 3:
            cloud_combustion_mode = 3
        elif fuel_class == 2 and space_class == 4:
            cloud_combustion_mode = 4
        elif fuel_class == 3 and space_class == 1:
            cloud_combustion_mode = 2
        elif fuel_class == 3 and space_class == 2:
            cloud_combustion_mode = 3
        elif fuel_class == 3 and space_class == 3:
            cloud_combustion_mode = 4
        elif fuel_class == 3 and space_class == 4:
            cloud_combustion_mode = 5
        elif fuel_class == 4 and space_class == 1:
            cloud_combustion_mode = 3
        elif fuel_class == 4 and space_class == 2:
            cloud_combustion_mode = 4
        elif fuel_class == 4 and space_class == 3:
            cloud_combustion_mode = 5
        elif fuel_class == 4 and space_class == 4:
            cloud_combustion_mode = 6

        return cloud_combustion_mode

    def _compute_velocity_flame(self, cloud_combustion_mode: int = 1,  mass_gas_phase: int | float = 0):
        # скорость фронта пламени
        k1 = 43.0
        k2 = 26.0
        if cloud_combustion_mode == 1:
            u_front = 500
        elif cloud_combustion_mode == 6:
            u_front = k2 * mass_gas_phase ** 0.166
        elif cloud_combustion_mode == 5:
            u_front = k1 * mass_gas_phase ** 0.166
        elif cloud_combustion_mode == 4:
            u_front = k1 * mass_gas_phase ** 0.166
            if u_front > 200:
                u_front = k1 * mass_gas_phase ** 0.166
            else:
                u_front = 200
        elif cloud_combustion_mode == 3:
            u_front = k1 * mass_gas_phase ** 0.166
            if u_front > 300:
                u_front = k1 * mass_gas_phase ** 0.166
            else:
                u_front = 300
        elif cloud_combustion_mode == 2:
            u_front = k1 * mass_gas_phase ** 0.166
            if u_front > 500:
                u_front = k1 * mass_gas_phase ** 0.166
            else:
                u_front = 500
        return u_front

    def compute_nonvelocity(self, wind: int | float, density_fuel: int | float, mass_burn_rate: int | float, eff_diameter: int | float):
        return wind / (np.cbrt((mass_burn_rate * self.g * eff_diameter) / density_fuel))

    def get_flame_deflection_angle(self, nonvelocity: int | float):
        if nonvelocity > 1:
            eta = m.acos(nonvelocity ** -0.5)
        else:
            eta = m.acos(1)
        angle = float(m.degrees(eta))
        return angle

    def compute_lenght_flame_pool(self, nonvelocity: int | float, density_air: int | float, mass_burn_rate: int | float, eff_diameter: int | float):
        if nonvelocity < 1:
            lenght_flame = 42 * eff_diameter * \
                (mass_burn_rate / (density_air * m.sqrt(self.g * eff_diameter))) ** 0.61
        else:
            lenght_flame = 55 * eff_diameter * \
                ((mass_burn_rate / (density_air * m.sqrt(self.g * eff_diameter)))
                 ** 0.67) * nonvelocity ** -0.21
        return lenght_flame

    def compute_surface_emissive_power(self, eff_diameter: int | float, subst: str, heat_of_comb: int | float = None, lenght_flame: int | float = None, mass_burning_rate: int | float = None):
        if heat_of_comb == None:
            if eff_diameter <= 10:
                if subst == 'gasoline':
                    sep = 60
                elif subst == 'diesel':
                    sep = 40
                elif subst == 'LNG':
                    sep = 220
                elif subst == 'LPG':
                    sep = 80
                elif subst == 'liq_hydrogen':
                    sep = 150
            elif 10 < eff_diameter < 50:
                if subst == 'gasoline':
                    sep_1 = interp1d([1, 10, 20, 30, 40, 50], [
                        60, 60, 47, 35, 28, 25], 'linear')  # Бензин
                    sep = sep_1(eff_diameter)
                    # sep = round(0.0179 * eff_diameter ** 2 - 1.9614 * eff_diameter + 78.2, 2)
                elif subst == 'diesel':
                    sep_2 = interp1d([1, 10, 20, 30, 40, 50], [
                        40, 40, 32, 25, 21, 18], 'linear')  # ДТ
                    sep = sep_2(eff_diameter)
                    # sep = round(0.0179 * eff_diameter ** 2 - 1.9614 * eff_diameter + 78.2, 2)
                elif subst == 'LNG':
                    sep_3 = interp1d([1, 10, 20, 30, 40, 50], [220, 220, 180, 150, 130, 120],
                                     'linear')  # СПГ ГОСТ Р 57431-2017
                    sep = sep_3(eff_diameter)
                elif subst == 'LPG':
                    sep_4 = interp1d([1, 10, 20, 30, 40, 50], [
                        80, 80, 63, 50, 43, 40], 'linear')  # СУГ
                    sep = sep_4(eff_diameter)
                elif subst == 'liq_hydrogen':
                    sep_5 = interp1d([1, 10, 20, 30, 40, 50], [
                        150, 150, 120, 100, 90, 80], 'linear')  # Сжиженный водород
                    sep = sep_5(eff_diameter)
            elif eff_diameter >= 50:
                if subst == 'gasoline':
                    sep = 25
                elif subst == 'diesel':
                    sep = 18
                elif subst == 'LNG':
                    sep = 120
                elif subst == 'LPG':
                    sep = 40
                elif subst == 'liq_hydrogen':
                    sep = 80
            else:
                # для нефти и нефтепродуктов по ГОСТ 1510-2022
                sep = 140 * m.exp(-0.12 * eff_diameter) + 20 * \
                    (1 - m.exp(-0.12 * eff_diameter))
        else:
            sep = (0.4 * mass_burning_rate * heat_of_comb) / \
                (1 + 4 * (lenght_flame / eff_diameter))
        return sep

    def compute_mass_burning_rate(self, subst: str = None, heat_of_comb: int | float = None, Lg: int | float = None, Cp: int | float = None, Tb: int | float = None, Ta: int | float = None):
        if heat_of_comb == None:
            if subst == 'gasoline':
                m = 0.06
            elif subst == 'diesel':
                m = 0.04
            elif subst == 'LNG':
                m = 0.08
            elif subst == 'LPG':
                m = 0.10
            elif subst == 'liq_hydrogen':
                m = 0.17
        else:
            m = (0.001 * heat_of_comb) / (Lg + Cp * (Tb - Ta))
        return m

    def compute_heat_flux(self, eff_diameter: int | float, sep: int | float, lenght_flame: int | float, angle: int | float):
        # Определение интенсивности теплового излучения, кВт/м2
        # расстояние от центра лужи для расчета
        x_lim = int(1 + lenght_flame * 5)
        x_values = []
        qf = []
        for r in range(0, x_lim, 1):
            x_values.append(r)
            if r < 1 + eff_diameter * 0.5:
                qf_f = sep
            else:
                a = 2 * lenght_flame / eff_diameter
                b = 2 * r / eff_diameter

                A = m.sqrt(a ** 2 + (b + 1) ** 2 - 2 *
                           a * (b + 1) * m.sin(angle))
                B = m.sqrt(a ** 2 + (b - 1) ** 2 - 2 *
                           a * (b - 1) * m.sin(angle))
                C = m.sqrt(1 + ((b ** 2) - 1) * m.cos(angle) ** 2)
                D = m.sqrt((b - 1) / (b + 1))
                E = (a * m.cos(angle)) / (b - a * m.sin(angle))
                F = m.sqrt(b ** 2 - 1)
                Fv = (1 / 3.14) * \
                     (-E * m.atan(D) + E * ((a ** 2 + (b + 1) ** 2 - 2 * b * (1 + a * m.sin(angle))) / (A * B)) * m.atan(
                         (A * D) / B) + (m.cos(angle) / C) * (m.atan((a * b - F ** 2 * m.sin(angle)) / (F * C)) +
                                                              m.atan((F ** 2 * m.sin(angle)) / (F * C))))
                Fh = (1 / 3.14) * \
                     ((m.atan(1 / D)) +
                      (m.sin(angle) / C) *
                      (m.atan((a * b - F ** 2 * m.sin(angle)) / (F * C)) +
                       m.atan((F ** 2 * m.sin(angle)) / (F * C))) -
                      ((a ** 2 + (b + 1) ** 2 - 2 * (b + 1 + a * b * m.sin(angle))) / (A * B)) *
                      m.atan((A * D) / B))

                Fq = m.sqrt(Fv ** 2 + Fh ** 2)  # коэффициент облученности
                # коэффициент пропускания атмосферы
                t = m.exp(-0.0007 * (r - 0.5 * eff_diameter))
                qf_f = float(sep * Fq * t)  # интенсивность теплового излучения

            qf.append(qf_f)

        return x_values, qf

    def get_distance_at_sep(self, x_values, y_values, sep):
        func_sep = interp1d(y_values, x_values, kind='linear',
                            bounds_error=False, fill_value=0)
        return func_sep(sep)

    def get_sep_at_distance(self, x_values, y_values, distance):
        func_distance = interp1d(x_values, y_values, kind='linear',
                                 bounds_error=False, fill_value=0)
        return func_distance(distance)

    def get_coefficient_eta(self, velocity_air_flow: int | float = 0, temperature_air: int | float = None):

        x_temp = [10.0, 15.0, 20.0, 30.0, 35.0]
        y_vel = [0.0, 0.1, 0.2, 0.5, 1.0]
        eta = np.array([(1.0, 1.0, 1.0, 1.0, 1.0),
                        (3.0, 2.6, 2.4, 1.8, 1.6),
                        (4.6, 3.8, 3.5, 2.4, 2.3),
                        (6.6, 5.7, 5.4, 3.6, 3.2),
                        (10.0, 8.7, 7.7, 5.6, 4.6)])
        f_eta = RectBivariateSpline(x_temp, y_vel, eta.T, kx=4, ky=4, s=1)
        coefficient_eta = f_eta(temperature_air, velocity_air_flow)
        log.info(
            f"При температуре: {temperature_air} и скорости: {velocity_air_flow}, eta: {coefficient_eta[-1][-1]:.2f}")
        return coefficient_eta[-1][-1]

    def calc_evaporation_intencity_liquid(self, eta: int | float, molar_mass: int | float, vapor_pressure: int | float):
        """Возвращает интенсивность испарения паров жидкости"""
        return 10 ** -6 * eta * m.sqrt(molar_mass) * vapor_pressure

    # def calc_saturated_vapor_pressure(self, temperature: int | float = None, a: int | float, b: int | float, ca: int | float):
    #     """Возвращает давление насыщенных паров в кПа при заданной температуре в С"""
    #     return 10 ** (a - (b / (temperature + ca)))

    def calc_concentration_saturated_vapors_at_temperature(self, vapor_pressure: int | float):
        return 100 * vapor_pressure / self.pressure_ambient * 0.001  # kPa
