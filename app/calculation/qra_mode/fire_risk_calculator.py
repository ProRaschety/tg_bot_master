

class FireRiskCalc(type_object="Цех"):
    def __init__(self):
        self.type_object: str = type_object

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
