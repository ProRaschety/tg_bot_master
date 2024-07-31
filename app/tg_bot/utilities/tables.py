import logging
# import os
# import csv
# import io
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.patches as patches
# import matplotlib.gridspec as gridspec
# import inspect

# from typing import Any

from fluentogram import TranslatorRunner

# from datetime import datetime
from app.calculation.physics.accident_parameters import AccidentParameters
from app.calculation.models.calculations import AccidentModel, RoomModel, SectionModel
from app.infrastructure.database.models.substance import FlammableMaterialModel, SubstanceModel

from app.calculation.physics.physics_utils import compute_characteristic_diameter, compute_density_gas_phase, compute_density_vapor_at_boiling, get_property_fuel, compute_stoichiometric_coefficient_with_fuel, compute_stoichiometric_coefficient_with_oxygen
# from app.calculation.qra_mode import probits
from app.calculation.utilities import misc_utils

# from app.tg_bot.utilities.misc_utils import get_picture_filling, get_data_table, get_plot_graph, get_dataframe_table
# from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb

from app.tg_bot.models.tables import DataFrameModel

from pprint import pprint

log = logging.getLogger(__name__)


class DataFrameBuilder:
    def __init__(self, i18n: TranslatorRunner,
                 request: str,
                 substance: FlammableMaterialModel | SubstanceModel = None,
                 #  flammable_material: FlammableMaterialModel = None,
                 model: AccidentModel = None,
                 fire_category_model: RoomModel = None,
                 ) -> None:

        self.i18n = i18n
        self.request = request
        # self.flammable_material = flammable_material
        # self.accident_model = accident_model
        self.accident_model = model
        # self.substance = substance if substance is not None else self.accident_model.substance
        self.substance = self.accident_model.substance if self.accident_model is not None else None
        self.room_model = fire_category_model

        log.info(f'Requst dataframe: {self.i18n.get(request)}')

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
            ('fire_flash', 'run_fire_flash'): self.get_dataframe_from_fire_flash,
            ('fire_pool', 'run_fire_pool'): self.get_dataframe_from_fire_pool,
            ('cloud_explosion', 'run_cloud_explosion'): self.get_dataframe_from_cloud_explosion,
            ('horizontal_jet', 'vertical_jet'): self.get_dataframe_from_jet_flame,
            ('fire_ball', 'run_fire_ball'): self.get_dataframe_from_fire_ball,
            ('accident_bleve', 'run_accident_bleve'): self.get_dataframe_from_accident_bleve,

            # категорирование
            ('category_build', 'run_category_build'): self.get_dataframe_from_category_build,
            ('category_premises', 'run_category_premises'): self.get_dataframe_from_category_premises,
            ('category_external_installation', 'run_category_external_installation'): self.get_dataframe_from_category_external_installation,

            # расчет ОФП
            ('analytics_model', 'run_analytics_model'): self.get_dataframe_from_analytics_model,

            # калькуляторы риска
            # ('public', 'run_public'): self.,
            # ('industrial', 'run_industrial'): self.,

            # огнестойкость
            ('strength_calculation', 'run_strength_steel'): self.get_dataframe_from_strength_calculation_steel,
            ('thermal_calculation', 'run_thermal_steel'): self.get_dataframe_from_thermal_calculation_steel,

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

    def get_dataframe_from_fire_flash(self):
        label: str = self.i18n.get('fire_flash')
        headers: list[str] = [self.i18n.get('name'), self.i18n.get(
            'variable'), self.i18n.get('value'), self.i18n.get('unit')]
        i18n = self.i18n
        accident_model = self.accident_model
        substance = self.substance

        if self.request == 'run_fire_flash':
            label: str = self.i18n.get('fire_flash')
            air_density = compute_density_gas_phase(
                molar_mass=28.97,
                temperature=accident_model.air_temperature)
            rad_pool = accident_model.liquid_spill_radius
            lfl = substance.lower_flammability_limit
            LFL = lfl if lfl > 0 else (0.1 if lfl == '' else 0.1)
            density_fuel = compute_density_gas_phase(
                molar_mass=substance.molar_mass, temperature=accident_model.fuel_temperature)

            f_flash = AccidentParameters(type_accident='fire_flash')
            radius_LFL = f_flash.compute_radius_LFL(
                density=density_fuel, mass=accident_model.mass_vapor_fuel, clfl=LFL)
            height_LFL = f_flash.compute_height_LFL(
                density=density_fuel, mass=accident_model.mass_vapor_fuel, clfl=LFL)

            dataframe = [
                [i18n.get('substance'), '', '',
                    i18n.get(accident_model.substance_name)],
                [i18n.get('ambient_temperature'), 'tₒ',
                    accident_model.air_temperature,  i18n.get('celsius')],
                [i18n.get('ambient_air_density'), 'ρₒ',
                    f"{air_density:.2f}",  i18n.get('kg_per_m_cub')],
                [i18n.get('lower_concentration_limit_of_flame_propagation'), 'Cнкпр',
                    LFL, i18n.get('percent_volume')],
                [i18n.get('mass_of_flammable_gases_entering_the_surrounding_space'),
                    'mг', accident_model.mass_vapor_fuel, i18n.get('kilogram')],
                [i18n.get('radius_of_the_strait_above_which_an_explosive_zone_is_formed'),
                    'r', accident_model.liquid_spill_radius,  i18n.get('meter')],
                [i18n.get('density_flammable_gases_at_ambient_temperature'),
                    'ρг', f"{density_fuel:.3f}", i18n.get('kg_per_m_cub')],
                [i18n.get('radius_zone_LFL'), i18n.get(
                    'radius_LFL'), f"{(radius_LFL if radius_LFL>rad_pool else rad_pool):.2f}", i18n.get('meter')],
                [i18n.get('height_zone_LFL'), i18n.get('height_LFL'),
                    f"{height_LFL:.2f}", i18n.get('meter')],
                [i18n.get('radius_zone_Rf'), i18n.get(
                    'radius_Rf'), f"{(radius_LFL if radius_LFL>rad_pool else rad_pool) * 1.2:.2f}", i18n.get('meter')]
            ]
            return DataFrameModel(label=label, headers=headers, dataframe=dataframe)
        else:
            air_density = compute_density_gas_phase(
                molar_mass=28.97,
                temperature=accident_model.air_temperature)
            rad_pool = accident_model.liquid_spill_radius
            lfl = substance.lower_flammability_limit
            LFL = lfl if lfl > 0 else (0.1 if lfl == '' else 0.1)
            density_fuel = compute_density_gas_phase(
                molar_mass=substance.molar_mass, temperature=accident_model.fuel_temperature)
            # print(f'density_fuel: {density_fuel}')

            # f_flash = AccidentParameters(type_accident='fire_flash')
            # radius_LFL = f_flash.compute_radius_LFL(
            #     density=density_fuel, mass=accident_model.mass_vapor_fuel, clfl=LFL)
            # height_LFL = f_flash.compute_height_LFL(
            #     density=density_fuel, mass=accident_model.mass_vapor_fuel, clfl=LFL)

            dataframe = [
                [i18n.get('substance'), '', '',
                    i18n.get(accident_model.substance_name),],
                [i18n.get('ambient_temperature'), 'tₒ',
                    accident_model.air_temperature,  i18n.get('celsius')],
                [i18n.get('ambient_air_density'), 'ρₒ',
                    f"{air_density:.2f}",  i18n.get('kg_per_m_cub')],
                [i18n.get('lower_concentration_limit_of_flame_propagation'), 'Cнкпр',
                    LFL, i18n.get('percent_volume')],
                [i18n.get('mass_of_flammable_gases_entering_the_surrounding_space'),
                    'mг', accident_model.mass_vapor_fuel, i18n.get('kilogram')],
                [i18n.get('radius_of_the_strait_above_which_an_explosive_zone_is_formed'),
                    'r', accident_model.liquid_spill_radius,  i18n.get('meter')],
                [i18n.get('density_flammable_gases_at_ambient_temperature'),
                    'ρг', f"{density_fuel:.3f}", i18n.get('kg_per_m_cub')],
                # [i18n.get('radius_zone_LFL'), i18n.get(
                #     'radius_LFL'), f"{(radius_LFL if radius_LFL>rad_pool else rad_pool):.2f}", i18n.get('meter')],
                # [i18n.get('height_zone_LFL'), i18n.get('height_LFL'),
                # f"{height_LFL:.2f}", i18n.get('meter')],
                # [i18n.get('radius_zone_Rf'), i18n.get(
                #     'radius_Rf'), f"{(radius_LFL if radius_LFL>rad_pool else rad_pool) * 1.2:.2f}", i18n.get('meter')]
            ]
            return DataFrameModel(label=label, headers=headers, dataframe=dataframe)

    def get_dataframe_from_fire_pool(self):
        headers: list[str] = [self.i18n.get('name'), self.i18n.get(
            'variable'), self.i18n.get('value'), self.i18n.get('unit')]

        i18n = self.i18n
        accident_model = self.accident_model
        substance = self.substance

        if self.request == 'run_fire_pool':
            label: str = self.i18n.get('run_fire_pool_text')
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

            x0 = misc_utils.get_distance_at_value(
                x_values=x, y_values=y, value=4.0)

            dataframe = [
                [i18n.get('substance'), '', '',
                 i18n.get(accident_model.substance_name)],
                [i18n.get('specific_mass_fuel_burning_rate'), 'm',
                 substance.mass_burning_rate, i18n.get('kg_per_m_square_in_sec')],
                [i18n.get('ambient_temperature'), 'tₒ',
                 accident_model.air_temperature, i18n.get('celsius')],
                [i18n.get('ambient_air_density'), 'ρₒ',
                 f"{air_density:.2f}", i18n.get('kg_per_m_cub')],
                [i18n.get('wind_velocity'), 'wₒ',
                 accident_model.velocity_wind, i18n.get('m_per_sec')],
                [i18n.get('description_pool_area'), 'F',  accident_model.pool_area,
                 i18n.get('meter_square')],
                [i18n.get('description_pool_distance'), 'r',
                 accident_model.pool_distance, i18n.get('meter')],
                [i18n.get('description_saturated_fuel_vapor_density_at_boiling_point'), 'ρп',
                 f"{fuel_density:.3f}", i18n.get('kg_per_m_cub')],
                [i18n.get('distance_to_safe_zone_from_the_heat_flux'), 'x0',
                 f"{x0:.2f}", i18n.get('meter')],

                [i18n.get('surface_density_thermal_radiation_flame'), 'Ef',
                 f"{sep:.2f}", i18n.get('kwatt_per_meter_square')],
                [i18n.get('description_pool_flame_lenght'), 'L',
                 f"{flame_lenght:.2f}", i18n.get('meter')],
                [i18n.get('description_pool_flame_angle'), 'θ',
                 f"{flame_angle:.2f}", i18n.get('degree')],
                [i18n.get('description_pool_diameter'), 'deff',
                 f"{diameter:.2f}", i18n.get('meter')]
            ]
            return DataFrameModel(label=label, headers=headers, dataframe=dataframe)
        else:
            label: str = self.i18n.get('fire_pool')
            air_density = compute_density_gas_phase(
                molar_mass=28.97,
                temperature=self.accident_model.air_temperature
            )
            dataframe = [
                [self.i18n.get('substance'), '', '',
                 self.i18n.get(self.accident_model.substance_name)],
                [self.i18n.get('specific_mass_fuel_burning_rate'), 'm',
                 self.substance.mass_burning_rate, self.i18n.get('kg_per_m_square_in_sec')],
                [self.i18n.get('ambient_temperature'), 'tₒ',
                 self.accident_model.air_temperature, self.i18n.get('celsius')],
                [self.i18n.get('ambient_air_density'), 'ρₒ',
                 f"{air_density:.2f}", self.i18n.get('kg_per_m_cub')],
                [self.i18n.get('wind_velocity'), 'wₒ',
                 self.accident_model.velocity_wind, self.i18n.get('m_per_sec')],
                [self.i18n.get('description_pool_area'), 'F',  self.accident_model.pool_area,
                 self.i18n.get('meter_square')],
                [self.i18n.get('description_pool_distance'), 'r',
                 self.accident_model.pool_distance, self.i18n.get('meter')]
            ]
            return DataFrameModel(label=label, headers=headers, dataframe=dataframe)

    def get_dataframe_from_cloud_explosion(self):
        label: str = self.i18n.get('cloud_explosion')
        headers: list[str] = [self.i18n.get('name'), self.i18n.get(
            'variable'), self.i18n.get('value'), self.i18n.get('unit')]
        i18n = self.i18n
        accident_model = self.accident_model
        substance = self.substance
        subst = accident_model.explosion_state_fuel
        methodology = accident_model.methodology
        mass = accident_model.explosion_mass_fuel
        stc_coef_oxygen = accident_model.explosion_stc_coef_oxygen
        class_fuel = substance.class_fuel
        class_space = accident_model.class_space
        distance = accident_model.explosion_distance

        cloud_exp = AccidentParameters(type_accident='cloud_explosion')
        mode_expl = cloud_exp.get_mode_explosion(
            class_fuel=class_fuel, class_space=class_space)

        if self.request == 'run_cloud_explosion':
            heat = substance.heat_of_combustion
            beta = substance.correction_parameter
            stc_coef_oxygen = accident_model.explosion_stc_coef_oxygen
            stc_coef_fuel = compute_stoichiometric_coefficient_with_fuel(
                beta=stc_coef_oxygen)
            coef_z = substance.coefficient_participation_in_explosion
            # expl_sf = True if accident_model.explosion_condition == 'on_surface' else False
            expl_sf = accident_model.explosion_condition == 'on_surface'

            cloud_exp = AccidentParameters()
            eff_energy = cloud_exp.compute_eff_energy_reserve(
                phi_fuel=stc_coef_fuel, phi_stc=stc_coef_fuel, mass_gas_phase=mass * coef_z, explosion_superficial=expl_sf)
            mode_expl = cloud_exp.get_mode_explosion(
                class_fuel=class_fuel, class_space=class_space)
            ufront = cloud_exp.compute_velocity_flame(
                cloud_combustion_mode=mode_expl, mass_gas_phase=mass * coef_z)

            nondimensional_distance, nondimensional_pressure, overpres, nondimensional_impuls, impuls = cloud_exp.compute_overpres_inclosed(
                energy_reserve=eff_energy, distance_run=False, distance=distance, ufront=ufront, mode_explosion=mode_expl, new_methodology=methodology)

            dataframe = [
                [i18n.get('description_explosion_mass_explosion'), 'Mт',
                    f"{(mass * coef_z):.2f}", i18n.get('kilogram')],
                #  [i18n.get('cloud_explosion_spec_heat_combustion'), 'Eуд',  f"{(heat * beta):.1f}", i18n.get('kJ_per_kg')],
                #  [i18n.get('stoichiometric_coefficient_for_oxygen'), 'β', f"{stc_coef_oxygen:.3f}", '-'],
                [i18n.get('description_explosion_stoichiometric_fuel'), 'Cст',
                    f"{stc_coef_fuel:.3f}", i18n.get('percent_volume')],
                [i18n.get('description_explosion_efficient_energy_reserve'), 'E',
                    f"{2 * (mass * coef_z) * (heat * beta) * 1000:.2e}", i18n.get('Joule')],
                #  [i18n.get('apparent_speed_of_flame_front'), 'uр', f"{103.2:.2f}", i18n.get('m_per_sec')],
                [i18n.get('max_speed_of_flame_front'), 'u',
                    f"{ufront:.2f}", i18n.get('m_per_sec')],
                [i18n.get('description_explosion_nondimensional_distance'),
                    'Rx', f"{nondimensional_distance:.3f}", '-'],
                [i18n.get('description_explosion_nondimensional_pressure'),
                    'px', f"{nondimensional_pressure:.3f}", '-'],
                [i18n.get('description_explosion_nondimensional_impuls'),
                    'Ix', f"{nondimensional_impuls:.3f}", '-'],
                [i18n.get('overpressure'), 'ΔP',
                    f"{overpres:.2e}", i18n.get('pascal')],
                [i18n.get('impuls_overpressure'), 'I+',
                    f"{impuls:.2e}", i18n.get('pascal_in_sec')],
            ]
            return DataFrameModel(label=label, headers=headers, dataframe=dataframe)
        else:
            dataframe = [
                [i18n.get('description_explosion_state_fuel'),
                    '', '', i18n.get(subst)],
                #  [i18n.get('cloud_explosion_heat_combustion'), 'Eуд0', data.get('accident_cloud_explosion_heat_combustion'), i18n.get('kJ_per_kg')],
                [i18n.get('description_explosion_correction_parameter'),
                    'β', substance.correction_parameter, '-'],
                [i18n.get('stoichiometric_coefficient_for_oxygen'),
                    'k', f"{stc_coef_oxygen:.3f}", '-'],
                [i18n.get('description_class_fuel'), '-',
                    class_fuel, '-'],
                [i18n.get('description_class_space'), '-',
                    class_space, '-'],
                [i18n.get('description_explosion_mode_explosion'),
                    '-', f"{mode_expl:.0f}", '-'],
                [i18n.get('description_coefficient_participation_in_explosion'), 'Z',
                    substance.coefficient_participation_in_explosion, '-'],

                [i18n.get('description_condition_on_ground'), '-',
                    i18n.get(accident_model.explosion_condition), '-'],

                [i18n.get('description_explosion_mass_fuel'), 'm',
                    f"{mass:.1f}", i18n.get('kilogram')],
                [i18n.get('description_explosion_distance'), 'r',
                    f"{distance:.1f}", i18n.get('meter')],
                [i18n.get('description_methodology'),
                    '-', i18n.get(methodology), '-']
            ]
            return DataFrameModel(label=label, headers=headers, dataframe=dataframe)

    def get_dataframe_from_jet_flame(self):
        label: str = self.i18n.get('')
        headers: list[str] = [self.i18n.get('name'), self.i18n.get(
            'variable'), self.i18n.get('value'), self.i18n.get('unit')]
        i18n = self.i18n
        accident_model = self.accident_model
        # substance = self.substance
        jet_state_phase = accident_model.jet_state_fuel
        k_coef = 15.0 if jet_state_phase == 'jet_state_liquid' else 13.5 if jet_state_phase == 'jet_state_liq_gas_vap' else 12.5
        mass_rate = accident_model.jet_mass_rate
        lenght_flame = k_coef * mass_rate ** 0.4
        diameter_flame = 0.15 * lenght_flame
        if self.request == 'horizontal_jet':
            dataframe = [
                [i18n.get('description_jet_state_fuel'),  '', '',
                    i18n.get(jet_state_phase)],
                [i18n.get('description_empirical_coefficient'),
                 'K', k_coef, '-'],
                [i18n.get('description_jet_mass_rate'), 'G',
                    f'{mass_rate:.2f}', i18n.get('kg_per_sec')],
                [i18n.get('description_jet_flame_length'), 'Lf',
                    f'{lenght_flame:.2f}', i18n.get('meter')],
                [i18n.get('description_jet_flame_width'), 'Df',
                    f'{diameter_flame:.2f}', i18n.get('meter')],
                [i18n.get('description_jet_human_distance'), 'r',
                    accident_model.distance, i18n.get('meter')]
            ]
            return DataFrameModel(label=label, headers=headers, dataframe=dataframe)
        elif self.request == 'vertical_jet':
            dataframe = [
                [i18n.get('description_jet_state_fuel'),  '', '',
                    i18n.get(jet_state_phase)],
                [i18n.get('description_empirical_coefficient'),
                 'K', k_coef, '-'],
                [i18n.get('description_jet_mass_rate'), 'G',
                    f'{mass_rate:.2f}', i18n.get('kg_per_sec')],
                [i18n.get('description_jet_flame_length'), 'Lf',
                    f'{lenght_flame:.2f}', i18n.get('meter')],
                [i18n.get('description_jet_flame_width'), 'Df',
                    f'{diameter_flame:.2f}', i18n.get('meter')],
                [i18n.get('description_jet_human_distance'), 'r',
                    accident_model.distance, i18n.get('meter')],
            ]
            return DataFrameModel(label=label, headers=headers, dataframe=dataframe)
        else:
            return self._create_2d_array()

    def get_dataframe_from_fire_ball(self):
        label: str = self.i18n.get('fire_ball')
        headers: list[str] = [self.i18n.get('name'), self.i18n.get(
            'variable'), self.i18n.get('value'), self.i18n.get('unit')]
        i18n = self.i18n
        accident_model = self.accident_model
        subst = accident_model.substance_name
        mass = accident_model.fire_ball_mass_fuel
        distance = accident_model.fire_ball_distance
        sep = accident_model.fire_ball_sep

        f_ball = AccidentParameters()
        ts = f_ball.compute_fire_ball_existence_time(mass=mass)
        d = f_ball.compute_fire_ball_diameter(mass=mass)

        if self.request == 'run_fire_ball':
            fq = f_ball.compute_fire_ball_view_factor(
                eff_diameter=d, height=d, distance=distance)
            t = f_ball.compute_fire_ball_atmospheric_transmittance(
                eff_diameter=d, height=d, distance=distance)
            q = sep * fq * t

            dataframe = [
                        [i18n.get('substance'), '', '', i18n.get(subst)],
                        [i18n.get('surface_density_thermal_radiation_flame'),
                            'Ef', accident_model.fire_ball_sep, i18n.get('kwatt_per_meter_square')],
                        [i18n.get('description_ball_mass_fuel'), 'm',
                            mass, i18n.get('kilogram')],
                        [i18n.get('description_ball_existence_time'), 'ts',
                            f"{ts:.2f}", i18n.get('second')],
                        [i18n.get('description_ball_diameter'), 'Ds',
                            f"{d:.2f}", i18n.get('meter')],
                        [i18n.get('description_ball_height_center'), 'H',
                            f"{d:.2f}", i18n.get('meter')],
                        [i18n.get('description_ball_distance'), 'r',
                            accident_model.fire_ball_distance, i18n.get('meter')],
                        [i18n.get('description_ball_view_factor'),
                            'Fq', f"{fq:.3f}", '-'],
                        [i18n.get('description_ball_atmospheric_transmittance'),
                            'τ',  f"{t:.2f}", '-'],
                        [i18n.get('description_ball_heat_flux'), 'q', f"{q:.2f}", i18n.get(
                            'kwatt_per_meter_square')]
            ]
            return DataFrameModel(label=label, headers=headers, dataframe=dataframe)
        else:
            dataframe = [
                [i18n.get('substance'), '', '', i18n.get(subst)],
                [i18n.get('surface_density_thermal_radiation_flame'), 'Ef',
                    accident_model.fire_ball_sep, i18n.get('kwatt_per_meter_square')],
                [i18n.get('description_ball_mass_fuel'), 'm',
                    mass, i18n.get('kilogram')],
                [i18n.get('description_ball_existence_time'), 'ts',
                    f"{ts:.2f}", i18n.get('second')],
                [i18n.get('description_ball_diameter'), 'Ds',
                    f"{d:.2f}", i18n.get('meter')],
                [i18n.get('description_ball_height_center'), 'H',
                    f"{d:.2f}", i18n.get('meter')],
                [i18n.get('description_ball_distance'), 'r',
                    accident_model.fire_ball_distance, i18n.get('meter')]
            ]
            return DataFrameModel(label=label, headers=headers, dataframe=dataframe)

    def get_dataframe_from_accident_bleve(self):
        label: str = self.i18n.get('accident_bleve')
        headers: list[str] = [self.i18n.get('name'), self.i18n.get(
            'variable'), self.i18n.get('value'), self.i18n.get('unit')]
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

        if self.request == 'run_accident_bleve':
            reduced_mass = acc_bleve.compute_redused_mass(
                expl_energy=expl_energy)
            overpres, impuls = acc_bleve.compute_overpres_inopen(
                reduced_mass=reduced_mass, distance=distance)
            dataframe = [
                [i18n.get('substance'), '', '', i18n.get(subst)],
                [i18n.get('specific_heat_capacity_liquid_phase'), 'Cp',
                    heat_capacity, i18n.get('J_per_kg_in_kelvin')],
                [i18n.get('boiling_point'),
                    'Tb', f"{boiling_point + 273.15:.2f}", i18n.get('kelvin')],
                [i18n.get('description_temperature_liquid_phase'), 'Tₒ',
                    temp_liq, i18n.get('kelvin')],
                [i18n.get('description_mass_liquid_phase'), 'm',
                    mass, i18n.get('kilogram')],
                [i18n.get('description_pressure_wave_energy_fraction'),
                    'k', coef_k, '-'],
                [i18n.get('description_effective_explosion_energy'),
                    'Eeff', f"{expl_energy:.2e}", '-'],
                [i18n.get('description_bleve_distance'), 'r',
                    accident_model.bleve_distance, i18n.get('meter')],
                [i18n.get('description_reduced_mass_liquid_phase'),
                    'mпр', f"{reduced_mass:.2f}", '-'],
                [i18n.get('overpressure'), 'ΔP',
                    f"{overpres:.2e}", i18n.get('pascal')],
                [i18n.get('impuls_overpressure'), 'I+',
                    f"{impuls:.2e}", i18n.get('pascal_in_sec')],
            ]
            return DataFrameModel(label=label, headers=headers, dataframe=dataframe)
        else:
            dataframe = [
                [i18n.get('substance'), '', '', i18n.get(subst)],
                [i18n.get('specific_heat_capacity_liquid_phase'), 'Cp',
                    heat_capacity, i18n.get('J_per_kg_in_kelvin')],
                [i18n.get('boiling_point'),
                    'Tb', f"{boiling_point + 273.15:.2f}", i18n.get('kelvin')],
                [i18n.get('description_temperature_liquid_phase'), 'Tₒ',
                    temp_liq, i18n.get('kelvin')],
                [i18n.get('description_mass_liquid_phase'), 'm',
                    mass, i18n.get('kilogram')],
                [i18n.get('description_pressure_wave_energy_fraction'),
                    'k', coef_k, '-'],
                [i18n.get('description_effective_explosion_energy'),
                    'Eeff', f"{expl_energy:.2e}", '-'],
                [i18n.get('description_bleve_distance'), 'r',
                    accident_model.bleve_distance, i18n.get('meter')],
            ]
            return DataFrameModel(label=label, headers=headers, dataframe=dataframe)

    def get_dataframe_from_category_build(self):
        print(self.request)
        return 'Категория здания'

    def get_dataframe_from_category_premises(self):
        headers: list[str] = [self.i18n.get('name'), self.i18n.get(
            'variable'), self.i18n.get('value'), self.i18n.get('unit')]
        i18n = self.i18n
        label = i18n.get('category_premises_label')
        room = self.room_model
        # pprint(room)
        dataframe = [
            ['Параметры помещения', '', '', '',],
            [i18n.get('height'), 'h', f"{0:.1f}", i18n.get('meter')],
            [i18n.get('lenght'), 'a', f"{0:.1f}", i18n.get('meter')],
            [i18n.get('width'), 'b', f"{0:.1f}", i18n.get('meter')],
            [i18n.get('area'), 'S', f"{0:.1f}", i18n.get('meter_square')],
            [i18n.get('volume'), 'V', f"{0:.1f}", i18n.get('meter_cub')],
            [i18n.get('temperature'), 'tₒ', f"{0:.1f}", i18n.get('celsius')],
        ]

        for sec in room.sections:
            dataframe.append(['', '', '', '',])
        # dataframe = [
        #     {'id': i18n.get('fire_load'),
        #      'var': '',
        #      'unit_1': '',
        #      'unit_2': 'Древесина'},

        #     {'id': i18n.get('section'),
        #      'var': '№2',
        #      'unit_1': '',
        #      'unit_2': 'В4'},

        #     {'id': i18n.get('fire_load'),
        #      'var': '',
        #      'unit_1': '',
        #      'unit_2': 'Автомобиль'},

        #     {'id': i18n.get('section'),
        #      'var': '№1',
        #      'unit_1': '',
        #      'unit_2': 'В2'},]

        return DataFrameModel(label=label, headers=headers, dataframe=dataframe)

    def get_dataframe_from_category_external_installation(self):
        print(self.request)
        return 'Категория наружной установки'

    def get_dataframe_from_analytics_model(self):
        print(self.request)
        return 'Аналитическая модель'

    def get_dataframe_from_strength_calculation_steel(self):
        print(self.request)
        return 'Прочностной расчет. Сталь'

    def get_dataframe_from_thermal_calculation_steel(self):
        print(self.request)
        return 'Теплотехнический расчет. Сталь'

    def get_dataframe_from_(self):
        print(self.request)
        return ''

    # def get_dataframe_from__(self):
    #     label: str = self.i18n.get('')
    #     headers: list[str] = [self.i18n.get('name'), self.i18n.get(
    #         'variable'), self.i18n.get('value'), self.i18n.get('unit')]
    #     i18n = self.i18n
    #     accident_model = self.accident_model
    #     substance = self.substance
    #     if self.request == '':
    #         pass
    #     else:
    #         pass
