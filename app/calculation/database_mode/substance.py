import logging

from fluentogram import TranslatorRunner

from app.tg_bot.utilities.misc_utils import get_temp_folder

import plotly.graph_objects as go
import math as m
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from scipy.interpolate import interp1d

import re
import json

logger = logging.getLogger(__name__)


class SubstanceDB:
    def __init__(self, chat_id, data="А"):
        self.chat_id: str = chat_id
        self.data: str = data

    def get_list_substances(self):
        with open(file='app/infrastructure/substance_data/combustible_gas.json', mode='r', encoding='utf-8') as file_r_gas:
            db_gas = json.load(file_r_gas)
        with open(file='app/infrastructure/substance_data/combustible_liquid.json', mode='r', encoding='utf-8') as file_r_liquid:
            db_liquid = json.load(file_r_liquid)
        with open(file='app/infrastructure/substance_data/combustible_dust.json', mode='r', encoding='utf-8') as file_r_dust:
            db_dust = json.load(file_r_dust)
        list_sub = list(db_gas.keys()) + \
            list(db_liquid.keys()) + list(db_dust.keys())
        return list_sub

    def get_quantity_keys(self):
        list_sub = self.get_list_substances()
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

    def get_liquid_hfl(self):
        with open(file='app/infrastructure/substance_data/combustible_liquid.json', mode='r', encoding='utf-8') as file_r_liquid:
            db_liquid = json.load(file_r_liquid)
        hfl = []
        for key in list(db_liquid.keys()):
            if db_liquid[key]["substance_type"][-1] == "ЛВЖ":
                hfl.append(db_liquid[key]["substance_type"][-1])
        liquid_hfl = len(hfl)
        return liquid_hfl

    def get_liquid_fl(self):
        with open(file='app/infrastructure/substance_data/combustible_liquid.json', mode='r', encoding='utf-8') as file_r_liquid:
            db_liquid = json.load(file_r_liquid)
        fl = []
        for key in list(db_liquid.keys()):
            if db_liquid[key]["substance_type"][-1] == "ГЖ":
                fl.append(db_liquid[key]["substance_type"][-1])
        liquid_fl = len(fl)
        return liquid_fl

    def get_diagram_sankey(self):
        quantity_keys = self.get_quantity_keys()
        liquid_sub = self.get_liquid_sub()
        gas_sub = self.get_gas_sub()
        dust_sub = self.get_dust_sub()
        liquid_hfl = self.get_liquid_hfl()
        liquid_fl = self.get_liquid_fl()

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
                label=[
                    f"{quantity_keys}",
                    f"Жидкости: {liquid_sub}",
                    f"Газы: {gas_sub}",
                    f"Пыли: {dust_sub}",
                    f"ЛВЖ: {liquid_hfl}",
                    f"ГЖ: {liquid_fl}"],
                color="rgba(214, 39, 40, 0.5)"  # цвет вертикальной линии
            ),
            link=dict(
                # indices correspond to labels=индексы соответствуют меткам
                source=[0, 0, 0, 1, 1],  # source=[0, 6, 1, 4, 2, 3] - источник
                # target=[2, 1, 5, 2, 1, 5] - назначение
                target=[1, 2, 3, 4, 5],
                # value=[10, 11, 3, 6, 9, 4] - значение
                value=[liquid_sub, gas_sub, dust_sub, liquid_hfl, liquid_fl],
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
            paper_bgcolor='rgba(173, 157, 141, 0.70)')

        name_fig = 'fig_sankey_'

        directory = get_temp_folder(fold_name='temp_pic')
        name_plot = "".join([name_fig, str(self.chat_id), '.png'])
        name_dir = '/'.join([directory, name_plot])

        fig.write_image(name_dir, format='png', width=500,
                        height=500, scale=1, engine='kaleido')

        return name_dir

    def get_rus_alphabet(self):
        list_sub = self.get_list_substances()
        rus_sub = []
        for letter in list_sub:
            if not re.match(f"{self.data}\w", letter) == None:
                rus_sub.append(letter)

        return rus_sub

    # def get_quantity_rus(self, i18n: TranslatorRunner):
    #     list_sub = self.get_list_substances()
    #     letters = ['rus_1', 'rus_2', 'rus_3', 'rus_4', 'rus_5',
    #                'rus_6', 'rus_7', 'rus_8', 'rus_9', 'rus_10',
    #                'rus_11', 'rus_12', 'rus_13', 'rus_14', 'rus_15',
    #                                              'rus_16', 'rus_17', 'rus_18', 'rus_19', 'rus_20',
    #                                              'rus_21', 'rus_22', 'rus_23', 'rus_24', 'rus_25',
    #                                              'rus_26', 'rus_27', 'rus_28', 'rus_29', 'rus_30']
    #     quantity_rus = []

    #     for i in range(0, len(list_sub)+1):
    #         if not re.match(f"{i18n.get(letters[i])}\w", letter) == None:
    #             for letter in list_sub:

    #             quantity_rus.append(letter)
    #     print(quantity_rus)
    #     return quantity_rus
