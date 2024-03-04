import logging
import json

import math as m
import numpy as np

from scipy.constants import physical_constants
from scipy.interpolate import RectBivariateSpline
from scipy.stats import norm

# from app.calculation.physics._property_sub import FlowParameters
from fluentogram import TranslatorRunner

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
        elif self.type_accident == 'fire_flash':
            label = 'Пожар-вспышка'
        elif self.type_accident == 'cloud_explosion':
            label = 'Взрыв облака паров'
        elif self.type_accident == 'horizontal_jet':
            label = 'Горизонтальный факел'
        elif self.type_accident == 'vertical_jet':
            label = 'Вертикальный факел'
        elif self.type_accident == 'fire_ball':
            label = 'Огненный шар'
        elif self.type_accident == 'bleve':
            label = 'Взрыв резервуара'

        if self.type_accident == 'fire_pool':
            data_table = [
                {'id': 'Удельная теплота сгорания', 'var': 'Hсг',
                    'unit_1': 36000, 'unit_2': 'кДж/кг'},
                {'id': 'Плотность насыщенных паров топлива\nпри температуре кипения',
                    'var': 'ρп', 'unit_1': 0.82, 'unit_2': 'кг/м\u00B3'},
                {'id': 'Удельная массовая скорость выгорания топлива',
                    'var': 'm', 'unit_1': 0.06, 'unit_2': 'кг/(м\u00B2×с)'},
                {'id': 'Площадь пролива', 'var': 'F',  'unit_1': kwargs.get(
                    'accident_fire_pool_pool_area'), 'unit_2': 'м\u00B2'},
                {'id': 'Скорость ветра', 'var': 'wₒ',
                    'unit_1': f"{float((kwargs.get('accident_fire_pool_vel_wind'))):.1f}", 'unit_2': 'м/с'},
                {'id': 'Плотность окружающего воздуха', 'var': 'ρₒ',
                    'unit_1': 1.25, 'unit_2': 'кг/м\u00B3'},
                {'id': 'Темепература окружающей среды', 'var': 'tₒ', 'unit_1': kwargs.get(
                    'accident_fire_pool_temperature'), 'unit_2': '\u00B0С'},
                {'id': 'Вещество', 'var': '-', 'unit_1': f"{kwargs.get('accident_fire_pool_sub')}", 'unit_2': '-'}]

        elif self.type_accident == 'fire_flash':
            data_table = [
                {'id': 'Масса горючих газов (паров)\nпоступивших в окружающее пространство', 'var': 'mг',  'unit_1': kwargs.get(
                    'accident_fire_flash_mass_fuel'), 'unit_2': 'кг'},
                {'id': 'Плотность горючих газов (паров)\nпри температуре окружающей среды',
                    'var': 'ρг', 'unit_1': 0.82, 'unit_2': 'кг/м\u00B3'},
                {'id': 'Нижний концентрационный предел\nраспространения пламени',
                    'var': 'Cнкпр', 'unit_1': 1.5, 'unit_2': '% об.'},
                {'id': 'Плотность окружающего воздуха', 'var': 'ρₒ',
                    'unit_1': 1.25, 'unit_2': 'кг/м\u00B3'},
                {'id': 'Темепература окружающей среды', 'var': 'tₒ', 'unit_1': kwargs.get(
                    'accident_fire_flash_temperature'), 'unit_2': '\u00B0С'},
                {'id': 'Вещество', 'var': '-', 'unit_1': f"{kwargs.get('accident_fire_flash_sub')}", 'unit_2': '-'}]
        elif self.type_accident == 'cloud_explosion':
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
        elif self.type_accident == 'fire_ball':
            data_table = [
                {'id': 'Расстояние от облучаемого объекта до точки\nна поверхности земли непосредственно\nпод центром огненного шара', 'var': 'r',  'unit_1': kwargs.get(
                    'accident_fire_ball_human_distance'), 'unit_2': 'м'},
                {'id': 'Масса горючих газов (паров)\nсодержащегося в облаке', 'var': 'mг',  'unit_1': kwargs.get(
                    'accident_fire_ball_mass_fuel'), 'unit_2': 'кг'},
                {'id': 'Высота центра огненного шара', 'var': 'H', 'unit_1': kwargs.get(
                    'accident_fire_ball_center'), 'unit_2': '-'},
                {'id': 'Вещество', 'var': '-', 'unit_1': f"{kwargs.get('accident_fire_ball_sub')}", 'unit_2': '-'}]
        return data_table, head, label

    def calc_radius_LCl(self):
        pass

    def calc_overpres_inclosed(self,
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
