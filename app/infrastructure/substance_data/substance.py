import logging

from app.tg_bot.utilities.misc_utils import get_temp_folder

import plotly.graph_objects as go
import math as m
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from scipy.interpolate import interp1d

import json

logger = logging.getLogger(__name__)


class SubstanceDB:
    def __init__(self, chat_id):
        self.chat_id = chat_id

    def get_quantity_keys(self):
        with open(file='app/infrastructure/substance_data/combustible_gas.json', mode='r', encoding='utf-8') as file_r_gas:
            db_gas = json.load(file_r_gas)
        with open(file='app/infrastructure/substance_data/combustible_liquid.json', mode='r', encoding='utf-8') as file_r_liquid:
            db_liquid = json.load(file_r_liquid)
        with open(file='app/infrastructure/substance_data/combustible_dust.json', mode='r', encoding='utf-8') as file_r_dust:
            db_dust = json.load(file_r_dust)
        list_sub = list(db_gas.keys()) + \
            list(db_liquid.keys()) + list(db_dust.keys())
        quantity_keys = len(list_sub)
        return quantity_keys

    def get_liquid_sub(self):
        with open(file='app/infrastructure/substance_data/combustible_liquid.json', mode='r', encoding='utf-8') as file_r_liquid:
            db_liquid = json.load(file_r_liquid)
        liquid_sub = len(list(db_liquid.keys()))
        return liquid_sub

    def get_gas_sub(self):
        with open(file='app/infrastructure/substance_data/combustible_gas.json', mode='r', encoding='utf-8') as file_r_gas:
            db_gas = json.load(file_r_gas)
        gas_sub = len(list(db_gas.keys()))
        return gas_sub

    def get_dust_sub(self):
        with open(file='app/infrastructure/substance_data/combustible_dust.json', mode='r', encoding='utf-8') as file_r_dust:
            db_dust = json.load(file_r_dust)
        dust_sub = len(list(db_dust.keys()))
        return dust_sub

    def get_diagram_sankey(self):
        quantity_keys = self.get_quantity_keys()
        liquid_sub = self.get_liquid_sub()
        gas_sub = self.get_gas_sub()
        dust_sub = self.get_dust_sub()

        color_link = ['rgba(217, 203, 190, 0.5)',
                      'rgba(100, 117, 124, 0.5)',
                      'rgba(137, 137, 137, 0.5)',
                      'rgba(144, 108, 108, 0.5)',
                      'rgba(114, 108, 108, 0.5)',
                      ]
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                thickness=5,
                line=dict(color="white", width=0.5),
                # label=["A", "B", "C", "D", "E", "F", "t"]
                label=["Общее количество", "Жидкости",
                       "Газы", "Пыли", "ЛВЖ", "ГЖ"],
                color="rgba(214, 39, 40, 0.5)"  # цвет вертикальной линии
            ),
            link=dict(
                # indices correspond to labels=индексы соответствуют меткам
                source=[0, 0, 0, 1, 1],  # source=[0, 6, 1, 4, 2, 3] - источник
                # target=[2, 1, 5, 2, 1, 5] - назначение
                target=[1, 2, 3, 4, 5],
                # value=[10, 11, 3, 6, 9, 4] - значение
                value=[liquid_sub, gas_sub, dust_sub, 21, 19],
                color=color_link
            ))])

        # incoming flow count - подсчет входящего потока
        # outcoming flow count - количество исходящих потоков

        fig.update_layout(
            autosize=False,
            width=800,
            height=800,
            hovermode='x',
            title='База данных веществ',
            font=dict(size=14, color='white'),
            paper_bgcolor='rgba(173, 157, 141, 0.90)')

        name_fig = 'fig_sankey'

        directory = get_temp_folder()
        name_plot = "_".join([name_fig, str(self.chat_id), '.png'])
        name_dir = '/'.join([directory, name_plot])

        fig.write_image(name_dir, format='png', width=500,
                        height=500, scale=1, engine='kaleido')

        # fig.savefig(name_dir, format='png', transparent=True)
        # plt.cla()
        # plt.close(fig)

        return name_dir
