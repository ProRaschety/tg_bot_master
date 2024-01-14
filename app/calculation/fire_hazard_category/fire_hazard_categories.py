import logging

import io
import json

from fluentogram import TranslatorRunner
from dataclasses import dataclass, asdict

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math as m
import numpy as np

from scipy.interpolate import RectBivariateSpline
from scipy.stats import norm

from CoolProp import CoolProp

log = logging.getLogger(__name__)


class FireHazardCategory:
    """Определние категорий по взрывопожарной и пожарной опасности"""

    CATEGORY_OUT_INST = {
        "increased_explosion_and_fire_hazard": "Ан",
        "explosion_and_fire_hazard": "Бн",
        "fire_hazard": "Вн",
        "moderate_fire_hazard": "Гн",
        "reduced_fire_hazard": "Дн"}

    CATEGORY_PREMISES = {
        "increased_explosion_and_fire_hazard": "А",
        "explosion_and_fire_hazard": "Б",
        "fire_hazard_1": "В1",
        "fire_hazard_2": "В2",
        "fire_hazard_3": "В3",
        "fire_hazard_4": "В4",
        "moderate_fire_hazard": "Г",
        "reduced_fire_hazard": "Д"}

    CATEGORY_BUILD = {
        "increased_explosion_and_fire_hazard": "А",
        "explosion_and_fire_hazard": "Б",
        "fire_hazard": "В",
        "moderate_fire_hazard": "Г",
        "reduced_fire_hazard": "Д"}

    def __init__(self, type_obj: str = None):
        self.fire_category = self.get_fire_category(type_obj=type_obj)
        self.burn_in_oxygen: bool = False

    def get_fire_category(self, type_obj: str = None) -> dict:
        if type_obj == "build":
            fire_category = self.CATEGORY_BUILD
        elif type_obj == "premises":
            fire_category = self.CATEGORY_PREMISES
        elif type_obj == "out_inst":
            fire_category = self.CATEGORY_OUT_INST
        else:
            fire_category = None
        return fire_category


class FireCategoryBuild(FireHazardCategory):
    def __init__(self):
        self.build_type: str = "out_inst"

    def get_category_premises(self):
        fire_hazard_categories = None

        # if type_substance == "ГГ" or type_substance == "ЛВЖ" or burn_in_oxygen == True:
        #     if temperature_flash <= 28.0:
        #     # fire_hazard_categories = category("increased_explosion_and_fire_hazard")
        #     # fire_hazard_categories = increased_explosion_and_fire_hazard  # "Ан"
        #
        #     elif burn_in_oxigen == True:
        #         if self.fire_risk > 10 ** -6:
        # fire_hazard_categories = category("increased_explosion_and_fire_hazard")
        # fire_hazard_categories = increased_explosion_and_fire_hazard  # "Ан"
        #
        # if type_substance == "ГП" or type_substance == "ЛВЖ" or type_substance == "ГЖ" or burn_in_oxygen == True:
        #     if temperature_flash > 28 | (fire_hazard_categories != increased_explosion_and_fire_hazard):
        #         fire_hazard_categories = explosion_and_fire_hazard  # "Бн"
        #
        #     elif burn_in_oxigen == True:
        #         if fire_risk > 10 ** -6:
        #             fire_hazard_categories = explosion_and_fire_hazard  # "Бн"
        #
        # if fire_hazard_categories != increased_explosion_and_fire_hazard and fire_hazard_categories != explosion_and_fire_hazard:
        #     fire_hazard_categories = fire_hazard  # "Вн"
        #
        # if type_substance == "НГ" or burned_disposed_fuel == True:
        #     fire_hazard_categories = moderate_fire_hazard  # "Гн"
        #
        # if fire_hazard_categories == increased_explosion_and_fire_hazard:
        #     increased_explosion_and_fire_hazard = "Ан"
        # elif fire_hazard_categories == explosion_and_fire_hazard:
        #     explosion_and_fire_hazard = "Бн"
        # elif fire_hazard_categories == fire_hazard:
        #     fire_hazard = "Вн"
        # elif fire_hazard_categories == moderate_fire_hazard:
        #     moderate_fire_hazard = "Гн"
        # else:
        #     reduced_fire_hazard = "Дн"

    def get_category_build(self):
        pass


class FireCategoryPremises(FireHazardCategory):
    def __init__(self):
        pass

    def get_category_premises(self, combustable_mass: int | float, specific_heat_combustion: float):
        lower_heat_combustion = 1
        category_premises = 1
        return category_premises


class FireCategoryOutInstall(FireHazardCategory):
    """Опеределение Категории по взрывопожароопасности по СП 12.13130 наружной установки"""

    def __init__(self, substance="Пропилен", type_obj="out_inst"):
        super().__init__(type_obj=type_obj)
        self.substance: str = substance

    def get_init_data_table(self) -> list[dict]:
        label = 'Исходные данные для определения категории\nнаружной установки по пожарной опасности'
        log.info("Определение категории наружной установки по пожарной опасности")
        physical_state = 'Газ'
        molar_mass = 42.08
        heat_of_burn = 45604
        pressure_substance = 2500
        temperature_substance = 60
        density_substance = 1.5387
        type_container = 'Сепаратор'
        volume_container = 50
        inlet_pipeline = 'Подводящий'
        lenght_inlet_pipeline = 700
        diameter_inlet_pipeline = 0.5
        outlet_pipeline = 'Отводящий'
        lenght_outlet_pipeline = 75
        diameter_outlet_pipeline = 0.5
        valve_closing_time = 120

        type_pipeline = 'Подводящий'

        data = [
            {'id': 'Время закрытия задвижек',
                'var': valve_closing_time, 'unit': 'с'},
            {'id': 'Диаметр', 'var': diameter_outlet_pipeline, 'unit': 'м'},
            {'id': 'Длина', 'var':  lenght_outlet_pipeline, 'unit': 'м'},
            {'id': 'Тип трубопровода', 'var': outlet_pipeline, 'unit': '-'},
            {'id': 'Диаметр', 'var': diameter_inlet_pipeline, 'unit': 'м'},
            {'id': 'Длина', 'var': lenght_inlet_pipeline, 'unit': 'м'},
            {'id': 'Тип трубопровода', 'var': inlet_pipeline, 'unit': '-'},
            {'id': 'Объем', 'var': volume_container, 'unit': 'м\u00B3'},
            {'id': 'Тип емкости', 'var': type_container, 'unit': '-'},
            {'id': 'Плотность газа',
                'var': density_substance, 'unit': 'кг/м\u00B3'},
            {'id': 'Температура газа', 'var': temperature_substance, 'unit': '\u00B0С'},
            {'id': 'Давление газа', 'var': pressure_substance, 'unit': 'кПа'},
            {'id': 'Удельная теплота сгорания',
                'var': heat_of_burn, 'unit': 'кДж/кг'},
            {'id': 'Молярная масса', 'var': molar_mass, 'unit': 'кг/кмоль'},
            {'id': 'Агрегатное состояние', 'var': physical_state, 'unit': '-'},
            {'id': 'Вещество', 'var': self.substance, 'unit': '-'}]

        return data, label

    def get_fire_hazard_categories(self) -> str:
        # category = FireHazardCategory.get_fire_category("out_inst")
        # property_sub = self.get_property_sub()
        type_substance = "ГГ"
        temperature_flash = 0           # С
        burn_in_oxigen = False
        fire_risk = 10 ** -7            # 1/год
        excessive_pressure_30m = 6      # кПа
        heat_flow_30m = 5               # кВт/м2
        zone_LCL = 35                   # м

        if type_substance == "ГГ" or type_substance == "ЛВЖ" or burn_in_oxigen == True:
            if temperature_flash <= 28.0:
                fire_hazard_categories = fire_category.get(
                    "increased_explosion_and_fire_hazard")
            elif burn_in_oxigen == True:
                if fire_risk > 10 ** -6:
                    fire_hazard_categories = fire_category.get(
                        "increased_explosion_and_fire_hazard")

        if type_substance == "ГП" or type_substance == "ЛВЖ" or type_substance == "ГЖ" or burn_in_oxigen == True:
            if temperature_flash > 28 | (fire_hazard_categories != increased_explosion_and_fire_hazard):
                fire_hazard_categories = explosion_and_fire_hazard  # "Бн"

            elif burn_in_oxigen == True:
                if fire_risk > 10 ** -6:
                    fire_hazard_categories = explosion_and_fire_hazard  # "Бн"

        if fire_hazard_categories != increased_explosion_and_fire_hazard and fire_hazard_categories != explosion_and_fire_hazard:
            fire_hazard_categories = fire_hazard  # "Вн"

        if type_substance == "НГ" or burned_disposed_fuel == True:
            fire_hazard_categories = moderate_fire_hazard  # "Гн"

        if fire_hazard_categories == increased_explosion_and_fire_hazard:
            increased_explosion_and_fire_hazard = "Ан"
        elif fire_hazard_categories == explosion_and_fire_hazard:
            explosion_and_fire_hazard = "Бн"
        elif fire_hazard_categories == fire_hazard:
            fire_hazard = "Вн"
        elif fire_hazard_categories == moderate_fire_hazard:
            moderate_fire_hazard = "Гн"
        else:
            reduced_fire_hazard = "Дн"

        return fire_hazard_categories


class FireExplosiveZones(FireHazardCategory):
    """Опеределение Класса зоны взрывопожароопасности по СП 423.1325800.2018"""
    pass
