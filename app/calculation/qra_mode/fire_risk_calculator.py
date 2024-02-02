import logging
import json


log = logging.getLogger(__name__)


class FireRiskPublic:
    def __init__(self):
        pass

    def get_frequency_of_fire(self):
        area_from_scenario = 1000
        frequency_fire = area_from_scenario * 0.04
        return frequency_fire

    def get_probability_of_presence(self):
        days_in_year = 365
        work_time = 12
        quantity_work_day_in_year = 337
        probability_of_presence = (337 * 12)/(365 * 24)
        return probability_of_presence

    def get_probability_of_evacuation(self):
        emergency_exits = True
        if emergency_exits:
            coef_emerg_exit = 0.03
        else:
            coef_emerg_exit = 0.001

        coef_evacuation = 0.999

        probability_of_evacuation = 1 - \
            (1 - coef_evacuation) * (1 - coef_emerg_exit)

        return probability_of_evacuation

    def get_probability_fire_protection_system(self):
        coef_ext_system = 0.9
        coef_fire_alarm_system = 0.8
        coef_evacuation_controls_system = 0.8
        coef_space_planning_solutions = 0.8

        probability_fire_protection_system = 1 - ((1-coef_ext_system) *
                                                  (1-coef_fire_alarm_system) *
                                                  (1-coef_evacuation_controls_system) *
                                                  (1-coef_space_planning_solutions))
        return probability_fire_protection_system

    def probability_of_human_damage(self):
        probability_of_human_damage = 1
        return probability_of_human_damage

    def potential_fire_risk(self):
        potential_fire_risk = 1
        return potential_fire_risk

    def individual_fire_risk(self):
        individual_fire_risk = 1
        return individual_fire_risk


class FireRiskIndustrial:
    def __init__(self):
        pass

    def get_frequency_of_fire(self):
        area_from_scenario = 1000
        frequency_fire = area_from_scenario * 0.04
        return frequency_fire

    def get_probability_of_presence(self):
        days_in_year = 365
        work_time = 12
        quantity_work_day_in_year = 337
        probability_of_presence = (337 * 12)/(365 * 24)
        return probability_of_presence

    def get_probability_of_evacuation(self):
        emergency_exits = True
        if emergency_exits:
            coef_emerg_exit = 0.03
        else:
            coef_emerg_exit = 0.001

        coef_evacuation = 0.999

        probability_of_evacuation = 1 - \
            (1 - coef_evacuation) * (1 - coef_emerg_exit)

        return probability_of_evacuation

    def get_probability_fire_protection_system(self):
        coef_ext_system = 0.9
        coef_fire_alarm_system = 0.8
        coef_evacuation_controls_system = 0.8
        coef_space_planning_solutions = 0.8

        probability_fire_protection_system = 1 - ((1-coef_ext_system) *
                                                  (1-coef_fire_alarm_system) *
                                                  (1-coef_evacuation_controls_system) *
                                                  (1-coef_space_planning_solutions))
        return probability_fire_protection_system

    def probability_of_human_damage(self):
        probability_of_human_damage = 1
        return probability_of_human_damage

    def potential_fire_risk(self):
        potential_fire_risk = 1
        return potential_fire_risk

    def individual_fire_risk(self):
        individual_fire_risk = 1
        return individual_fire_risk


class FireRisk(FireRiskPublic, FireRiskIndustrial):
    def __init__(self, type_object=None):
        self.type_object: str = type_object
        if type_object == "Производственное":
            pass
        elif type_object == "Общественное":
            pass
        else:
            pass

    def calc_fire_risk(self, type_object: str):
        headers = ('Параметр', 'Значение', 'Ед.изм.')
        if type_object == 'industrial':
            label = 'Расчет пожарного риска для производственного здания'
            data = [
                {'id': 'Вероятность эффективного срабатывания\nустановок пожаротушения',
                    'var': "ptm", 'unit': 'мм'},
                {'id': 'Вероятность эффективного срабатывания\nсистемы противодымной защиты',
                    'var': "num_sides_heated", 'unit': 'шт'},
                {'id': 'Вероятность эффективного срабатывания\nпожарной сигнализации\nв сочетании с системой оповещения',
                    'var': "self.sketch", 'unit': '-'},
                {'id': 'Время нахождения людей на объекте',
                    'var': '1', 'unit': 'часы'},
                {'id': 'Вероятность эвакуации', 'var': '1', 'unit': '-'},
                {'id': 'Площадь помещения', 'var': '1', 'unit': 'м\u00B2'},
                {'id': 'Частота возникновения пожара', 'var': '1', 'unit': '-'}]
        else:
            label = 'Расчет пожарного риска для общественного здания'
            data = [
                {'id': 'Вероятность эффективного срабатывания\nустановок пожаротушения',
                    'var': "ptm", 'unit': 'мм'},
                {'id': 'Вероятность эффективного срабатывания\nсистемы противодымной защиты',
                    'var': "num_sides_heated", 'unit': 'шт'},
                {'id': 'Вероятность эффективного срабатывания\nпожарной сигнализации\nв сочетании с системой оповещения',
                    'var': "self.sketch", 'unit': '-'},
                {'id': 'Время нахождения людей на объекте',
                    'var': '1', 'unit': 'часы'},
                {'id': 'Вероятность эвакуации', 'var': '1', 'unit': '-'},
                {'id': 'Площадь помещения', 'var': '1', 'unit': 'м\u00B2'},
                {'id': 'Частота возникновения пожара', 'var': '1', 'unit': '-'}]

        return data, headers, label
