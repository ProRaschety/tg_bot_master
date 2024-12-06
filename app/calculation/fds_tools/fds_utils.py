import logging
import csv
import json

import matplotlib.pyplot as plt
# import math
# import numpy as np

# import sympy as sp
# from sympy import symbols, integrate

# import scipy.integrate as spi
# from scipy.integrate import quad

log = logging.getLogger(__name__)

# HRRPUA (Heat Release Rate per Unit Area).

# delta_hc = 48000  # теплота сгорания кДж/кг
# area = 10  # площадь горения м2

# HRRPUA = delta_hc * mi  # Максимальная удельная скорость тепловыделения, которую необходимо задать в поверхности типа «горелка»
# Q1(t) = 1  # зависимость номинальной (соответствующей полному сгоранию) мощности тепловыделения от времени.
# Q_i = Q1(t)/area  # Удельная мощность тепловыделения, задается в исходных данных параметром HRRPUA.
# m_i(t) = Qi/delta_hc  # скорость выгорания
# file_name_dict = r'D:\YandexDisk\Python_МетодМатериалы\db_fire_type.json'


class FDSTools:
    def __init__(self):
        self.name_flammable_load: str
        self.min_t: int = 0
        self.max_t: int = 180
        self.temperature_air: float = 293.0  # К
        self.__density_air = 1.204  # кг/м3
        self.__specific_heat_of_gas = 1.005  # кДж/кг*К
        self.__acceleration_of_gravity = 9.81  # м/с2

    def get_hrr_result(self):
        q_f = 650  # МДж/м2 Функциональная пожарная нагрузка
        q_n = 15.8  # МДж/кг Низшая теплота сгорания пожарной нагрузки
        psi_spec = 0.015  # кг/(м2*с) Удельная массовая скорость выгорания

        with open(file_name_dict, encoding='utf-8') as file_op:
            name_dict_in = json.load(file_op)
        name_type = "Wardrobe_5-FASTLite"  # Fire Type
        # fire_type = name_dict_in[name_type]
        num_dive = 200  # Divisions in Graph
        t_0 = name_dict_in[name_type]['t_0']
        t_l0 = name_dict_in[name_type]['t_l0']
        t_d = name_dict_in[name_type]['t_d']
        t_end = name_dict_in[name_type]['t_end']
        Q_dotmax = name_dict_in[name_type]['Q_dotmax']
        t_g = name_dict_in[name_type]['t_g']
        alpha_g = name_dict_in[name_type]['alpha_g']
        alpha_d = name_dict_in[name_type]['alpha_d']

        burnout_rate_of_the_combustible_load = 1
        # Время, при котором в центре пожара окажется зона выгорания
        t_hol = q_f / (q_n * psi_spec)
        psi = psi_spec * area_fire  # скорость выгорания горючей нагрузки
        eta = 0.93                  # коэффициент полноты горения
        lower_heat_comb = self.get_lower_heat_of_combustion()
        mass_burn_rate = self.get_specific_mass_burnout_rate()
        fire_area = self.get_area_of_fire()

        hrr_fire = eta * lower_heat_comb * psi

        return hrr_fire

    def get_functional_fire_load(self):
        functional_fire_load = 650  # МДж/м2 Функциональная пожарная нагрузка
        return functional_fire_load

    def get_placement_area(self):
        # м2 Площадь размещения ГН (или помещения очага пожара)
        placement_area = 1
        return placement_area

    def get_lower_heat_of_combustion(self):
        lower_heat_of_combustion = 15.8  # МДж/кг Низшая теплота сгорания пожарной нагрузки
        return lower_heat_of_combustion

    def get_specific_mass_burnout_rate(self):
        # кг/(м2*с) Удельная массовая скорость выгорания
        specific_mass_burnout_rate = 0.015
        return specific_mass_burnout_rate

    def get_linear_flame_propagation_velocity(self):
        # м/с Линейная скорость распространения пламени
        linear_flame_propagation_velocity = 0.0055
        return linear_flame_propagation_velocity

    def get_area_of_fire(self):
        linear_vel = self.get_linear_flame_propagation_velocity()
        area_of_the_fire = []
        for t in range(self.min_t, self.max_t):
            area_of_the_fire.append(3.14 * linear_vel ** 2 * t ** 2)
        return area_of_the_fire

    def get_burn_out_rate_of_flammable_load(self):
        burn_out_rate_of_flammable_load = 1
        return burn_out_rate_of_flammable_load

    def get_plot_fire_mod(self):
        graphic_fire = 1
        data_plot = self.get_area_of_fire()
        x_axes = range(self.min_t, self.max_t)
        y_axes = data_plot
        plt.plot(x_axes, y_axes, "--")
        plt.xlabel("Время, мин")
        plt.ylabel("Мощность пожара, кВт")
        plt.xlim(xmax=200)
        plt.ylim(ymax=5)
        plt.grid()
        plt.show()
        return graphic_fire

    def get_charact_diameter_of_fire(self):
        max_HRR = 675  # кВт
        charact_diameter_of_fire = (max_HRR/(self.__density_air * self.__specific_heat_of_gas *
                                    self.temperature_air * (self.__acceleration_of_gravity ** 0.5))) ** (2/5)
        return charact_diameter_of_fire

    def get_size_of_cubic_grid_cell(self):
        above_d = self.get_charact_diameter_of_fire()
        norm_grid_multiplier = 5
        size_of_cubic_grid_cell = above_d / norm_grid_multiplier

        return size_of_cubic_grid_cell

    def clean_and_convert_float(self, number_str):
        number_str = number_str.strip().split(' ')[0]
        return float(number_str.replace(',', '.'))

    def parse_evac_time(self, line):
        return self.clean_and_convert_float(line.split(':')[1])

    def compute_deltas(self, evac_times, density_threshold):
        deltas = []
        first_time_exceeded = None
        last_time_exceeded = None
        for time, max_density in evac_times:

            if max_density >= density_threshold:
                if first_time_exceeded is None:
                    first_time_exceeded = time
                last_time_exceeded = time
                delta = time - \
                    evac_times[-1][0] if evac_times[-1][1] >= density_threshold else 0.2

            else:
                delta = 0

            deltas.append(delta)

        return sum(deltas), first_time_exceeded, last_time_exceeded

    def compute_human_densities(self, file_paths, density_threshold=0.5):
        evac_times = []
        current_max_density = 0.0
        time = None
        with open(file_paths, newline='', encoding="utf-8") as file:
            reader = csv.reader(file, delimiter='\t')
            first_line = True

            for row in reader:
                if not row or first_line:
                    first_line = False
                    continue
                first_cell = row[0]
                if 'EvacuationTime' in first_cell:
                    time = self.parse_evac_time(first_cell)
                    evac_times.append((time, current_max_density))
                    current_max_density = 0
                elif len(row) > 4 and row[4] != 'Density':
                    try:
                        density = self.clean_and_convert_float(row[4])
                        if density > current_max_density:
                            current_max_density = density
                    except ValueError:
                        pass

            if current_max_density > 0 and time is not None:
                evac_times.append((time, current_max_density))

        total_delta_sum, first_time_exceeded, last_time_exceeded = self.compute_deltas(
            evac_times, density_threshold)

        return evac_times, total_delta_sum, first_time_exceeded, last_time_exceeded

    def open_file(self, file_paths):
        log.info("Утилита FDS. График плотности людского потока")
        density_threshold = 0.5
        evac_times, total_delta_sum, first_time_exceeded, last_time_exceeded = self.compute_human_densities(
            file_paths, density_threshold)

        if total_delta_sum < 0:
            total_delta_sum = 0

        try:
            times, densities = zip(*evac_times)
            return times, densities, total_delta_sum
        except ValueError:
            evac_times = [(0.0, 0.0), (0.3, 0.1),
                          (0.6, 0.1), (0.9, 0.0)]
            times, densities = zip(*evac_times)
            return times, densities, 0.0
