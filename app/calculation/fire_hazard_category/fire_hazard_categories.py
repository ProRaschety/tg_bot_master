import logging
# import io
# import json

# from fluentogram import TranslatorRunner
# from dataclasses import dataclass, asdict

# import matplotlib as mpl
# import matplotlib.pyplot as plt
# import matplotlib.patches as patches
# import math as m
# import numpy as np

from scipy.interpolate import RectBivariateSpline, interp1d
from scipy.stats import norm
from scipy.constants import physical_constants

# from CoolProp import CoolProp

from app.calculation.models.calculations import RoomModel, SectionModel

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

    def calc_area_premises(self, *args):
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
                    area_a.append(float(i.get('area')))
                    area_efs_a.append(True if i.get(
                        'efs', 'False') == "True" else False)
                elif i.get('category') == 'Б':
                    area_b.append(float(i.get('area')))
                    area_efs_b.append(True if i.get(
                        'efs', 'False') == "True" else False)
                elif i.get('category') in ['В1', 'В2', 'В3']:
                    area_v.append(float(i.get('area')))
                    area_efs_v.append(True if i.get(
                        'efs', 'False') == "True" else False)
                elif i.get('category') == 'Г':
                    area_g.append(float(i.get('area')))
                else:
                    area_other.append(float(i.get('area')))
        else:
            pass
        return sum(area_a), sum(area_b), sum(area_v), sum(area_g), sum(area_other), area_efs_a, area_efs_b, area_efs_v

    def _check_category_a(self,  efs_a, total_area, a: int | float = 0, b: int | float = 0) -> str | None:
        area_a = a
        area_percent_5 = total_area * 0.05
        area_percent_25 = total_area * 0.25
        if area_a >= area_percent_5 or area_a >= 200:
            if all(efs_a) is False:
                if area_a >= area_percent_5:
                    cause = (
                        f'Площадь помещений кат. А: {area_a:.2f}м\u00B2 сост. {(100 / (total_area / area_a)):.2f}% от {total_area:.2f}м\u00B2 и не оборуд. АУПТ')
                    cat_build = 'A'
                    return cat_build, cause
                else:
                    cause = (
                        f'Площадь помещений кат. А: {area_a:.2f}м\u00B2 сост. {(100 / (total_area / area_a)):.2f}%, но ≥ 200м\u00B2 и не оборуд. АУПТ')
                    cat_build = 'A'
                    return cat_build, cause
            else:
                if area_a >= area_percent_25 or area_a >= 1000:
                    if area_a >= area_percent_25:
                        cause = (
                            f'Площадь помещений кат. А: {area_a:.2f}м\u00B2 сост. {(100 / (total_area / area_a)):.2f}% от {total_area:.2f}м\u00B2 оборуд. АУПТ')
                        cat_build = 'A'
                        return cat_build, cause
                    else:
                        cause = (
                            f'Площадь помещений кат. А: {area_a:.2f}м\u00B2 ≥ 1000м\u00B2 и оборуд. АУПТ')
                        cat_build = 'A'
                        return cat_build, cause
                else:
                    return None, None
        else:
            return None, None

    def _check_category_b(self,  efs_a, efs_b, total_area, a: int | float = 0, b: int | float = 0) -> str | None:
        area_a = a
        area_b = b
        area_percent_5 = total_area * 0.05
        area_percent_25 = total_area * 0.25
        if (area_a + area_b) >= area_percent_5 or (area_a + area_b) >= 200:
            if all(efs_a + efs_b) is False:
                if (area_a + area_b) >= area_percent_5:
                    cause = (
                        f'Площадь помещений кат. А и Б: {(area_a + area_b):.2f}м\u00B2 сост. {(100 / (total_area / (area_a + area_b))):.2f}% от {total_area:.2f}м\u00B2 и не оборуд. АУПТ')
                    cat_build = 'Б'
                    return cat_build, cause
                else:
                    cause = (
                        f'Площадь помещений кат. А и Б: {(area_a + area_b):.2f}м\u00B2 ≥ 200м\u00B2 и не оборуд. АУПТ')
                    cat_build = 'Б'
                    return cat_build, cause
            else:
                if (area_a + area_b) >= area_percent_25 or (area_a + area_b) >= 1000:
                    if (area_a + area_b) >= area_percent_25:
                        cause = (
                            f'Площадь помещений кат. А и Б: {(area_a + area_b):.2f}м\u00B2 сост. {(100 / (total_area / (area_a + area_b))):.2f}% от {total_area:.2f}м\u00B2 оборуд. АУПТ')
                        cat_build = 'Б'
                        return cat_build, cause
                    else:
                        cause = (
                            f'Площадь помещений кат. А и Б: {(area_a + area_b):.2f}м\u00B2 ≥ 1000м\u00B2 и оборуд. АУПТ')
                        cat_build = 'Б'
                        return cat_build, cause

                else:
                    return None, None
        else:
            return None, None

    def _check_category_v(self,  efs_a, efs_b, efs_v, total_area, a: int | float = 0, b: int | float = 0, v: int | float = 0) -> str | None:
        area_percent_5 = total_area * 0.05
        area_percent_10 = total_area * 0.10
        area_percent_25 = total_area * 0.25

        if a == 0 and b == 0 and v > 0:
            if v < area_percent_10:
                return None, None
            else:
                cause = (
                    f'Площадь помещений кат. В1-В3: {(v):.2f}м\u00B2 сост. {100/(total_area/(v)):.2f}% от {total_area:.2f}м\u00B2')
                cat_build = 'В'
                return cat_build, cause

        elif a > 0 and b > 0 and v > 0:
            if (a + b + v) >= area_percent_5:
                if all(efs_a + efs_b + efs_v):
                    if ((a + b + v) >= area_percent_25) or ((a + b + v) >= 3500):
                        if ((a + b + v) >= area_percent_25):
                            cause = (
                                f'Площадь помещений кат. А, Б и В1-В3: {(a + b + v):.2f}м\u00B2 сост. {100/(total_area/(a + b + v)):.2f}% от {total_area:.2f}м\u00B2 и помещения кат. А,Б,В1-В3 оборуд. АУПТ')
                            cat_build = 'В'
                            return cat_build, cause
                        else:
                            cause = (
                                f'Площадь помещений кат. А, Б и В1-В3: {(a + b + v):.2f}м\u00B2 ≥ 3500 м\u00B2 и помещения кат. А,Б,В1-В3 оборуд. АУПТ')
                            cat_build = 'В'
                            return cat_build, cause
                    else:
                        return None, None
                else:
                    cause = (
                        f'Площадь помещений кат. А, Б и В1-В3: {(a + b + v):.2f}м\u00B2 сост. {100/(total_area/(a + b + v)):.2f}% от {total_area:.2f}м\u00B2 и помещения кат. А,Б,В1-В3 не оборуд. АУПТ')
                    cat_build = 'В'
                    return cat_build, cause

        elif a == 0 and b > 0 and v > 0:
            if (b + v) >= area_percent_5:
                if all(efs_b + efs_v):
                    if ((b + v) >= area_percent_25) or ((b + v) >= 3500):
                        if ((b + v) >= area_percent_25):
                            cause = (
                                f'Площадь помещений кат. Б и В1-В3: {(b + v):.2f}м\u00B2 сост. {100/(total_area/(b + v)):.2f}% от {total_area}м\u00B2 и помещения кат. Б,В1-В3 оборуд. АУПТ')
                            cat_build = 'В'
                            return cat_build, cause
                        else:
                            cause = (
                                f'Площадь помещений кат. Б и В1-В3: {(b + v):.2f}м\u00B2 ≥ 3500 м\u00B2 и помещения кат. Б,В1-В3 оборуд. АУПТ')
                            cat_build = 'В'
                            return cat_build, cause
                    else:
                        return None, None
                else:
                    cause = (
                        f'Площадь помещений кат. Б и В1-В3: {(b + v):.2f}м\u00B2 сост. {100/(total_area/(b + v)):.2f}% от {total_area:.2f}м\u00B2 и помещения кат. Б,В1-В3 не оборуд. АУПТ')
                    cat_build = 'В'
                    return cat_build, cause

        elif a > 0 and b == 0 and v > 0:
            if (a + v) >= area_percent_5:
                if all(efs_a + efs_v):
                    if ((a + v) >= area_percent_25) or ((a + v) >= 3500):
                        if ((a + v) >= area_percent_25):
                            cause = (
                                f'Площадь помещений кат. А и В1-В3: {(a + v):.2f}м\u00B2 сост. {100/(total_area/(a + v)):.2f}% от {total_area:.2f}м\u00B2 и помещения кат. А,В1-В3 оборуд. АУПТ')
                            cat_build = 'В'
                            return cat_build, cause
                        else:
                            cause = (
                                f'Площадь помещений кат. А и В1-В3: {(a + v):.2f}м\u00B2 ≥ 3500 м\u00B2 и помещения кат. А,В1-В3 оборуд. АУПТ')
                            cat_build = 'В'
                            return cat_build, cause
                    else:
                        return None, None
                else:
                    cause = (
                        f'Площадь помещений кат. А и В1-В3: {(a + v):.2f}м\u00B2 сост. {100/(total_area/(a + v)):.2f}% от {total_area:.2f}м\u00B2 и помещения кат. А,В1-В3 не оборуд. АУПТ')
                    cat_build = 'В'
                    return cat_build, cause

            else:
                return None, None
        else:
            return None, None

    def _check_category_g(self,  efs_a, efs_b, efs_v, total_area, a: int | float = 0, b: int | float = 0, v: int | float = 0, g: int | float = 0) -> str | None:
        area_percent_5 = total_area * 0.05
        area_percent_25 = total_area * 0.25
        if a > 0 and b > 0 and v > 0:
            if (a + b + v + g) >= area_percent_5:
                if all(efs_a + efs_b + efs_v):
                    if ((a + b + v + g) >= area_percent_25) or ((a + b + v + g) >= 5000):
                        if ((a + b + v + g) >= area_percent_25):
                            cause = (
                                f'Площадь помещений кат. А, Б, В1-В3 и Г: {(a + b + v + g):.2f}м\u00B2 сост. {100/(total_area/(a + b + v + g)):.2f}% от {total_area:.2f}м\u00B2 и помещения кат. А,Б,В1-В3 оборуд. АУПТ')
                            cat_build = 'Г'
                            return cat_build, cause
                        else:
                            cause = (
                                f'Площадь помещений кат. А, Б, В1-В3 и Г: {(a + b + v + g):.2f}м\u00B2 ≥ 5000 м\u00B2 и помещения кат. А,Б,В1-В3 оборуд. АУПТ')
                            cat_build = 'Г'
                            return cat_build, cause
                    else:
                        return None, None
                else:
                    cause = (
                        f'Площадь помещений кат. А, Б, В1-В3 и Г: {(a + b + v + g):.2f}м\u00B2 сост. {100/(total_area/(a + b + v + g)):.2f}% от {total_area:.2f}м\u00B2 и помещения кат. А,Б,В1-В3 не оборуд. АУПТ')
                    cat_build = 'Г'
                    return cat_build, cause

            else:
                return None, None
        else:
            return None, None

        if a == 0 and b > 0 and v > 0:
            if (b + v + g) >= area_percent_5:
                if all(efs_b + efs_v):
                    if ((b + v + g) >= area_percent_25) or ((b + v + g) >= 5000):
                        if ((b + v + g) >= area_percent_25):
                            cause = (
                                f'Площадь помещений кат. Б, В1-В3 и Г: {(b + v + g):.2f}м\u00B2 сост. {100/(total_area/(b + v + g)):.2f}% от {total_area:.2f}м\u00B2 и помещения кат. Б,В1-В3 оборуд. АУПТ')
                            cat_build = 'Г'
                            return cat_build, cause
                        else:
                            cause = (
                                f'Площадь помещений кат. Б, В1-В3 и Г: {(b + v + g):.2f}м\u00B2 ≥ 5000 м\u00B2 и помещения кат. Б,В1-В3 оборуд. АУПТ')
                            cat_build = 'Г'
                            return cat_build, cause
                    else:
                        return None, None
                else:
                    cause = (
                        f'Площадь помещений кат. Б, В1-В3 и Г: {(b + v + g):.2f}м\u00B2 сост. {100/(total_area/(b + v + g)):.2f}% от {total_area:.2f}м\u00B2 и помещения кат. Б,В1-В3 не оборуд. АУПТ')
                    cat_build = 'Г'
                    return cat_build, cause
            else:
                return None, None
        else:
            return None, None

        if a == 0 and b == 0 and v > 0:
            if (v + g) >= area_percent_5:
                if all(efs_v):
                    if ((v + g) >= area_percent_25) or ((v + g) >= 5000):
                        if ((v + g) >= area_percent_25):
                            cause = (
                                f'Площадь помещений кат. В1-В3 и Г: {(v + g):.2f}м\u00B2 сост. {100/(total_area/(v + g)):.2f}% от {total_area:.2f}м\u00B2 и помещения кат. В1-В3 оборуд. АУПТ')
                            cat_build = 'Г'
                            return cat_build, cause
                        else:
                            cause = (
                                f'Площадь помещений кат. В1-В3 и Г: {(v + g):.2f}м\u00B2 ≥ 5000 м\u00B2 и помещения кат. В1-В3 оборуд. АУПТ')
                            cat_build = 'Г'
                            return cat_build, cause
                    else:
                        return None, None
                else:
                    cause = (
                        f'Площадь помещений кат. В1-В3 и Г: {(v + g):.2f}м\u00B2 сост. {100/(total_area/(v + g)):.2f}% от {total_area:.2f}м\u00B2 и помещения кат. В1-В3 не оборуд. АУПТ')
                    cat_build = 'Г'
                    return cat_build, cause
            else:
                return None, None
        else:
            return None, None

    def get_init_data_table(self, *args):
        log.info("Определение категории здания по пожарной опасности")

        a = float(args[0].get('area', 0))
        b = float(args[1].get('area', 0))
        v1 = float(args[2].get('area', 0))
        v2 = float(args[3].get('area', 0))
        v3 = float(args[4].get('area', 0))
        v4 = float(args[5].get('area', 0))
        g = float(args[6].get('area', 0))
        d = float(args[7].get('area', 0))

        label = 'Категория здания по пожарной опасности'
        headers = ("Наименование помещения",
                   "Площадь, м\u00B2", "АУПТ")

        area = []
        nums = len(list(args))
        for num in range(nums):
            area.append(float(args[num].get('area', 0)))
        area = sum(area)

        data = [
            {'id': 'Общая площадь помещений\nв здании или сооружении',
                'var': f'{area:.2f}', 'unit_1': '-'},
            {'id': 'Помещения категории Д', 'var': d, 'unit_1': '-'},
            {'id': 'Помещения категории Г', 'var': g, 'unit_1': '-'},
            {'id': 'Помещения категории В4', 'var': v4, 'unit_1': '-'},
            {'id': 'Помещения категории В3', 'var': v3, 'unit_1': 'Да' if args[4].get(
                'efs', 'True') == 'True' and v3 > 0 else '-'},
            {'id': 'Помещения категории В2', 'var': v2, 'unit_1': 'Да' if args[3].get(
                'efs', 'True') == 'True' and v2 > 0 else '-'},
            {'id': 'Помещения категории В1', 'var': v1, 'unit_1': 'Да' if args[2].get(
                'efs', 'True') == 'True' and v1 > 0 else '-'},
            {'id': 'Помещения категории Б', 'var': b, 'unit_1': 'Да' if args[1].get(
                'efs', 'True') == 'True' and b > 0 else '-'},
            {'id': 'Помещения категории А', 'var': a, 'unit_1': 'Да' if args[0].get('efs', 'True') == 'True' and a > 0 else '-'}]
        return data, headers, label

    def get_category_build(self, *args, total_area: int | float = None, **kwargs):
        a, b, v, g, other, efs_a, efs_b, efs_v = self.calc_area_premises(
            *args)
        cat_build = ''
        if total_area is None:
            total_area = a + b + v + g + other

        if a > 0 and b >= 0:
            cat_build, cause = self._check_category_a(
                a=a, efs_a=efs_a, total_area=total_area)
            log.info(f'Проверка кат.А: {cat_build} {cause}')

        if a == 0 and b > 0:
            cat_build, cause = self._check_category_b(
                a=a, b=b, efs_a=efs_a, efs_b=efs_b, total_area=total_area)
            log.info(f'Проверка кат.Б: {cat_build} {cause}')

        if (cat_build is None or cat_build == '') and a >= 0 and b > 0:
            cat_build, cause = self._check_category_b(
                a=a, b=b, efs_a=efs_a, efs_b=efs_b, total_area=total_area)
            log.info(f'Проверка кат.Б: {cat_build} {cause}')

        if (cat_build is None or cat_build == '') and v > 0:
            cat_build, cause = self._check_category_v(
                a=a, b=b, v=v, efs_a=efs_a, efs_b=efs_b, efs_v=efs_v, total_area=total_area)
            log.info(f'Проверка кат.B: {cat_build} {cause}')

        if (cat_build is None or cat_build == '') and g > 0:
            cat_build, cause = self._check_category_g(
                a=a, b=b, v=v, g=g, efs_a=efs_a, efs_b=efs_b, efs_v=efs_v, total_area=total_area)
            log.info(f'Проверка кат.Г: {cat_build} {cause}')

        if (cat_build is None or cat_build == ''):
            cause = 'Здание не относится к кат. А, Б, В или Г'
            cat_build = 'Д'
            log.info(f'Проверка кат.Д: {cat_build} {cause}')
        return cat_build, cause


class FireCategoryOutInstall(FireHazardCategory):
    """Опеределение Категории по взрывопожароопасности по СП 12.13130 наружной установки"""

    def __init__(self, substance="Пропилен", type_obj="out_inst"):
        super().__init__(type_obj=type_obj)
        self.substance: str = substance

    def get_init_data_table(self) -> list[dict]:
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

        label = 'Категория наружной установки'
        headers = ('Параметр', 'Значение', 'Ед.изм.')
        data = [
            {'id': 'Время закрытия задвижек',
                'var': valve_closing_time, 'unit_1': 'с'},
            {'id': 'Диаметр', 'var': diameter_outlet_pipeline, 'unit_1': 'м'},
            {'id': 'Длина', 'var':  lenght_outlet_pipeline, 'unit_1': 'м'},
            {'id': 'Тип трубопровода', 'var': outlet_pipeline, 'unit_1': '-'},
            {'id': 'Диаметр', 'var': diameter_inlet_pipeline, 'unit_1': 'м'},
            {'id': 'Длина', 'var': lenght_inlet_pipeline, 'unit_1': 'м'},
            {'id': 'Тип трубопровода', 'var': inlet_pipeline, 'unit_1': '-'},
            {'id': 'Объем', 'var': volume_container, 'unit_1': 'м\u00B3'},
            {'id': 'Тип емкости', 'var': type_container, 'unit_1': '-'},
            {'id': 'Плотность газа',
                'var': density_substance, 'unit_1': 'кг/м\u00B3'},
            {'id': 'Температура газа', 'var': temperature_substance, 'unit_1': '\u00B0С'},
            {'id': 'Давление газа', 'var': pressure_substance, 'unit_1': 'кПа'},
            {'id': 'Удельная теплота сгорания',
                'var': heat_of_burn, 'unit_1': 'кДж/кг'},
            {'id': 'Молярная масса', 'var': molar_mass, 'unit_1': 'кг/кмоль'},
            {'id': 'Агрегатное состояние', 'var': physical_state, 'unit_1': '-'},
            {'id': 'Вещество', 'var': self.substance, 'unit_1': '-'}]

        return data, headers, label

    def get_fire_hazard_categories(self) -> str:
        # category = FireHazardCategory.get_fire_category("out_inst")
        # property_sub = self.get_property_sub()
        type_substance = "ГГ"
        temperature_flash = 0           # С
        burn_in_oxigen = False
        fire_risk = 10 ** -7            # 1/год
        excessive_pressure_30m = 6      # кПа
        heat_flow_30m = 5               # кВт/м\u00B2
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


class FireCategoryPremises:
    def __init__(self, room: RoomModel, init_temperature: int | float = 20) -> None:
        self.pressure_ambient = physical_constants.get(
            'standard atmosphere')[0]  # Па
        self.heat_capacity_air = 1010  # Дж/кг*К
        self.R = physical_constants.get('molar gas constant')[0]  # Дж/моль*К
        self.K = 273.15  # К
        self.g = physical_constants.get('standard acceleration of gravity')[0]
        self.sound_speed = 340
        self.init_temperature = init_temperature
        self.room: RoomModel = room

    def get_lim_distance_from_heat_flux(self, heat_flux: int | float):
        log.info(f'heat_flux: {heat_flux}')
        data = interp1d(
            [5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0],
            [12, 8, 6, 5, 4, 3.8, 3.2, 2.8],
            kind='linear', bounds_error=False, fill_value='extrapolate'
            # fill_value=(12.0, 2.8)
        )  # Предельное расстояние в зависимости от критического значения теплового потока, м
        return data(heat_flux)

    def compute_lim_distance(self, height: int | float, distance: int | float):
        state_material = 'solid'
        if state_material == 'solid':
            if height >= 11:
                return distance
            else:
                return distance + (11 - height)
        elif state_material == 'liquid':
            if height >= 11:
                return 15
            else:
                return 26 - height

    def compute_criteria_fire_load_and_height(self, gt: int | float, height: int | float):
        return 0.64 * gt * height ** 2

    def compute_fire_load_per_unit_area(self, Q: list[int | float], area: int | float = 10):
        # area_room = self.room.area
        # log.info(f'Q: {Q}')
        g = []
        i = 0
        for sec in self.room.sections:
            # log.info(f'sec: {sec}')
            for i in range(len(sec.material)):
                _area_sec = sec.section_area
                log.info(f'area_sec: {_area_sec}, i: {i}')

                if area <= 10:
                    g.append(Q[i] / 10)
                else:
                    g.append(Q[i] / _area_sec)
            i += 1
        return g, sum(g)

    def compute_fire_load_in_section(self):
        Q = []
        i = 0
        for section in self.room.sections:
            if len(section.mass) > 1:
                for i in range(len(section.mass)):
                    _mass = section.mass[i]
                    _Q = section.material[i].lower_heat_of_combustion
                    Q.append(_Q * _mass)
                    # Q1.append(10)
            else:
                _mass = section.mass[-1]
                _Q = section.material[-1].lower_heat_of_combustion
                Q.append(_Q * _mass)
            i += 1
        return Q, sum(Q)

    def get_result_check_category(self, pre_cat: int, Q: int | float, gt: int | float, height: int | float):
        _condition = self.compute_criteria_fire_load_and_height(
            gt=gt, height=height)
        if pre_cat == 3 and Q < _condition:
            return 3
        elif (pre_cat == 3 and Q >= _condition) or (pre_cat == 2 and Q < _condition):
            return 2
        elif (pre_cat == 2 and Q >= _condition) or pre_cat == 1:
            return 1

    def get_fire_hazard_category(self) -> str:
        log.info('Запрос: Определение категории помещения В1-В4')
        cat_data = {1: 'В1', 2: 'В2', 3: 'В3', 4: 'В4', '-': None}
        category = []
        Q, Qs = self.compute_fire_load_in_section()
        g, gt = self.compute_fire_load_per_unit_area(Q=Q)
        i = 0
        j = 0
        log.info(f'g[i]: {g}, Q: {Q}')
        for sec in self.room.sections:
            print(sec, i)
            log.info(f'g[{i}]: {g[i]}, Q: {Q}')
            if g[i] > 0 and g[i] <= 180:
                l0 = sec.distance_to_section if len(sec.mass) > 1 else 1000
                l1 = self.get_lim_distance_from_heat_flux(
                    heat_flux=sec.material[j].critical_heat_flux)
                l2 = self.compute_lim_distance(
                    height=sec.distance_to_ceiling, distance=l1)
                log.info(f'l0:{l0}, l1:{l1}, l2: {l2}')

                if sec.share_fire_load_area <= 10 and l0 >= l2:
                    log.info(f'lпр:{l2}')
                    category.append(4)

                elif g[i] > 0 and g[i] <= 1400:
                    pre_category = 3
                    cat = self.get_result_check_category(
                        pre_cat=pre_category, Q=Q[i], gt=1400, height=sec.distance_to_ceiling)
                    category.append(cat)

                elif g[i] > 1400 and g[i] <= 2200:
                    pre_category = 2
                    cat = self.get_result_check_category(
                        pre_cat=pre_category, Q=Q[i], gt=2200, height=sec.distance_to_ceiling)
                    category.append(cat)

                else:
                    pre_category = 1
                    cat = self.get_result_check_category(
                        pre_cat=pre_category, Q=Q[i], gt=22000, height=sec.distance_to_ceiling)
                    category.append(cat)

            elif g[i] > 0 and g[i] <= 1400:
                pre_category = 3
                cat = self.get_result_check_category(
                    pre_cat=pre_category, Q=Q[i], gt=1400, height=sec.distance_to_ceiling)
                category.append(cat)

            elif g[i] > 1400 and g[i] <= 2200:
                pre_category = 2
                cat = self.get_result_check_category(
                    pre_cat=pre_category, Q=Q[i], gt=2200, height=sec.distance_to_ceiling)
                category.append(cat)

            else:
                pre_category = 1
                cat = self.get_result_check_category(
                    pre_cat=pre_category, Q=Q[i], gt=22000, height=sec.distance_to_ceiling)
                category.append(cat)
            # else:
            #     category.append(1)
            i += 1

        result_cat = cat_data.get(min(category), '-')
        log.info(
            f'\nПожарная нагрузка: Q= {Qs} МДж\n'
            f'Удельная пожарная нагрузка: g= {gt} МДж/м2\n'
            f'Категория: {result_cat}'
        )
        return Qs, gt, result_cat

    def get_explosion_and_fire_hazard_category(self) -> str:
        pass
