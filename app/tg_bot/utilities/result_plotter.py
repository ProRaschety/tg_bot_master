import logging
# import re
# import os
# import csv
# import io
# import pandas as pd
# import numpy as np
# import inspect
# from typing import Any

# import matplotlib.pyplot as plt
# import matplotlib.patches as patches
# import matplotlib.gridspec as gridspec
# from matplotlib import font_manager as fm, rcParams
# from matplotlib.offsetbox import OffsetImage, AnnotationBbox
# from matplotlib import font_manager
# from datetime import datetime


from fluentogram import TranslatorRunner

# from datetime import datetime
from app.calculation.physics.accident_parameters import AccidentParameters
from app.infrastructure.database.models.calculations import AccidentModel
from app.infrastructure.database.models.substance import FlammableMaterialModel, SubstanceModel

from app.calculation.physics.physics_utils import compute_characteristic_diameter, compute_density_gas_phase, compute_density_vapor_at_boiling, compute_stoichiometric_coefficient_with_fuel, compute_stoichiometric_coefficient_with_oxygen
from app.calculation.qra_mode import probits
from app.calculation.utilities import misc_utils

# from app.tg_bot.utilities.misc_utils import get_picture_filling, get_data_table, get_plot_graph, get_dataframe_table
# from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb

from app.tg_bot.models.tables import DataFrameModel
from app.tg_bot.models.plotter import DataPlotterModel

# from pprint import pprint

log = logging.getLogger(__name__)


# class DataPlotter:
#     def __init__(self, data):
#         self.data = data

#     def plot_graph(self):
#         x = [item[0] for item in self.data]
#         y = [item[1] for item in self.data]

#         plt.plot(x, y)
#         plt.xlabel('X-axis')
#         plt.ylabel('Y-axis')
#         plt.title('Data Plot')
#         plt.grid(True)
#         plt.show()


# # Пример использования класса
# data = [(1, 2), (2, 4), (3, 6), (4, 8)]
# plotter = DataPlotter(data)
# plotter.plot_graph()


# class DataPlotter:
#     def __init__(self, data):
#         self.data = data

#     def plot_graph(self, annotations=None):
#         plt.figure()
#         for line_data in self.data:
#             x = [item[0] for item in line_data]
#             y = [item[1] for item in line_data]
#             plt.plot(x, y)

#         plt.xlabel('X-axis')
#         plt.ylabel('Y-axis')
#         plt.title('Data Plot')

#         if annotations:
#             for annotation in annotations:
#                 plt.annotate(annotation['text'], (annotation['x'], annotation['y']), xytext=(
#                     10, 10), textcoords='offset points', arrowprops=dict(arrowstyle="->"))

#         plt.grid(True)
#         plt.show()


# # Пример использования класса с несколькими линиями
# data = [[(1, 2), (2, 4), (3, 6), (4, 8)], [(1, 3), (2, 6), (3, 9), (4, 12)]]
# annotations = [{'x': 2, 'y': 4, 'text': 'Point 1'},
#                {'x': 3, 'y': 6, 'text': 'Point 2'}]
# plotter = DataPlotter(data)
# plotter.plot_graph(annotations)

class DataPlotter:
    def __init__(self, i18n: TranslatorRunner,
                 request: str,
                 substance: FlammableMaterialModel | SubstanceModel = None,
                 #  flammable_material: FlammableMaterialModel = None,
                 model: AccidentModel = None
                 ) -> None:

        self.i18n = i18n
        self.request = request
        # self.flammable_material = flammable_material
        # self.accident_model = accident_model
        self.accident_model = model
        self.substance = substance if substance is not None else self.accident_model.substance

        log.info(f'Request dataplotter: {self.i18n.get(request)}')

    def _create_2d_array(self, rows: int = 10, cols: int = 4):
        label: str = self.i18n.get('unknown_request')
        headers = ['', '', '', '']
        array_2d = []
        for _ in range(rows + 1):
            row = []
            for _ in range(cols):
                row.append('')
            array_2d.append(row)
        return DataFrameModel(label=label, headers=headers, dataframe=array_2d)

    def action_request_admins(self):
        admins_actions = {
            # команды администратора
            # ('handbooks', ''): self.,
            # ('', ''): self.,
            # (): self.,
            # (): self.,
            # (): self.,
        }

        if self.request in admins_actions:
            return admins_actions[self.request]()
        else:
            for key in admins_actions:
                if self.request in key:
                    return admins_actions[key]()
        return self._create_2d_array()

    def action_request_reports(self):
        reports_actions = {
            # отчеты и протоколы расчетов
            # ('handbooks', ''): self.,
            # ('', ''): self.,
            # (): self.,
            # (): self.,
            # (): self.,
        }

        if self.request in reports_actions:
            return reports_actions[self.request]()
        else:
            for key in reports_actions:
                if self.request in key:
                    return reports_actions[key]()
        return self._create_2d_array()

    def action_request(self):
        actions = {
            # типовые аварии
            # ('plot_fire_flash', 'probit_fire_flash'): self.get_dataframe_from_fire_flash,
            ('plot_fire_pool', 'probit_fire_pool'): self.get_plot_from_fire_pool,
            ('plot_accident_cloud_explosion_pressure', 'plot_accident_cloud_explosion_impuls'): self.get_plot_from_cloud_explosion,
            # ('horizontal_jet', 'vertical_jet'): self.get_dataframe_from_jet_flame,
            ('plot_fire_ball', 'probit_fire_ball'): self.get_plot_from_fire_ball,
            ('plot_accident_bleve_pressure', 'plot_accident_bleve_impuls'): self.get_plot_from_accident_bleve,

            # категорирование
            # ('category_build', 'run_category_build'): self.get_dataframe_from_category_build,
            # ('category_premises', 'run_category_premises'): self.get_dataframe_from_category_premises,
            # ('category_external_installation', 'run_category_external_installation'): self.get_dataframe_from_category_external_installation,

            # расчет ОФП
            # ('analytics_model', 'run_analytics_model'): self.get_dataframe_from_analytics_model,

            # калькуляторы риска
            # ('public', 'run_public'): self.,
            # ('industrial', 'run_industrial'): self.,

            # огнестойкость
            # ('strength_calculation', 'run_strength_steel'): self.get_dataframe_from_strength_calculation_steel,
            # ('thermal_calculation', 'run_thermal_steel'): self.get_dataframe_from_thermal_calculation_steel,

            # инструменты
            # ('tool_liquid', 'run_tool_liquid'): self.,
            # ('tool_comp_gas', 'run_tool_comp_gas'): self.,
            # ('tool_liq_gas', ''): self.,
            # ('tool_evaporation_rate', ''): self.,

            # утилиты FDS
            # ('fds_tools_density', ''): self.,
            # ('', ''): self.,
            # ('', ''): self.,

            # справочники
            # ('handbooks', ''): self.,
            # ('climate', ''): self.,
            # ('frequencies', 'table_404'): self.,
            # ('type_to_table_1_3', 'type_to_table_2_3', 'type_to_table_2_4'): self.,
            # ('standard_flammable_load', 'analytics_model_flammable_load'): self.,

            # ('', ''): self.,
            # (): self.,
            # (): self.,
            # (): self.,
        }

        if self.request in actions:
            return actions[self.request]()
        else:
            for key in actions:
                if self.request in key:
                    return actions[key]()
        return self._create_2d_array()

    def get_plot_from_fire_pool(self):
        i18n = self.i18n
        accident_model = self.accident_model
        substance = self.substance

        distance = accident_model.pool_distance
        diameter = compute_characteristic_diameter(
            area=accident_model.pool_area)
        air_density = compute_density_gas_phase(
            molar_mass=28.97, temperature=accident_model.air_temperature)
        fuel_density = compute_density_vapor_at_boiling(molar_mass=substance.molar_mass,
                                                        boiling_point=substance.boiling_point)

        f_pool = AccidentParameters()
        nonvelocity = f_pool.compute_nonvelocity(
            wind=accident_model.velocity_wind, density_fuel=fuel_density, mass_burn_rate=substance.mass_burning_rate, eff_diameter=diameter)
        flame_angle = f_pool.get_flame_deflection_angle(
            nonvelocity=nonvelocity)
        flame_lenght = f_pool.compute_lenght_flame_pool(
            nonvelocity=nonvelocity, density_air=air_density, mass_burn_rate=substance.mass_burning_rate, eff_diameter=diameter)
        sep = f_pool.compute_surface_emissive_power(
            eff_diameter=diameter, subst=accident_model.substance_name)
        x, y = f_pool.compute_heat_flux(
            eff_diameter=diameter, sep=sep, lenght_flame=flame_lenght, angle=flame_angle)

        if self.request == 'plot_fire_pool':
            x_4_kW = misc_utils.get_distance_at_value(
                x_values=x, y_values=y, value=4.0)

            sep_num = misc_utils.get_value_at_distance(
                x_values=x, y_values=y, distance=distance + diameter / 2)

            unit_sep = i18n.get('kwatt_per_meter_square')
            text_annotate = f"q({distance + diameter / 2:.1f})= {sep_num:.1f} {unit_sep}"
            plot_label = i18n.eq_heat_flux()
            label = i18n.get('plot_pool_label')

            return DataPlotterModel(
                x_values=x, y_values=y, ylim=max(y) + max(y) * 0.05,
                add_annotate=True, text_annotate=text_annotate, x_ann=distance + diameter / 2, y_ann=sep_num,
                label=label, x_label=i18n.get('distance_label'), y_label=i18n.get('y_pool_label'),
                add_legend=True, loc_legend=1,
                plot_label=plot_label
            )

        else:
            x, y = probits.compute_thermal_fatality_prob_for_plot(
                type_accident='fire_pool', x_val=x, heat_flux=y, eff_diameter=diameter)
            # dist_num = f_pool.get_distance_at_sep(x_values=x, y_values=y, sep=4)
            # sep_num = f_pool.get_sep_at_distance(
            #     x_values=x, y_values=y, distance=distance + diameter / 2)

            value = misc_utils.get_value_at_distance(
                x_values=x, y_values=y, distance=distance + diameter / 2)
            # unit_sep = i18n.get('kwatt_per_meter_square')
            unit_sep = ''
            text_annotate = f"Q({distance + diameter / 2:.1f})= {value:.1e} {unit_sep}"

            plot_label = i18n.eq_heat_flux()
            return DataPlotterModel(x_values=x, y_values=y, ylim=max(y) + max(y) * 0.05, ymin=-0.01,
                                    add_annotate=True, text_annotate=text_annotate, x_ann=distance + diameter / 2, y_ann=value,
                                    label=i18n.get('plot_probit_label'), x_label=i18n.get('distance_label'), y_label=i18n.get('y_probit_label'),
                                    add_legend=False, loc_legend=1,
                                    plot_label=plot_label)

    def get_plot_from_fire_ball(self):
        i18n = self.i18n
        accident_model = self.accident_model
        mass = accident_model.fire_ball_mass_fuel
        distance = accident_model.fire_ball_distance
        sep = accident_model.fire_ball_sep

        f_ball = AccidentParameters()
        diameter_ball = f_ball.compute_fire_ball_diameter(mass=mass)

        x, y = f_ball.compute_heat_flux_fire_ball(
            diameter_ball=diameter_ball, height=diameter_ball, sep=sep)
        sep_num = f_ball.get_sep_at_distance(
            x_values=x, y_values=y, distance=distance)
        if self.request == 'plot_fire_ball':
            unit_sep = i18n.get('kwatt_per_meter_square')
            text_annotate = f" q({distance:.1f})= {sep_num:.1f} {unit_sep}"
            plot_label = i18n.eq_heat_flux()

            return DataPlotterModel(x_values=x, y_values=y, ylim=max(y) + max(y) * 0.05,
                                    add_annotate=True, text_annotate=text_annotate, x_ann=distance, y_ann=sep_num,
                                    label=i18n.get('plot_ball_label'), x_label=i18n.get('distance_label'), y_label=i18n.get('y_ball_label'),
                                    add_legend=True, loc_legend=1,
                                    plot_label=plot_label)
        else:
            x, y = probits.compute_thermal_fatality_prob_for_plot(
                type_accident='fire_ball', x_val=x, heat_flux=y, mass_ball=mass)

            value = misc_utils.get_value_at_distance(
                x_values=x, y_values=y, distance=distance)
            unit_sep = ''
            text_annotate = f"Q({distance:.1f})= {value:.1e} {unit_sep}"

            plot_label = i18n.eq_heat_flux()

            return DataPlotterModel(x_values=x, y_values=y, ylim=max(y) + max(y) * 0.05, ymin=-0.01,
                                    add_annotate=True, text_annotate=text_annotate, x_ann=distance, y_ann=value,
                                    label=i18n.get('plot_probit_label'), x_label=i18n.get('distance_label'), y_label=i18n.get('y_probit_label'),
                                    add_legend=False, loc_legend=1,
                                    plot_label=plot_label)

    def get_plot_from_accident_bleve(self):
        i18n = self.i18n
        accident_model = self.accident_model
        substance = self.substance
        subst = accident_model.substance_name
        coef_k = accident_model.bleve_energy_fraction
        heat_capacity = accident_model.bleve_heat_capacity_liquid_phase
        mass = accident_model.bleve_mass_fuel
        # temp_liq = accident_model.bleve_temperature_liquid_phase
        distance = accident_model.bleve_distance
        boiling_point = substance.boiling_point
        acc_bleve = AccidentParameters(type_accident='accident_bleve')
        expl_energy, temp_liq = acc_bleve.compute_expl_energy(
            k=coef_k, Cp=heat_capacity, mass=mass, temp_liquid=accident_model.bleve_temperature_liquid_phase, boiling_point=boiling_point)
        reduced_mass = acc_bleve.compute_redused_mass(
            expl_energy=expl_energy)

        overpres, impuls, dist = acc_bleve.compute_overpres_inopen(
            reduced_mass=reduced_mass, distance_run=True, distance=distance)
        overpresure_30, impuls_30 = acc_bleve.compute_overpres_inopen(
            reduced_mass=reduced_mass, distance=distance)

        if self.request == 'plot_accident_bleve_pressure':
            unit_p = i18n.get('pascal')
            unit_p1 = i18n.get('kg_per_santimeter_square')
            text_annotate = f" ΔP\n = {overpresure_30:.2e} {unit_p}\n = {(overpresure_30*0.000010197):.2e} {unit_p1}"
            return DataPlotterModel(x_values=dist, y_values=overpres, ylim=overpresure_30 * 3.5,
                                    add_annotate=True,
                                    text_annotate=text_annotate, x_ann=distance, y_ann=overpresure_30,
                                    label=i18n.get('plot_pressure_label'),
                                    x_label=i18n.get('distance_label'),
                                    y_label=i18n.get('plot_pressure_legend'),
                                    add_legend=True, loc_legend=1)

        else:
            unit_i = i18n.get('pascal_in_sec')
            text_annotate = f" I+ = {impuls_30:.2e} {unit_i}"
            return DataPlotterModel(x_values=dist, y_values=impuls, ylim=impuls_30 * 4.0,
                                    add_annotate=True,
                                    text_annotate=text_annotate, x_ann=distance, y_ann=impuls_30,
                                    label=i18n.get('plot_impuls_label'), x_label=i18n.get('distance_label'), y_label=i18n.get('plot_impuls_legend'),
                                    add_legend=True, loc_legend=1)

    def get_plot_from_cloud_explosion(self):
        i18n = self.i18n
        accident_model = self.accident_model
        substance = accident_model.substance

        subst = accident_model.explosion_state_fuel
        methodology = accident_model.methodology
        mass = accident_model.explosion_mass_fuel
        stc_coef_oxygen = accident_model.explosion_stc_coef_oxygen
        class_fuel = substance.class_fuel
        class_space = accident_model.class_space
        distance = accident_model.distance
        stc_coef_oxygen = accident_model.explosion_stc_coef_oxygen
        stc_coef_fuel = compute_stoichiometric_coefficient_with_fuel(
            beta=stc_coef_oxygen)
        coef_z = substance.coefficient_participation_in_explosion
        expl_sf = True if accident_model.explosion_condition == 'on_surface' else False

        cloud_exp = AccidentParameters(type_accident='cloud_explosion')
        mode_expl = cloud_exp.get_mode_explosion(
            class_fuel=class_fuel, class_space=class_space)
        # cloud_exp = AccidentParameters()

        eff_energy = cloud_exp.compute_eff_energy_reserve(
            phi_fuel=stc_coef_fuel, phi_stc=stc_coef_fuel, mass_gas_phase=mass * coef_z, explosion_superficial=expl_sf)
        mode_expl = cloud_exp.get_mode_explosion(
            class_fuel=class_fuel, class_space=class_space)
        ufront = cloud_exp.compute_velocity_flame(
            cloud_combustion_mode=mode_expl, mass_gas_phase=mass * coef_z)

        dist, overpres, impuls = cloud_exp.compute_overpres_inclosed(
            energy_reserve=eff_energy, distance_run=True, distance=distance, ufront=ufront, mode_explosion=mode_expl, new_methodology=methodology)

        if self.request == 'plot_accident_cloud_explosion_pressure':
            value = cloud_exp.get_sep_at_distance(
                x_values=dist, y_values=overpres, distance=distance)
            unit_p = i18n.get('pascal')
            unit_p1 = i18n.get('kg_per_santimeter_square')
            text_annotate = f"ΔP\n = {value:.2e} {unit_p}\n = {(value*0.000010197):.2e} {unit_p1}"
            return DataPlotterModel(x_values=dist, y_values=overpres, ylim=max(overpres) + max(overpres) * 0.05,
                                    add_annotate=True, text_annotate=text_annotate, x_ann=distance, y_ann=value,
                                    label=i18n.get(
                'plot_pressure_label'),
                x_label=i18n.get('distance_label'),
                y_label=i18n.get(
                'plot_pressure_legend'),
                add_legend=True, loc_legend=1)

        else:
            value = cloud_exp.get_sep_at_distance(
                x_values=dist, y_values=impuls, distance=distance)

            unit = i18n.get('pascal_in_sec')
            text_annotate = f" I+ = {value:.1f} {unit}"
            return DataPlotterModel(x_values=dist, y_values=impuls, ylim=max(impuls) + max(impuls) * 0.05,
                                    add_annotate=True, text_annotate=text_annotate, x_ann=distance, y_ann=value,
                                    label=i18n.get(
                'plot_impuls_label'),
                x_label=i18n.get('distance_label'),
                y_label=i18n.get(
                'plot_impuls_legend'),
                add_legend=True, loc_legend=1)
