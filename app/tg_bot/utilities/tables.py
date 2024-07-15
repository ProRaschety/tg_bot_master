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
                  accmodel: AccidentModel = None
                  ):
    log.info(f'Requst dataframe: {i18n.get(request)}')

    # pprint(f'accmodel: {accmodel}')
    # pprint(f'accmodel.substance: {accmodel.substance}')

    """Собирает данные для формирования таблицы"""

    label: str = i18n.get('Неизвестный запрос')
    headers: list[str] = [i18n.get('name'), i18n.get(
        'variable'), i18n.get('value'), i18n.get('unit')]
    dataframe: list[dict] = None

    if request in ['fire_pool', 'gasoline', 'diesel', 'LNG', 'LPG', 'liq_hydrogen', 'run_fire_pool', 'run_fire_pool_guest']:
        # label: str = i18n.get(request)
        if request in ['fire_pool', 'gasoline', 'diesel', 'LNG', 'LPG', 'liq_hydrogen', ]:
            substance = SubstanceModel(
                **accmodel.substance)
            air_density = compute_density_gas_phase(
                molar_mass=28.97,
                temperature=accmodel.air_temperature
            )
            label: str = i18n.get('fire_pool')
            dataframe = [
                [i18n.get('substance'), '-',
                 i18n.get(accmodel.substance_name), '-'],
                [i18n.get('specific_mass_fuel_burning_rate'), 'm',
                 substance.mass_burning_rate, i18n.get('kg_per_m_square_in_sec')],
                [i18n.get('ambient_temperature'), 'tₒ',
                 accmodel.air_temperature, i18n.get('celsius')],
                [i18n.get('ambient_air_density'), 'ρₒ',
                 f"{air_density:.2f}", i18n.get('kg_per_m_cub')],
                [i18n.get('wind_velocity'), 'wₒ',
                 accmodel.velocity_wind, i18n.get('m_per_sec')],
                [i18n.get('pool_area'), 'F',  accmodel.pool_area,
                 i18n.get('meter_square')],
                [i18n.get('pool_distance'), 'r',
                 accmodel.distance, i18n.get('meter')]
            ]
        elif request in ['run_fire_pool', 'run_fire_pool_guest']:
            substance = SubstanceModel(**accmodel.substance)

            # distance = accmodel.distance
            diameter = compute_characteristic_diameter(area=accmodel.pool_area)
            air_density = compute_density_gas_phase(
                molar_mass=28.97, temperature=accmodel.air_temperature)
            fuel_density = compute_density_vapor_at_boiling(molar_mass=substance.molar_mass,
                                                            boiling_point=substance.boiling_point)
            f_pool = AccidentParameters(type_accident='fire_pool')
            nonvelocity = f_pool.compute_nonvelocity(
                wind=accmodel.velocity_wind, density_fuel=fuel_density, mass_burn_rate=substance.mass_burning_rate, eff_diameter=diameter)
            flame_angle = f_pool.get_flame_deflection_angle(
                nonvelocity=nonvelocity)
            flame_lenght = f_pool.compute_lenght_flame_pool(
                nonvelocity=nonvelocity, density_air=air_density, mass_burn_rate=substance.mass_burning_rate, eff_diameter=diameter)
            sep = f_pool.compute_surface_emissive_power(
                eff_diameter=diameter, subst=accmodel.substance_name)
            x, y = f_pool.compute_heat_flux(
                eff_diameter=diameter, sep=sep, lenght_flame=flame_lenght, angle=flame_angle)

            x0 = misc_utils.get_distance_at_value(
                x_values=x, y_values=y, value=4.0)

            label: str = i18n.get('run_fire_pool_text')
            dataframe = [
                [i18n.get('substance'), '-',
                 i18n.get(accmodel.substance_name), '-'],
                [i18n.get('specific_mass_fuel_burning_rate'), 'm',
                 substance.mass_burning_rate, i18n.get('kg_per_m_square_in_sec')],
                [i18n.get('ambient_temperature'), 'tₒ',
                 accmodel.air_temperature, i18n.get('celsius')],
                [i18n.get('ambient_air_density'), 'ρₒ',
                 f"{air_density:.2f}", i18n.get('kg_per_m_cub')],
                [i18n.get('wind_velocity'), 'wₒ',
                 accmodel.velocity_wind, i18n.get('m_per_sec')],
                [i18n.get('pool_area'), 'F',  accmodel.pool_area,
                 i18n.get('meter_square')],
                [i18n.get('pool_distance'), 'r',
                 accmodel.distance, i18n.get('meter')],
                [i18n.get('saturated_fuel_vapor_density_at_boiling_point'), 'ρп',
                 f"{fuel_density:.3f}", i18n.get('kg_per_m_cub')],
                [i18n.get('distance_to_safe_zone_from_the_heat_flux'), 'x0',
                 f"{x0:.2f}", i18n.get('meter')],

                [i18n.get('surface_density_thermal_radiation_flame'), 'Ef',
                 f"{sep:.2f}", i18n.get('kwatt_per_meter_square')],
                [i18n.get('pool_flame_lenght'), 'L',
                 f"{flame_lenght:.2f}", i18n.get('meter')],
                [i18n.get('pool_flame_angle'), 'θ',
                 f"{flame_angle:.2f}", i18n.get('degree')],
                [i18n.get('pool_diameter'), 'deff',
                 f"{diameter:.2f}", i18n.get('meter')]

            ]

    return DataFrameModel(label=label, headers=headers, dataframe=dataframe)
