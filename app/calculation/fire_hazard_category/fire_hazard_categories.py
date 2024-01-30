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
        self.build_type: str = "industrial"  # "storage_room"

    def _calc_area_premises(self, *args):
        area_a = []
        area_b = []
        area_v = []
        area_g = []
        area_other = []
        area_efs_a = []
        area_efs_b = []
        area_efs_v = []
        if args:
            for i in args:
                if i.get('category') == 'А':
                    area_a.append(i.get('area'))
                    area_efs_a.append(i.get('efs', False))
                elif i.get('category') == 'Б':
                    area_b.append(i.get('area'))
                    area_efs_b.append(i.get('efs', False))
                elif i.get('category') in ['В1', 'В2', 'В3']:
                    area_v.append(i.get('area'))
                    area_efs_v.append(i.get('efs', False))
                elif i.get('category') == 'Г':
                    area_g.append(i.get('area'))
                else:
                    area_other.append(i.get('area'))
        return sum(area_a), sum(area_b), sum(area_v), sum(area_g), sum(area_other), area_efs_a, area_efs_b, area_efs_v

    def _check_category_a(self,  efs_a, total_area, a: int | float = 0, b: int | float = 0) -> str | None:
        area_a = a
        area_percent_5 = total_area * 0.05
        area_percent_25 = total_area * 0.25
        if area_a >= area_percent_5 or area_a >= 200:
            if any(efs_a) is False:
                if area_a >= area_percent_5:
                    log.info(
                        f'Площадь пом.кат. А: {area_a}м2 сост. {(100 / (total_area / area_a)):.2f}% > 5% от {total_area}м2 и нет АУПТ')
                    cat_build = 'A'
                    return cat_build
                else:
                    log.info(
                        f'Площадь пом.кат. А: {area_a}м2 сост. {(100 / (total_area / area_a)):.2f}% не прев. 5%, но боллее 200 м2 и нет АУПТ')
                    cat_build = 'A'
                    return cat_build
            else:
                if area_a >= area_percent_25 or area_a >= 1000:
                    if area_a >= area_percent_25:
                        log.info(
                            f'Площадь пом.кат. А: {area_a}м2 сост. {(100 / (total_area / area_a)):.2f}% > 25% от {total_area}м2 оборуд. АУПТ')
                        cat_build = 'A'
                        return cat_build
                    else:
                        log.info(
                            f'Площадь пом.кат. А: {area_a}м2 больше 1000м2 и оборуд. АУПТ')
                        cat_build = 'A'
                        return cat_build
                else:
                    return None
        else:
            return None

    def _check_category_b(self,  efs_a, efs_b, total_area, a: int | float = 0, b: int | float = 0) -> str | None:
        area_a = a
        area_b = b
        area_percent_5 = total_area * 0.05
        area_percent_25 = total_area * 0.25
        if (area_a + area_b) >= area_percent_5 or (area_a + area_b) >= 200:
            if any(efs_a) is False:
                if (area_a + area_b) >= area_percent_5:
                    log.info(
                        f'Площадь пом.кат. А и Б: {area_a + area_b}м2 сост. {(100 / (total_area / (area_a + area_b))):.2f}% > 5% от {total_area}м2 и отсутст. АУПТ')
                    cat_build = 'Б'
                    return cat_build
                else:
                    log.info(
                        f'Площадь пом.кат. А и Б: {area_a + area_b}м2 более 200м2 и отсутст. АУПТ')
                    cat_build = 'Б'
                    return cat_build
            else:
                if (area_a + area_b) >= area_percent_25 or (area_a + area_b) >= 1000:
                    if (area_a + area_b) >= area_percent_25:
                        log.info(
                            f'Площадь пом.кат. А и Б: {area_a + area_b}м2 сост. {(100 / (total_area / (area_a + area_b))):.2f}% > 25% от {total_area}м2 оборуд. АУПТ')
                        cat_build = 'Б'
                        return cat_build
                    else:
                        log.info(
                            f'Площадь пом.кат. А и Б: {area_a + area_b}м2 больше 1000м2 и оборуд. АУПТ')
                        cat_build = 'Б'
                        return cat_build

                else:
                    return None
        else:
            return None

    def _check_category_v(self,  efs_a, efs_b, efs_v, total_area, a: int | float = 0, b: int | float = 0, v: int | float = 0) -> str | None:
        area_percent_5 = total_area * 0.05
        area_percent_10 = total_area * 0.10
        area_percent_25 = total_area * 0.25

        if a == 0 and b == 0 and v > 0:
            if v < area_percent_10:
                return None
            else:
                log.info(
                    f'Площадь пом.кат. В: {a + b + v}м2 сост. {100/(total_area/(a + b + v)):.2f}% > 10% от {total_area}м2')
                cat_build = 'В'
                return cat_build

        if a > 0 or b > 0 or v > 0:
            if (a + b + v) >= area_percent_5:
                if all(efs_a + efs_b + efs_v) is True:
                    if ((a + b + v) >= area_percent_25) or ((a + b + v) >= 3500):
                        if ((a + b + v) >= area_percent_25):
                            log.info(
                                f'Площадь пом.кат. А, Б и В: {a + b + v}м2 сост. {100/(total_area/(a + b + v)):.2f}% > 25% от {total_area}м2 и пом.кат. А,Б,В1-В3 оборуд. АУПТ')
                            cat_build = 'В'
                            return cat_build
                        else:
                            log.info(
                                f'Площадь пом.кат. А, Б и В: {a + b + v}м2 более 3500 м2 и пом.кат. А,Б,В1-В3 оборуд. АУПТ')
                            cat_build = 'В'
                            return cat_build
                    else:
                        return None
                else:
                    log.info(
                        f'Площадь пом.кат. А, Б и В: {a + b + v}м2 сост. {100/(total_area/(a + b + v)):.2f}% > 5% от {total_area}м2 и пом.кат. А,Б,В1-В3 не оборуд. АУПТ')
                    cat_build = 'В'
                    return cat_build
            else:
                return None

    def _check_category_g(self,  efs_a, efs_b, efs_v, total_area, a: int | float = 0, b: int | float = 0, v: int | float = 0, g: int | float = 0) -> str | None:
        area_percent_5 = total_area * 0.05
        area_percent_25 = total_area * 0.25
        if (a + b + v + g) >= area_percent_5:
            if all(efs_a + efs_b + efs_v) is True:
                if ((a + b + v + g) >= area_percent_25) or ((a + b + v + g) >= 5000):
                    if ((a + b + v + g) >= area_percent_25):
                        log.info(
                            f'Площадь пом.кат. А, Б, В и Г: {a + b + v + g}м2 сост. {100/(total_area/(a + b + v + g)):.2f}% > 25% от {total_area}м2 и пом.кат. А,Б,В1-В3 оборуд. АУПТ')
                        cat_build = 'Г'
                        return cat_build
                    else:
                        log.info(
                            f'Площадь пом.кат. А, Б, В и Г: {a + b + v + g}м2 более 5000 м2 и пом.кат. А,Б,В1-В3 оборуд. АУПТ')
                        cat_build = 'Г'
                        return cat_build
                else:
                    return None
            else:
                log.info(
                    f'Площадь пом.кат. А, Б, В и Г: {a + b + v + g}м2 сост. {100/(total_area/(a + b + v + g)):.2f}% > 5% от {total_area}м2 и пом.кат. А,Б,В1-В3 не оборуд. АУПТ')
                cat_build = 'Г'
                return cat_build
        else:
            return None

    def get_category_build(self, *args, total_area: int | float = None, **kwargs):
        a, b, v, g, other, efs_a, efs_b, efs_v = self._calc_area_premises(
            *args)
        cat_build = ''
        # print(f'area_efs ([А], [Б], [В]): {efs_a, efs_b, efs_v}')
        if total_area is None:
            total_area = a + b + v + g + other
        log.info(f'Общая площадь, м2: {total_area}')
        log.info(
            f'Площадь пом. кат. А: {a} -> {(100 / (total_area / a)):.2f}% от {total_area}м2')
        log.info(
            f'Площадь пом. кат. Б: {b} -> {(100 / (total_area / b)):.2f}% от {total_area}м2')
        log.info(
            f'Площадь пом. кат. В1-В3: {v} -> {(100 / (total_area / v)):.2f}% от {total_area}м2')
        log.info(
            f'Площадь пом. кат. Г: {g} -> {(100 / (total_area / g)):.2f}% от {total_area}м2')
        log.info(
            f'Общая площадь пом. с кат.: {other} -> {(100 / (total_area / other)):.2f}% от {total_area}м2')

        if a > 0 and b > 0:
            cat_build = self._check_category_a(
                a=a, efs_a=efs_a, total_area=total_area)
            log.info(f'Проверка кат.А: {cat_build}')

        if a >= 0 and b > 0:
            cat_build = self._check_category_b(
                a=a, b=b, efs_a=efs_a, efs_b=efs_b, total_area=total_area)
            log.info(f'Проверка кат.Б: {cat_build}')

        if (cat_build is None or cat_build == '') and v > 0:
            cat_build = self._check_category_v(
                a=a, b=b, v=v, efs_a=efs_a, efs_b=efs_b, efs_v=efs_v, total_area=total_area)
            log.info(f'Проверка кат.B: {cat_build}')

        if (cat_build is None or cat_build == '') and g > 0:
            cat_build = self._check_category_g(
                a=a, b=b, v=v, g=g, efs_a=efs_a, efs_b=efs_b, efs_v=efs_v, total_area=total_area)
            log.info(f'Проверка кат.Г: {cat_build}')

        if (cat_build is None or cat_build == ''):
            cat_build = 'Д'
            log.info(f'Проверка кат.Д: {cat_build}')
        return cat_build


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
        label = 'Категория наружной установки по пожарной опасности'
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
