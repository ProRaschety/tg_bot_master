import logging
# from re import search
import io
import re
import json

from fluentogram import TranslatorRunner

from app.tg_bot.utilities.misc_utils import get_temp_folder

import plotly.graph_objects as go
import math as m
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from scipy.interpolate import interp1d


logger = logging.getLogger(__name__)

# data: list | str, word_search: str


class SubstanceDB:
    def __init__(self, i18n: TranslatorRunner, chat_id=None, data=None, word_search=None):
        self.chat_id: int = chat_id
        self.data: list | str = data
        self.word_search: list | str = word_search

    def get_list_substances(self):
        with open(file='app/infrastructure/substance_data/db_explosive_substances.json', mode='r', encoding='utf-8') as file_db_exp:
            db_explosive_sub = json.load(file_db_exp)
        with open(file='app/infrastructure/substance_data/db_flammable_substances.json', mode='r', encoding='utf-8') as file_db_flam_sub:
            db_flam_sub = json.load(file_db_flam_sub)
        with open(file='app/infrastructure/substance_data/db_flammable_gases.json', mode='r', encoding='utf-8') as file_db_flam_gas:
            db_flam_gas = json.load(file_db_flam_gas)
        with open(file='app/infrastructure/substance_data/db_liquefied_hydrocarbon_gases.json', mode='r', encoding='utf-8') as file_db_liq_gas:
            db_liq_gas = json.load(file_db_liq_gas)
        with open(file='app/infrastructure/substance_data/db_highly_flammable_liquids.json', mode='r', encoding='utf-8') as file_db_h_flam_liq:
            db_h_flam_liq = json.load(file_db_h_flam_liq)
        with open(file='app/infrastructure/substance_data/db_flammable_liquids.json', mode='r', encoding='utf-8') as file_db_flam_liq:
            db_flam_liq = json.load(file_db_flam_liq)
        with open(file='app/infrastructure/substance_data/db_flammable_dust.json', mode='r', encoding='utf-8') as file_db_flam_dust:
            db_flam_dust = json.load(file_db_flam_dust)
        with open(file='app/infrastructure/substance_data/db_solid_combustible_materials.json', mode='r', encoding='utf-8') as file_db_solid_comb_mat:
            db_solid_comb_mat = json.load(file_db_solid_comb_mat)
        with open(file='app/infrastructure/substance_data/db_non_flammable_materials.json', mode='r', encoding='utf-8') as file_db_non_flam_mat:
            db_non_flam_mat = json.load(file_db_non_flam_mat)

        list_sub = list(db_explosive_sub.keys()) + list(db_flam_sub.keys()) + list(db_flam_gas.keys()) + \
            list(db_liq_gas.keys()) + list(db_h_flam_liq.keys()) + \
            list(db_flam_liq.keys()) + list(db_flam_dust.keys()) + list(db_solid_comb_mat.keys()) + \
            list(db_non_flam_mat.keys())

        return list_sub

    def _index_search(self):
        list_sub = self.get_list_substances()
        try:
            name_sub = self.word_search.lower()
            word = name_sub.split()[0]
            word_index = []
            for letter in list_sub:
                l_ind = list_sub.index(letter)
                let = letter.lower().split()
                len_word = len(let)
                for i in range(0, len_word):
                    let_i = let[i]
                    if word == let_i:
                        word_index.append(l_ind)
                    elif re.search(word, let_i):
                        word_index.append(l_ind)
            return word_index
        except:
            print(f"Произошла ошибка:")

    def get_word_search_result(self):
        list_sub = self.get_list_substances()
        try:
            word_index = self._index_search()
            result_search = []
            for index in word_index:
                result_search.append(list_sub[index])
            return result_search
        except:
            print("Произошла ошибка")

    def get_quantity_keys(self):
        list_sub = self.get_list_substances()
        quantity_keys = len(list_sub)
        return quantity_keys

    def get_liquid_sub(self):
        with open(file='app/infrastructure/substance_data/db_highly_flammable_liquids.json', mode='r', encoding='utf-8') as file_db_h_flam_liq:
            db_h_flam_liq = json.load(file_db_h_flam_liq)
        with open(file='app/infrastructure/substance_data/db_flammable_liquids.json', mode='r', encoding='utf-8') as file_db_flam_liq:
            db_flam_liq = json.load(file_db_flam_liq)

        liquid_sub = len(list(db_h_flam_liq.keys())+list(db_flam_liq.keys()))
        return liquid_sub

    def get_gas_sub(self):
        with open(file='app/infrastructure/substance_data/db_flammable_gases.json', mode='r', encoding='utf-8') as file_db_flam_gas:
            db_flam_gas = json.load(file_db_flam_gas)
        with open(file='app/infrastructure/substance_data/db_liquefied_hydrocarbon_gases.json', mode='r', encoding='utf-8') as file_db_liq_gas:
            db_liq_gas = json.load(file_db_liq_gas)

        gas_sub = len(list(db_flam_gas.keys())+list(db_liq_gas.keys()))
        return gas_sub

    def get_dust_sub(self):
        with open(file='app/infrastructure/substance_data/db_flammable_dust.json', mode='r', encoding='utf-8') as file_db_flam_dust:
            db_flam_dust = json.load(file_db_flam_dust)
        dust_sub = len(list(db_flam_dust.keys()))
        return dust_sub

    def get_liquid_hfl(self):
        with open(file='app/infrastructure/substance_data/db_highly_flammable_liquids.json', mode='r', encoding='utf-8') as file_db_h_flam_liq:
            db_h_flam_liq = json.load(file_db_h_flam_liq)
        hfl = []
        for key in list(db_h_flam_liq.keys()):
            if db_h_flam_liq[key]["substance_type"][-1] == "ЛВЖ":
                hfl.append(db_h_flam_liq[key]["substance_type"][-1])
        liquid_hfl = len(hfl)
        return liquid_hfl

    def get_liquid_fl(self):
        with open(file='app/infrastructure/substance_data/db_flammable_liquids.json', mode='r', encoding='utf-8') as file_db_flam_liq:
            db_flam_liq = json.load(file_db_flam_liq)
        fl = []
        for key in list(db_flam_liq.keys()):
            if db_flam_liq[key]["substance_type"][-1] == "ГЖ":
                fl.append(db_flam_liq[key]["substance_type"][-1])
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

        # name_fig = 'fig_sankey_'

        # directory = get_temp_folder(fold_name='temp_pic')
        # name_plot = "".join([name_fig, str(self.chat_id), '.png'])
        # name_dir = '/'.join([directory, name_plot])

        buffer = io.BytesIO()

        fig.write_image(buffer, format='png', width=500,
                        height=500, scale=1, engine='kaleido')

        # fig.savefig(buffer, format='png')
        buffer.seek(0)
        fig_sankey = buffer.getvalue()
        buffer.close()
        # plt.cla()
        # plt.close(fig)

        return fig_sankey

    def get_rus_alphabet(self):
        list_sub = self.get_list_substances()
        rus_sub = []
        for letter in list_sub:
            if not re.match(f"{self.data}\w", letter) == None:
                rus_sub.append(letter)
        return rus_sub

    def get_rus_alphabet_quan(self, i18n: TranslatorRunner):
        list_sub = self.get_list_substances()
        data = ['rus_1', 'rus_2', 'rus_3', 'rus_4', 'rus_5',
                'rus_6', 'rus_7', 'rus_8', 'rus_9', 'rus_10',
                'rus_11', 'rus_12', 'rus_13', 'rus_14', 'rus_15',
                'rus_16', 'rus_17', 'rus_18', 'rus_19', 'rus_20',
                'rus_21', 'rus_22', 'rus_23', 'rus_24', 'rus_25',
                'rus_26', 'rus_27', 'rus_28', 'rus_29', 'rus_30']
        rus_sub = []
        for letter in list_sub:
            for let in i18n.get(data):
                if not re.match(f"{data[let]}\w", letter) == None:
                    rus_sub.append(letter)

        return rus_sub

    def get_substance_data(self):
        data = self.data
        # with open(file='app/infrastructure/substance_data/combustible_gas.json', mode='r', encoding='utf-8') as file_r_gas:
        #     db_gas = json.load(file_r_gas)
        # with open(file='app/infrastructure/substance_data/combustible_liquid.json', mode='r', encoding='utf-8') as file_r_liquid:
        #     db_liquid = json.load(file_r_liquid)
        # with open(file='app/infrastructure/substance_data/db_flammable_dust.json', mode='r', encoding='utf-8') as file_db_flam_dust:
        #     db_dust = json.load(file_db_flam_dust)

        with open(file='app/infrastructure/substance_data/db_explosive_substances.json', mode='r', encoding='utf-8') as file_db_exp:
            db_explosive_sub = json.load(file_db_exp)
        with open(file='app/infrastructure/substance_data/db_flammable_substances.json', mode='r', encoding='utf-8') as file_db_flam_sub:
            db_flam_sub = json.load(file_db_flam_sub)
        with open(file='app/infrastructure/substance_data/db_flammable_gases.json', mode='r', encoding='utf-8') as file_db_flam_gas:
            db_flam_gas = json.load(file_db_flam_gas)
        with open(file='app/infrastructure/substance_data/db_liquefied_hydrocarbon_gases.json', mode='r', encoding='utf-8') as file_db_liq_gas:
            db_liq_gas = json.load(file_db_liq_gas)
        with open(file='app/infrastructure/substance_data/db_highly_flammable_liquids.json', mode='r', encoding='utf-8') as file_db_h_flam_liq:
            db_h_flam_liq = json.load(file_db_h_flam_liq)
        with open(file='app/infrastructure/substance_data/db_flammable_liquids.json', mode='r', encoding='utf-8') as file_db_flam_liq:
            db_flam_liq = json.load(file_db_flam_liq)
        with open(file='app/infrastructure/substance_data/db_flammable_dust.json', mode='r', encoding='utf-8') as file_db_flam_dust:
            db_flam_dust = json.load(file_db_flam_dust)
        with open(file='app/infrastructure/substance_data/db_solid_combustible_materials.json', mode='r', encoding='utf-8') as file_db_solid_comb_mat:
            db_solid_comb_mat = json.load(file_db_solid_comb_mat)
        with open(file='app/infrastructure/substance_data/db_non_flammable_materials.json', mode='r', encoding='utf-8') as file_db_non_flam_mat:
            db_non_flam_mat = json.load(file_db_non_flam_mat)

        # substances_dict = db_non_flam_mat
        # проверяем в каком словаре данный ключ
        if db_explosive_sub.get(data) is not None:
            substances_dict = db_explosive_sub
        elif db_flam_sub.get(data) is not None:
            substances_dict = db_flam_sub
        elif db_flam_gas.get(data) is not None:
            substances_dict = db_flam_gas
        elif db_liq_gas.get(data) is not None:
            substances_dict = db_liq_gas
        elif db_h_flam_liq.get(data) is not None:
            substances_dict = db_h_flam_liq
        elif db_flam_liq.get(data) is not None:
            substances_dict = db_flam_liq
        elif db_flam_dust.get(data) is not None:
            substances_dict = db_flam_dust
        elif db_solid_comb_mat.get(data) is not None:
            substances_dict = db_solid_comb_mat
        elif db_non_flam_mat.get(data) is not None:
            substances_dict = db_non_flam_mat

        substance_full_name = substances_dict[data]['substance_full_name'][0]
        substance_synonym = substances_dict[data]['substance_synonym'][0]
        molecular_formula = substances_dict[data]['molecular_formula'][0]
        molecular_weight = substances_dict[data]['molecular_weight'][0]
        atoms_nC = substances_dict[data]['atoms_nC'][0]
        atoms_nH = substances_dict[data]['atoms_nH'][0]
        atoms_nO = substances_dict[data]['atoms_nO'][0]
        atoms_nX = substances_dict[data]['atoms_nX'][0]
        const_ant_a = substances_dict[data]['const_ant_a'][0]
        const_ant_b = substances_dict[data]['const_ant_b'][0]
        const_ant_ca = substances_dict[data]['const_ant_ca'][0]
        const_ant_temperature_range = substances_dict[data]['const_ant_temperature_range'][0]
        substance_type = substances_dict[data]['substance_type'][0]
        lower_flammability_limit = substances_dict[data]['lower_flammability_limit'][0]
        temperature_flash_C = substances_dict[data]['temperature_flash_C'][0]
        temperature_spon_combustion_in_air_C = substances_dict[
            data]['temperature_spon_combustion_in_air_C'][0]
        heat_of_burn_kJ_kg = substances_dict[data]['heat_of_burn_kJ_kg'][0]
        burning_rate_kg_m2_s = substances_dict[data]['burning_rate_kg_m2_s'][0]
        density_kg_m3 = substances_dict[data]['density_kg_m3'][0]
        extinguishin_agents = substances_dict[data]['extinguishin_agents'][0]
        description_substance = substances_dict[data]['description_substance'][0]
        property_substance = substances_dict[data]['property_substance'][0]
        s = substances_dict[data]['source'][0]
        source = s.replace('*', '\n')

        # if db_gas.get(data) is not None:
        #     substance_name = db_gas[data]['substance_name'][0]
        #     molecular_formula = db_gas[data]['molecular_formula'][0]
        #     molecular_weight = db_gas[data]['molecular_weight'][0]
        #     atoms_nC = db_gas[data]['atoms_nC'][0]
        #     atoms_nH = db_gas[data]['atoms_nH'][0]
        #     atoms_nO = db_gas[data]['atoms_nO'][0]
        #     atoms_nX = db_gas[data]['atoms_nX'][0]
        #     const_ant_a = db_gas[data]['const_ant_a'][0]
        #     const_ant_b = db_gas[data]['const_ant_b'][0]
        #     const_ant_ca = db_gas[data]['const_ant_ca'][0]
        #     substance_type = db_gas[data]['substance_type'][0]
        #     lower_flammability_limit = db_gas[data]['lower_flammability_limit'][0]
        #     temperature_flash = db_gas[data]['temperature_flash'][0]
        #     temperature_spon_combustion = db_gas[data]['temperature_spon_combustion'][0]
        #     heat_of_burn = db_gas[data]['heat_of_burn'][0]
        #     const_ant_in_temp = db_gas[data]['const_ant_in_temp'][0]
        #     burning_rate = db_gas[data]['burning_rate'][0]
        #     density = db_gas[data]['density_gas'][0]
        #     s = db_gas[data]['source'][0]
        #     source = s.replace('*', '\n')

        # if db_liquid.get(data) is not None:
        #     substance_name = db_liquid[data]['substance_name'][0]
        #     molecular_formula = db_liquid[data]['molecular_formula'][0]
        #     molecular_weight = db_liquid[data]['molecular_weight'][0]
        #     atoms_nC = db_liquid[data]['atoms_nC'][0]
        #     atoms_nH = db_liquid[data]['atoms_nH'][0]
        #     atoms_nO = db_liquid[data]['atoms_nO'][0]
        #     atoms_nX = db_liquid[data]['atoms_nX'][0]
        #     const_ant_a = db_liquid[data]['const_ant_a'][0]
        #     const_ant_b = db_liquid[data]['const_ant_b'][0]
        #     const_ant_ca = db_liquid[data]['const_ant_ca'][0]
        #     substance_type = db_liquid[data]['substance_type'][0]
        #     lower_flammability_limit = db_liquid[data]['lower_flammability_limit'][0]
        #     temperature_flash = db_liquid[data]['temperature_flash'][0]
        #     temperature_spon_combustion = db_liquid[data]['temperature_spon_combustion'][0]
        #     heat_of_burn = db_liquid[data]['heat_of_burn'][0]
        #     const_ant_in_temp = db_liquid[data]['const_ant_in_temp'][0]
        #     burning_rate = db_liquid[data]['burning_rate'][0]
        #     density = db_liquid[data]['density_liquid'][0]
        #     s = db_liquid[data]['source'][0]
        #     source = s.replace('*', '\n')

        # if db_dust.get(data) is not None:
        #     substance_name = db_dust[data]['substance_name'][0]
        #     molecular_formula = db_dust[data]['molecular_formula'][0]
        #     molecular_weight = db_dust[data]['molecular_weight'][0]
        #     atoms_nC = db_dust[data]['atoms_nC'][0]
        #     atoms_nH = db_dust[data]['atoms_nH'][0]
        #     atoms_nO = db_dust[data]['atoms_nO'][0]
        #     atoms_nX = db_dust[data]['atoms_nX'][0]
        #     const_ant_a = db_dust[data]['const_ant_a'][0]
        #     const_ant_b = db_dust[data]['const_ant_b'][0]
        #     const_ant_ca = db_dust[data]['const_ant_ca'][0]
        #     substance_type = db_dust[data]['substance_type'][0]
        #     lower_flammability_limit = db_dust[data]['lower_flammability_limit'][0]
        #     temperature_flash = db_dust[data]['temperature_flash'][0]
        #     temperature_spon_combustion = db_dust[data]['temperature_spon_combustion'][0]
        #     heat_of_burn = db_dust[data]['heat_of_burn'][0]
        #     const_ant_in_temp = db_dust[data]['const_ant_in_temp'][0]
        #     burning_rate = db_dust[data]['burning_rate'][0]
        #     density = db_dust[data]['density_gas'][0]
        #     s = db_dust[data]['source'][0]
        #     source = s.replace('*', '\n')

        list_property = [
            str(substance_full_name),  # 0
            str(substance_synonym),  # 1
            str(molecular_formula),  # 2
            str(molecular_weight),  # 3
            str(atoms_nC),  # 4
            str(atoms_nH),  # 5
            str(atoms_nO),  # 6
            str(atoms_nX),  # 7
            str(const_ant_a),  # 8
            str(const_ant_b),  # 9
            str(const_ant_ca),  # 10
            str(const_ant_temperature_range),  # 11
            str(substance_type),  # 12
            str(lower_flammability_limit),  # 13
            str(temperature_flash_C),  # 14
            str(temperature_spon_combustion_in_air_C),  # 15
            str(heat_of_burn_kJ_kg),  # 16
            str(density_kg_m3),  # 17
            str(burning_rate_kg_m2_s),  # 18
            str(extinguishin_agents),  # 19
            str(description_substance+", "+property_substance),  # 20

            str(source)]

        return list_property
