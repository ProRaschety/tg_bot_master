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
from app.infrastructure.database.models.calculations import AccidentModel
from app.infrastructure.database.models.substance import FlammableMaterialModel, SubstanceModel

from app.calculation.physics.physics_utils import compute_characteristic_diameter, compute_density_gas_phase, compute_density_vapor_at_boiling, get_property_fuel, compute_stoichiometric_coefficient_with_fuel, compute_stoichiometric_coefficient_with_oxygen
from app.calculation.qra_mode import probits

from app.tg_bot.models.tables import DataFrameModel

log = logging.getLogger(__name__)


def get_initial_data(data: tuple, label: str, i18n: TranslatorRunner):
    label_text = i18n.get(label)

    headers = (i18n.get('name'),
               i18n.get('variable'),
               i18n.get('value'),
               i18n.get('unit'))

    data_out = [
        {'id': i18n.get('pool_distance'),
         'var': 'r',
         'unit_1': data.get('accident_fire_pool_distance'),
         'unit_2': i18n.get('meter')},

        {'id': i18n.get('pool_area'),
         'var': 'F',
         'unit_1': data.get('accident_fire_pool_pool_area'),
         'unit_2': i18n.get('meter_square')}]

    return data_out, headers, label_text


def get_result_data(*args, data: tuple, label: str, i18n: TranslatorRunner):
    label_text = i18n.get(label)

    headers = (i18n.get('name'),
               i18n.get('variable'),
               i18n.get('value'),
               i18n.get('unit'))

    data_out = {
        'frequencies_table_2_4': [
            {'id': i18n.get('fire_frequency'),
             'var': 'Q',
             'unit_1': f"{args[2]:.2e}",
             'unit_2': i18n.get('one_per_year')},
            {'id': i18n.get('area_to_frequencies'),
             'var': 'F',
             'unit_1': f"{args[1]:.1f}",
             'unit_2': i18n.get('meter_square')},
            {'id': i18n.get('other_types_of_industrial_buildings'),
             'var': '○' if args[0] != 'other_types_of_industrial_buildings' else '●',
             'unit_1': f"{0.00840:.5f}",
             'unit_2': 0.41},
            {'id': i18n.get('administrative_buildings_of_industrial_facilities'),
             'var': '○' if args[0] != 'administrative_buildings_of_industrial_facilities' else '●',
             'unit_1': f"{0.00006:.5f}",
             'unit_2': 0.90},
            {'id': i18n.get('printing_enterprises_publishing_business'),
             'var': '○' if args[0] != 'printing_enterprises_publishing_business' else '●',
             'unit_1': f"{0.00070:.5f}",
             'unit_2': 0.91},
            {'id': i18n.get('textile_industry'),
             'var': '○' if args[0] != 'textile_industry' else '●',
             'unit_1': f"{0.00750:.5f}",
             'unit_2': 0.35},
            {'id': i18n.get('vehicle_servicing'),
             'var': '○' if args[0] != 'vehicle_servicing' else '●',
             'unit_1': f"{0.00012:.5f}",
             'unit_2': 0.86},
            {'id': i18n.get('placement_of_electrical_equipment'),
             'var': '○' if args[0] != 'placement_of_electrical_equipment' else '●',
             'unit_1': f"{0.00610:.5f}",
             'unit_2': 0.59},
            {'id': i18n.get('recycling_of_combustible_substances_chemical_industry'),
             'var': '○' if args[0] != 'recycling_of_combustible_substances_chemical_industry' else '●',
             'unit_1': f"{0.00690:.5f}",
             'unit_2': 0.46},
            {'id': i18n.get('food_and_tobacco_industry_buildings'),
             'var': '○' if args[0] != 'food_and_tobacco_industry_buildings' else '●',
             'unit_1': f"{0.00110:.5f}",
             'unit_2': 0.60}],
        'frequencies_table_2_3': {},
        'frequencies_table_1_3': {},
    }

    return data_out.get(label), headers, label_text


def get_dataframe(request: str,
                  i18n: TranslatorRunner,
                  substance: SubstanceModel = None,
                  flammable_material: FlammableMaterialModel = None,
                  accmodel: AccidentModel = None
                  ):
    log.info(f'Requst dataframe: {i18n.get(request)}')

    """Собирает данные для формирования таблицы"""

    label: str = i18n.get(request)
    headers: list[str] = [i18n.get('name'), i18n.get(
        'variable'), i18n.get('value'), i18n.get('unit')]
    dataframe: list[dict] = None

    if request == 'fire_pool':
        air_density = compute_density_gas_phase(
            molar_mass=28.97,
            temperature=accmodel.air_temperature
        )
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

    return DataFrameModel(label=label, headers=headers, dataframe=dataframe)
