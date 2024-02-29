import logging


log = logging.getLogger(__name__)


class FireRisk:
    def __init__(self, type_obj: str, prob_evac: bool = False):
        self.type_obj = type_obj
        self.prob_evac = prob_evac

    def get_init_data(self, *args, **kwargs):
        head_risk = ('Наименование', 'Параметр', 'Значение', 'Ед.изм.')
        if self.type_obj == 'public':
            label_risk = 'Расчет пожарного риска. Методика 1140'
        else:
            label_risk = 'Расчет пожарного риска. Методика 404'
        if self.type_obj == 'public':
            probity_presence = self._calc_probity_presence(**kwargs)
            probity_evac = self._calc_probity_evacuation(**kwargs)
            data_risk = [
                {'id': 'Вероятность работы ПДЗ', 'var': 'Кпдз',
                    'unit_1': kwargs.get('k_smoke_pub', 0.0), 'unit_2': '-'},
                {'id': 'Вероятность работы СОУЭ', 'var': 'Ксоуэ',
                    'unit_1': kwargs.get('k_evacuation_pub', 0.0), 'unit_2': '-'},
                {'id': 'Вероятность работы АПС', 'var': 'Кобн',
                    'unit_1': kwargs.get('k_alarm_pub', 0.0), 'unit_2': '-'},
                {'id': 'Вероятность работы АУП', 'var': 'Кап',
                    'unit_1': kwargs.get('k_efs_pub', 0.0), 'unit_2': '-'},
                {'id': 'Вероятность эвакуации\nиз здания', 'var': 'Рэ',
                    'unit_1': f"{probity_evac:.3f}", 'unit_2': '-'},
                {'id': 'Вероятность присутствия\nв части здания', 'var': 'Рпр',
                    'unit_1': f"{probity_presence:.3f}", 'unit_2': 'tпр/24'},
                {'id': 'Время присутствия\nв части здания', 'var': 'tпр',
                    'unit_1': kwargs.get('time_presence_pub', 0.000), 'unit_2': 'ч'},
                {'id': 'Частота возникновения пожара', 'var': 'Qп', 'unit_1': f"{float((kwargs.get('fire_freq_pub', 0.04))):.2e}", 'unit_2': '1/год'}]
        else:
            probity_presence = self._calc_probity_presence(**kwargs)
            probity_escape_exits = self._calc_probity_escape_exits(**kwargs)
            probity_evac = self._calc_probity_evacuation(**kwargs)
            data_risk = [
                # {'id': 'Индивидуальный риск в помещении', 'var': 'Rm',
                #     'unit_1': f'{ind_risk:.2e}', 'unit_2': '-'},
                # {'id': 'Потенциальный риск в помещении', 'var': 'Рi',
                #     'unit_1': f'{poten_risk:.2e}', 'unit_2': '-'},
                # {'id': 'Условная вероятность\nпоражения человека в i-ом помещении',
                #     'var': 'Qd', 'unit_1': f"{probity_dam:.3f}", 'unit_2': '-'},
                # {'id': 'Вероятность эффектиной работы\nсистем противопожарной защиты', 'var': 'Dijk',
                #     'unit_1': f"{probity_efs:.3f}", 'unit_2': '-'},
                {'id': 'Вероятность работы ПДЗ', 'var': 'Dпдз',
                    'unit_1': kwargs.get('k_smoke_ind', 0.8), 'unit_2': '-'},
                {'id': 'Вероятность работы СОУЭ', 'var': 'Dсоуэ',
                    'unit_1': kwargs.get('k_evacuation_ind', 0.8), 'unit_2': '-'},
                {'id': 'Вероятность работы АПС', 'var': 'Dапс',
                    'unit_1': kwargs.get('k_alarm_ind', 0.8), 'unit_2': '-'},
                {'id': 'Вероятность работы АПТ', 'var': 'Dапт',
                    'unit_1': kwargs.get('k_efs_ind', 0.9), 'unit_2': '-'},
                # {'id': 'Вероятность эвакуации из здания', 'var': 'Рэ',
                #     'unit_1': probity_evac, 'unit_2': '-'},
                {'id': 'Вероятность эвакуации\nчерез аварийные выходы', 'var': 'Рдв',
                    'unit_1': kwargs.get('emergency_escape_ind'), 'unit_2': '-'},
                {'id': 'Вероятность эвакуации\nпо эвакуационным путям', 'var': 'Рэп',
                    'unit_1': f"{probity_escape_exits:.3f}", 'unit_2': '-'},
                {'id': 'Расчетное время эвакуации', 'var': 'tр',
                    'unit_1': kwargs.get('time_evacuation_ind'), 'unit_2': 'сек'},
                {'id': 'Время блокирования путей эвакуации', 'var': 'tбл',
                    'unit_1': kwargs.get('time_blocking_paths_ind'), 'unit_2': 'сек'},
                {'id': 'Время начала эвакуации', 'var': 'tнэ',
                    'unit_1': kwargs.get('time_start_evacuation_ind'), 'unit_2': 'сек'},
                # {'id': 'Вероятность присутствия', 'var': 'Р',
                #     'unit_1': f"{(probity_presence):.3f}", 'unit_2': '-'},
                {'id': 'Количество рабочих дней в году', 'var': 'Nрд',
                    'unit_1': kwargs.get('working_days_per_year_ind', 30), 'unit_2': 'сутки'},
                {'id': 'Время присутствия работника\nв i-ом помещении здания', 'var': 'tпр',
                    'unit_1': kwargs.get('time_presence_ind', 0), 'unit_2': 'час/\nсутки'},
                # {'id': 'Частота возникновения\nпожара в здании', 'var': 'Q',
                #     'unit_1': f"{(fire_freq):.2e}", 'unit_2': '1/год'},
                {'id': 'Частота возникновения пожара', 'var': 'Q',
                 'unit_1': f"{(float(kwargs.get('fire_freq_ind', 0.04))):.2e}", 'unit_2': 'м\u00B2*1/год'},
                {'id': 'Площадь помещения', 'var': 'Sпом', 'unit_1': kwargs.get('area_ind', 100), 'unit_2': 'м\u00B2'}]

        return data_risk, head_risk, label_risk

    def get_result_data(self, *args, **kwargs):
        head_risk = ('Наименование', 'Параметр', 'Значение', 'Ед.изм.')
        if self.type_obj == 'public':
            label_risk = 'Расчет пожарного риска. Методика 1140'
        else:
            label_risk = 'Расчет пожарного риска. Методика 404'
        if self.type_obj == 'public':
            fire_freq = self._get_frequency_of_fire(**kwargs)
            coef_fire_protection = self._calc_probity_fire_protec_system(
                **kwargs)
            probity_presence = self._calc_probity_presence(**kwargs)
            probity_evac = self._calc_probity_evacuation(**kwargs)
            ind_risk = self.calc_fire_risk(
                self, *args, fire_frequency=fire_freq, **kwargs)
            data_risk = [
                # {'id': 'Индивидуальный пожарный риск\nc учетом противопожарных дверей', 'var': 'Ri',
                #     'unit_1': f'{(0.3 * ind_risk + 0.7 * ind_risk):.2e}', 'unit_2': f"{'Соотв.' if ind_risk < 0.000001 else 'Не соотв.'}"},
                {'id': 'Индивидуальный пожарный риск', 'var': 'Rij',
                    'unit_1': f'{ind_risk:.2e}', 'unit_2': f"{'Соотв.' if ind_risk < 0.000001 else 'Не соотв.'}"},
                {'id': 'Коэффициент соответствия СПЗ', 'var': 'Кпз',
                    'unit_1': f'{coef_fire_protection:.3f}', 'unit_2': '-'},
                {'id': 'Вероятность работы ПДЗ', 'var': 'Кпдз',
                    'unit_1': kwargs.get('k_smoke_pub', 0.0), 'unit_2': '-'},
                {'id': 'Вероятность работы СОУЭ', 'var': 'Ксоуэ',
                    'unit_1': kwargs.get('k_evacuation_pub', 0.0), 'unit_2': '-'},
                {'id': 'Вероятность работы АПС', 'var': 'Кобн',
                    'unit_1': kwargs.get('k_alarm_pub', 0.0), 'unit_2': '-'},
                {'id': 'Вероятность работы АУП', 'var': 'Кап',
                    'unit_1': kwargs.get('k_efs_pub', 0.0), 'unit_2': '-'},
                {'id': 'Вероятность эвакуации\nиз здания', 'var': 'Рэ',
                    'unit_1': f"{probity_evac:.3f}", 'unit_2': '-'},
                {'id': 'Вероятность присутствия\nв части здания', 'var': 'Рпр',
                    'unit_1': f"{probity_presence:.3f}", 'unit_2': 'tпр/24'},
                {'id': 'Время присутствия\nв части здания', 'var': 'tпр',
                    'unit_1': kwargs.get('time_presence_pub', 0.000), 'unit_2': 'ч'},
                {'id': 'Частота возникновения пожара', 'var': 'Qп', 'unit_1': f"{fire_freq:.2e}", 'unit_2': '1/год'}]
        else:
            fire_freq = self._get_frequency_of_fire(**kwargs)
            probity_efs = self._calc_probity_fire_protec_system(**kwargs)
            probity_presence = self._calc_probity_presence(**kwargs)
            probity_evac = self._calc_probity_evacuation(**kwargs)
            probity_dam = self._calc_probity_of_human_damage(
                probity_evac=probity_evac, probity_efs=probity_efs)
            poten_risk = self._calc_potential_fire_risk(
                probity_damage=probity_dam, fire_frequency=fire_freq)
            ind_risk = self.calc_fire_risk(
                self, *args, potencial_risk=poten_risk, probity_presence=probity_presence, **kwargs)
            data_risk = [
                {'id': 'Индивидуальный риск\nдля работника m в i-ом помещении', 'var': 'Rm',
                    'unit_1': f'{ind_risk:.2e}', 'unit_2': '-'},
                {'id': 'Потенциальный риск\nв i-ом помещении', 'var': 'Рi',
                    'unit_1': f'{poten_risk:.2e}', 'unit_2': '-'},
                {'id': 'Условная вероятность поражения \nработника в i-ом помещении',
                    'var': 'Qdij', 'unit_1': f"{probity_dam:.2e}", 'unit_2': '-'},
                {'id': 'Вероятность эффективной работы\nсистем противопожарной защиты', 'var': 'Dijk',
                    'unit_1': f"{probity_efs:.3f}", 'unit_2': '-'},
                {'id': 'Вероятность присутствия\nработника m в i-ом помещении', 'var': 'qim',
                    'unit_1': f"{probity_presence:.3f}", 'unit_2': '-'},
                {'id': 'Вероятность эвакуации из здания', 'var': 'Рэ',
                    'unit_1': f"{probity_evac:.3f}", 'unit_2': '-'},
                {'id': 'Частота реализации в течение года\nj-го сценария пожара', 'var': 'Qj',
                    'unit_1': f"{fire_freq:.2e}", 'unit_2': '1/год'},
                {'id': 'Вероятность работы ПДЗ', 'var': 'Dпдз',
                    'unit_1': kwargs.get('k_smoke_ind', 0.8), 'unit_2': '-'},
                {'id': 'Вероятность работы СОУЭ', 'var': 'Dсоуэ',
                    'unit_1': kwargs.get('k_evacuation_ind', 0.8), 'unit_2': '-'},
                {'id': 'Вероятность работы АПС', 'var': 'Dапс',
                    'unit_1': kwargs.get('k_alarm_ind', 0.8), 'unit_2': '-'},
                {'id': 'Вероятность работы АПТ', 'var': 'Dапт',
                    'unit_1': kwargs.get('k_efs_ind', 0.9), 'unit_2': '-'},
            ]
        return data_risk, head_risk, label_risk

    def _get_frequency_of_fire(self, **kwargs):
        if self.type_obj == 'public':
            frequency = float(kwargs.get('fire_freq_pub', 0.04))
        else:
            frequency = float(kwargs.get('fire_freq_ind', 0.04)) * \
                float(kwargs.get('area_ind', 100))
        return frequency

    def _calc_probity_presence(self, **kwargs):
        hours_day = 24
        days_in_year = 365

        if self.type_obj == 'public':
            probity_of_presence = float(
                kwargs.get('time_presence_pub', 0)) / hours_day
        else:
            work_time = float(kwargs.get('time_presence_ind', 0))
            quantity_work_day_in_year = float(
                kwargs.get('working_days_per_year_ind', 247))
            probity_of_presence = (
                quantity_work_day_in_year * work_time)/(days_in_year * hours_day)
        return probity_of_presence

    def _calc_probity_escape_exits(self, **kwargs):
        if self.prob_evac:
            probity_escape_exits = float(
                kwargs.get('probity_evacuation_ind'))
        else:
            time_evacuation = float(kwargs.get('time_evacuation_ind'))
            time_blocking_paths = float(
                kwargs.get('time_blocking_paths_ind'))
            time_start_evacuation = self._calc_time_start_evacuation(
                **kwargs)
            if time_evacuation >= (0.8 * time_blocking_paths):
                probity_escape_exits = 0.001
            elif ((time_evacuation + time_start_evacuation) <= (0.8 * time_blocking_paths)):
                probity_escape_exits = 0.999
            elif ((0.8 * time_blocking_paths) > time_evacuation) and ((0.8 * time_blocking_paths) < (time_evacuation + time_start_evacuation)):
                probity_escape_exits = 0.999 * \
                    ((0.8 * time_blocking_paths - time_evacuation) /
                        time_start_evacuation)
        return probity_escape_exits

    def _calc_probity_evacuation(self, start_evacuation: int | float = None, **kwargs):
        if self.type_obj == 'public':
            if self.prob_evac:
                probity_evacuation = float(
                    kwargs.get('probity_evacuation_pub'))
            else:
                probity_evacuation = float(
                    kwargs.get('probity_evacuation_pub'))
                time_evacuation = float(kwargs.get('time_evacuation_pub'))
                time_blocking_paths = float(
                    kwargs.get('time_blocking_paths_pub'))
                time_crowding = float(kwargs.get('time_crowding_pub'))

                if start_evacuation == None:
                    time_start_evacuation = self._calc_time_start_evacuation(
                        **kwargs)
                else:
                    time_start_evacuation = start_evacuation

                if time_evacuation >= (0.8 * time_blocking_paths) or time_crowding > 6:
                    probity_evacuation = 0.0
                elif ((0.8 * time_blocking_paths) > time_evacuation) and ((0.8 * time_blocking_paths) < (time_evacuation + time_start_evacuation)) and (time_crowding <= 6):
                    probity_evacuation = 0.999 * \
                        ((0.8 * time_blocking_paths - time_evacuation) /
                         time_start_evacuation)
                elif ((time_evacuation + time_start_evacuation) <= (0.8 * time_blocking_paths)) and (time_crowding <= 6):
                    probity_evacuation = 0.999
        else:
            probity_escape_exits = self._calc_probity_escape_exits(**kwargs)
            probity_evacuation = 1 - \
                ((1 - probity_escape_exits) *
                 (1 - float(kwargs.get('emergency_escape_ind', 0.0))))
        return probity_evacuation

    def _calc_time_start_evacuation(self, **kwargs):
        if self.type_obj == 'public':
            time_start = float(kwargs.get('time_start_evacuation_pub'))
            # time_start = 5 + 0.01 * float(kwargs.get('area_pub', 0.0))
        else:
            time_start = float(kwargs.get('time_start_evacuation_ind'))
        return time_start

    def _calc_probity_of_human_damage(self, probity_evac: int | float, probity_efs: int | float):
        if self.type_obj == 'public':
            probity_human_damage = 10
        else:
            probity_human_damage = (1 - probity_evac) * (1 - probity_efs)
        return probity_human_damage

    def _calc_potential_fire_risk(self, probity_damage: int | float, fire_frequency: int | float):
        if self.type_obj == 'public':
            poten_fire_risk = 1
        else:
            poten_fire_risk = round(fire_frequency, 6) * \
                round(probity_damage, 6)
        return poten_fire_risk

    def _calc_probity_fire_protec_system(self, **kwargs):
        if self.type_obj == 'public':
            probity_efs = 1 - (1 - float(kwargs.get('k_alarm_pub', 0.0)) * float(kwargs.get('k_evacuation_pub', 0.0))) * (
                1 - float(kwargs.get('k_alarm_pub', 0.0)) * float(kwargs.get('k_smoke_pub', 0.0)))
        else:
            probity_efs = 1 - ((1 - float(kwargs.get('k_alarm_ind', 0.8))) * (1 - float(kwargs.get('k_evacuation_ind', 0.8)))
                               * (1 - float(kwargs.get('k_smoke_ind', 0.8))) * (1 - float(kwargs.get('k_efs_ind', 0.9))))
        return probity_efs

    def calc_fire_risk(self, *args, potencial_risk: int | float = None, fire_frequency: int | float = None, probity_presence: int | float = None, **kwargs) -> int | float:
        if self.type_obj == 'public':
            k_efs = float(kwargs.get('k_efs_pub', 0))
            prob_presence = self._calc_probity_presence(**kwargs)
            probability_evacuation = self._calc_probity_evacuation(**kwargs)
            k_fps = self._calc_probity_fire_protec_system(**kwargs)
            fire_risk = fire_frequency * \
                (1 - k_efs) * prob_presence * \
                (1 - probability_evacuation) * (1 - k_fps)
        else:
            fire_risk = potencial_risk * probity_presence
        return fire_risk
