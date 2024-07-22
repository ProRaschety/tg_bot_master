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

from typing import Any

from fluentogram import TranslatorRunner

# from datetime import datetime
from app.calculation.physics.accident_parameters import AccidentParameters
from app.infrastructure.database.models.calculations import AccidentModel
from app.infrastructure.database.models.substance import FlammableMaterialModel, SubstanceModel

from app.calculation.physics.physics_utils import compute_characteristic_diameter, compute_density_gas_phase, compute_density_vapor_at_boiling, get_property_fuel, compute_stoichiometric_coefficient_with_fuel, compute_stoichiometric_coefficient_with_oxygen
from app.calculation.qra_mode import probits
from app.calculation.utilities import misc_utils

# from app.tg_bot.utilities.misc_utils import get_picture_filling, get_data_table, get_plot_graph, get_dataframe_table
# from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb

from app.tg_bot.models.tables import DataFrameModel

from pprint import pprint

log = logging.getLogger(__name__)


def get_dataframe(request: str,
                  i18n: TranslatorRunner,
                  substance: SubstanceModel = None,
                  flammable_material: FlammableMaterialModel = None,
                  accident_model: AccidentModel = None
                  ):
    log.info(f'Requst dataframe: {i18n.get(request)}')

    """Собирает данные для формирования таблицы"""

    label: str = i18n.get('unknown_request')
    headers: list[str] = [i18n.get('name'), i18n.get(
        'variable'), i18n.get('value'), i18n.get('unit')]
    dataframe: list[list[Any]] = None

    substance = accident_model.substance

    if request in ['fire_pool', 'back_fire_pool', 'gasoline', 'diesel', 'LNG', 'LPG', 'liq_hydrogen', 'run_fire_pool']:
        if request in ['fire_pool', 'back_fire_pool', 'gasoline', 'diesel', 'LNG', 'LPG', 'liq_hydrogen', 'any_substance',]:
            air_density = compute_density_gas_phase(
                molar_mass=28.97,
                temperature=accident_model.air_temperature
            )
            label: str = i18n.get('fire_pool')
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
                 accident_model.distance, i18n.get('meter')]
            ]
        elif request in ['run_fire_pool']:
            diameter = compute_characteristic_diameter(
                area=accident_model.pool_area)
            air_density = compute_density_gas_phase(
                molar_mass=28.97, temperature=accident_model.air_temperature)
            fuel_density = compute_density_vapor_at_boiling(molar_mass=substance.molar_mass,
                                                            boiling_point=substance.boiling_point)
            f_pool = AccidentParameters(type_accident='fire_pool')
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

            label: str = i18n.get('run_fire_pool_text')
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
                [i18n.get('description__pool_area'), 'F',  accident_model.pool_area,
                 i18n.get('meter_square')],
                [i18n.get('description_pool_distance'), 'r',
                 accident_model.distance, i18n.get('meter')],
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

    if request in ['fire_flash', 'back_fire_flash', 'run_fire_flash']:
        if request in ['fire_flash', 'back_fire_flash']:
            label: str = i18n.get('fire_flash')

            air_density = compute_density_gas_phase(
                molar_mass=28.97,
                temperature=accident_model.air_temperature)
            rad_pool = accident_model.liquid_spill_radius
            lfl = substance.lower_flammability_limit
            LFL = lfl if lfl > 0 else (0.1 if lfl == '' else 0.1)
            density_fuel = compute_density_gas_phase(
                molar_mass=substance.molar_mass, temperature=accident_model.fuel_temperature)

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
        elif request in ['run_fire_flash']:
            label: str = i18n.get('fire_flash')

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

    if request in ['cloud_explosion', 'back_cloud_explosion', 'run_cloud_explosion']:
        if request in ['cloud_explosion', 'back_cloud_explosion']:
            pass
        elif request in ['run_cloud_explosion']:
            pass
    if request in ['horizontal_jet', 'back_horizontal_jet',]:
        pass
    if request in ['vertical_jet', 'back_vertical_jet']:
        pass
    if request in ['fire_ball', 'back_fire_ball', 'run_fire_ball']:
        if request in ['fire_ball', 'back_fire_ball']:
            pass
        elif request in ['run_fire_ball']:
            pass
    if request in ['accident_bleve', 'back_accident_bleve', 'run_accident_bleve']:
        if request in ['accident_bleve', 'back_accident_bleve']:
            pass
        elif request in ['run_accident_bleve']:
            pass
    if request in []:
        pass
    if request in []:
        pass
    if request in []:
        pass
    if request in []:
        pass

    return DataFrameModel(label=label, headers=headers, dataframe=dataframe)
