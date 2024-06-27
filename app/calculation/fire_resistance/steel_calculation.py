import logging
import io
import json

from fluentogram import TranslatorRunner

import math as m
# import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from scipy.interpolate import interp1d

log = logging.getLogger(__name__)


class SteelFireStrength:
    def __init__(self, i18n: TranslatorRunner, chat_id=None, data=None):
        self.i18n = i18n
        self.chat_id = chat_id
        self.get_init_data(data)

    def get_init_data(self, data):
        # log.info(f"Данные из редис: {data}")
        """Функция возвращает параметры исходных данных для контруктора"""
        self.num_profile: str = data.get('num_profile')
        self.sketch: str = data.get('sketch')
        self.reg_document: str = data.get('reg_document')
        self.num_sides_heated: str = data.get('num_sides_heated')
        self.len_elem: float = float(data.get('len_elem'))
        self.fixation: str = data.get('fixation')
        # 1 Н ≈ 0,10197162 кгс , 1 кг = 9,807 Н
        self.n_load: float = float(data.get('n_load'))
        # 'stretching_element', 'compression_element', 'bend_element' = растяжение, сжатие, изгиб
        self.type_loading: str = data.get('type_loading')
        self.quan_elem: int = 1
        self.type_steel_element: str = data.get('type_steel_element')
        if self.type_loading == 'compression_element' or self.type_loading == 'stretching_element':
            self.loading_method = 'concentrated_load_steel'
        else:
            self.loading_method: str = data.get('loading_method')

    def get_init_data_table(self):
        log.info("Исходные данные для прочностного расчета")
        with open('app/infrastructure/data_base/db_steel_property.json', encoding='utf-8') as file_op:
            # with open('db_steel_property.json', encoding='utf-8') as file_op:
            property_steel_in = json.load(file_op)
        r_norm = float(
            property_steel_in[self.type_steel_element]["r_norm_kg_cm2"])
        num_sides_heated = self.i18n.get(self.num_sides_heated)
        fixation = self.i18n.get(self.fixation)
        type_loading = self.i18n.get(self.type_loading)
        loading_method = self.i18n.get(self.loading_method)
        unit_1_load = 'кг/м'
        if self.loading_method == 'distributed_load_steel':
            unit_1_load = "кг/м"
        elif self.loading_method == 'concentrated_load_steel':
            unit_1_load = "кг"

        # profile = self.num_profile
        sketch = self.sketch
        # reg_document = self.reg_document
        # len_elem = self.len_elem
        # n_load = self.n_load
        ptm = round(self.get_reduced_thickness(), 2)
        label = 'Прочностной расчет'
        headers = ('Параметр', 'Значение', 'Ед.изм.')
        if sketch == "Двутавр":
            data = [
                {'id': 'Способ закрепления', 'var': fixation, 'unit_1': '-'},
                {'id': 'Усилие', 'var': type_loading, 'unit_1': '-'},
                {'id': 'Тип нагружения', 'var': loading_method, 'unit_1': '-'},
                {'id': 'Нагрузка', 'var': self.n_load, 'unit_1': unit_1_load},
                {'id': 'Длина', 'var': self.len_elem, 'unit_1': 'мм'},
                {'id': 'Приведенная толщина\nметалла', 'var': ptm, 'unit_1': 'мм'},
                {'id': 'Количество сторон обогрева',
                    'var': num_sides_heated, 'unit_1': 'шт'},
                {'id': 'Сечение', 'var': self.sketch, 'unit_1': '-'},
                {'id': 'Профиль', 'var': self.num_profile, 'unit_1': '-'},
                {'id': 'Профиль по ГОСТ', 'var': self.reg_document, 'unit_1': '-'},
                {'id': 'Сопротивление стали', 'var': r_norm, 'unit_1': 'кг/см\u00B2'},
                {'id': 'Марка стали', 'var': self.type_steel_element, 'unit_1': '-'}]

        elif sketch == "Швеллер":
            data = [
                {'id': 'Способ закрепления', 'var': fixation, 'unit_1': '-'},
                {'id': 'Усилие', 'var': type_loading, 'unit_1': '-'},
                {'id': 'Тип нагружения', 'var': loading_method, 'unit_1': '-'},
                {'id': 'Нагрузка', 'var': self.n_load * 9.807, 'unit_1': 'Н'},
                {'id': 'Длина', 'var': self.len_elem, 'unit_1': 'мм'},
                {'id': 'Приведенная толщина\nметалла', 'var': ptm, 'unit_1': 'мм'},
                {'id': 'Количество сторон обогрева',
                    'var': num_sides_heated, 'unit_1': 'шт'},
                {'id': 'Марка стали', 'var': self.type_steel_element, 'unit_1': '-'},
                {'id': 'Сечение', 'var': self.name_profile, 'unit_1': '-'},
                {'id': 'Сортамент', 'var': self.sketch, 'unit_1': '-'},
                {'id': 'Профиль по ГОСТ', 'var': self.reg_document, 'unit_1': '-'}]
        return data, headers, label

    def get_initial_data_strength(self):
        data = self.get_init_data_table()
        rows = len(data)
        cols = len(list(data[0]))

        # размеры рисунка в дюймах
        # 1 дюйм = 2.54 см = 96.358115 pixel
        px = 96.358115
        w = 500  # px
        h = 500  # px
        # Создание объекта Figure
        margins = {
            "left": 0.030,  # 0.030
            "bottom": 0.030,  # 0.030
            "right": 0.970,  # 0.970
            "top": 0.900  # 0.900
        }
        fig = plt.figure(figsize=(w / px, h / px), dpi=300)
        fig.subplots_adjust(**margins)
        ax = fig.add_subplot()

        ax.set_xlim(0.0, cols+0.5)
        ax.set_ylim(-.75, rows+0.55)

        # добавить заголовки столбцов на высоте y=..., чтобы уменьшить пространство до первой строки данных
        ft_title_size = {'fontname': 'Arial', 'fontsize': 10}

        hor_up_line = rows-0.25
        ax.text(x=0, y=hor_up_line, s='Параметр',
                weight='bold', ha='left', **ft_title_size)
        ax.text(x=2.5, y=hor_up_line, s='Значение',
                weight='bold', ha='center', **ft_title_size)
        ax.text(x=cols+.5, y=hor_up_line, s='Ед. изм',
                weight='bold', ha='right', **ft_title_size)

        # добавить основной разделитель заголовка
        ax.plot([0, cols + .5], [rows-0.5, rows-0.5], lw='2', c='black')
        ax.plot([0, cols + .5], [- 0.5, - 0.5], lw='2', c='black')

        # линия сетки
        for row in range(rows):
            ax.plot([0, cols+.5], [row - .5, row - .5],
                    ls=':', lw='.5', c='grey')

        # заполнение таблицы данных
        ft_size = {'fontname': 'Arial', 'fontsize': 9}
        for row in range(rows):
            # извлечь данные строки из списка
            d = data[row]
            # координата y (строка (row)) основана на индексе строки (цикл (loop))
            # координата x (столбец (column)) определяется на основе порядка, в котором я хочу отображать данные в столбце имени игрока
            ax.text(x=0, y=row, s=d['id'], va='center', ha='left', **ft_size)
            # var column это мой «основной» столбец, поэтому текст выделен жирным шрифтом
            ax.text(x=2.5, y=row, s=d['var'], va='center',
                    ha='center', weight='bold', **ft_size)
            # unit_1 column
            ax.text(x=3.5, y=row, s=d['unit_1'],
                    va='center', ha='right', **ft_size)

        # выделите столбец, используя прямоугольную заплатку
        rect = patches.Rectangle((2.0, -0.5),  # нижняя левая начальная позиция (x,y)
                                 width=1,
                                 height=hor_up_line+0.95,
                                 ec='none',
                                 fc='grey',
                                 alpha=.2,
                                 zorder=-1)
        ax.add_patch(rect)

        ax.set_title(label='Исходные данные\nдля прочностного расчета',
                     loc='left', fontsize=12, weight='bold')
        ax.axis('off')

        buffer = io.BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.cla()
        plt.close(fig)

        return image_png

    def get_list_num_profile(self):
        # profile = self.num_profile
        sketch = self.sketch
        gost = self.reg_document
        if sketch == "Двутавр":
            with open(file="app/infrastructure/data_base/db_steel_ibeam.json", mode="r", encoding='utf-8') as file_op:
                db_ibeam = json.load(file_op)

        list_num_profile = list(db_ibeam[sketch][gost].keys())
        # log.info(
        #     f"Количесто номеров профилей: {len(db_ibeam[sketch][gost].keys())}")
        return list_num_profile

    def get_effective_length(self):
        effective_length = self.len_elem
        if self.fixation == 'console':
            effective_length = self.len_elem * 2
        elif self.fixation == 'hinge-hinge':
            effective_length = self.len_elem * 1
        elif self.fixation == 'sealing-sealing':
            effective_length = self.len_elem * 0.5
        elif self.fixation == 'seal-hinge':
            effective_length = self.len_elem * 0.7
        # log.info(f"Эффективная длина элемента: {effective_length} мм")
        return effective_length

    def get_sectional_area(self):
        """Опеределение площади сечения элемента в мм2"""
        profile = self.num_profile
        sketch = self.sketch
        gost = self.reg_document
        sec_area_cm2 = None
        if sketch == "Двутавр":
            with open(file="app/infrastructure/data_base/db_steel_ibeam.json", mode="r", encoding='utf-8') as file_op:
                db_steel_in = json.load(file_op)
                sec_area_cm2 = db_steel_in[sketch][gost][profile].get(
                    'a_cm2', 1)
        elif sketch == "Швеллер":
            with open(file="db_steel_channel.json", mode="r", encoding='utf-8') as file_op:
                db_steel_in = json.load(file_op)
                sec_area_cm2 = db_steel_in[sketch][gost][profile]['a_cm2']
        sectional_area = float(sec_area_cm2) * 100  # мм2
        # log.info(f"Площадь сечения: {sectional_area} мм2")
        return sectional_area

    def get_perimeter_section(self):
        num_sides_heated = float(self.i18n.get(self.num_sides_heated))
        profile = self.num_profile
        sketch = self.sketch
        gost = self.reg_document
        perimeter_section = None
        if sketch == "Двутавр":
            with open(file="app/infrastructure/data_base/db_steel_ibeam.json", mode="r", encoding='utf-8') as file_op:
                db_steel_in = json.load(file_op)
                h_mm = db_steel_in[sketch][gost][profile]["h_mm"]
                b_mm = db_steel_in[sketch][gost][profile]["b_mm"]
                s_mm = db_steel_in[sketch][gost][profile]["s_mm"]

        elif sketch == "Швеллер":
            with open(file="db_steel_channel.json", mode="r", encoding='utf-8') as file_op:
                db_steel_in = json.load(file_op)
                h_mm = db_steel_in[sketch][gost][profile]["h_mm"]

        if sketch == "Двутавр":
            if num_sides_heated == 3:
                perimeter_section = 2 * \
                    float(h_mm) + 3 * float(b_mm) - 2 * float(s_mm)
            else:
                perimeter_section = 2 * \
                    float(h_mm) + 4 * float(b_mm) - 2 * float(s_mm)

        elif sketch == "Швеллер":
            if num_sides_heated == 3:
                perimeter_section = 2 * \
                    float(h_mm) + 3 * float(b_mm) - 2 * float(s_mm)
            else:
                perimeter_section = 2 * \
                    float(h_mm) + 4 * float(b_mm) - 2 * float(s_mm)
        # log.info(
        #     f"Периметр сечения: {perimeter_section} мм")
        return perimeter_section

    def get_moment_section_resistance(self):
        """момент сопротивления сечения в направлении оси приложния усилия, W(x,y), см3"""
        profile = self.num_profile
        sketch = self.sketch
        gost = self.reg_document
        moment_section_resistance = None
        if sketch == "Двутавр":
            with open(file="app/infrastructure/data_base/db_steel_ibeam.json", mode="r", encoding='utf-8') as file_op:
                db_steel_in = json.load(file_op)
                w_x_cm3 = db_steel_in[sketch][gost][profile]['w_x_cm3']
                w_y_cm3 = db_steel_in[sketch][gost][profile]['w_y_cm3']
            moment_section_resistance = min(w_x_cm3, w_y_cm3)

        # elif profile == "Швеллер":
        #     with open(file="db_steel_channel.json", mode="r", encoding='utf-8') as file_op:
        #         db_steel_in = json.load(file_op)
        #         sec_area_cm2 = db_steel_in[profile][gost][sketch]['a_cm2']
        # log.info(
        #     f"Момент сопротивления сечения: {moment_section_resistance} см3")
        return moment_section_resistance

    def get_moment_section_of_inertia(self):
        """Момент инерции сечения, J см4"""
        profile = self.num_profile
        sketch = self.sketch
        gost = self.reg_document
        moment_section_of_inertia = None
        if sketch == "Двутавр":
            with open(file="app/infrastructure/data_base/db_steel_ibeam.json", mode="r", encoding='utf-8') as file_op:
                db_steel_in = json.load(file_op)
                i_x_cm4 = db_steel_in[sketch][gost][profile]['i_x_cm4']
                i_y_cm4 = db_steel_in[sketch][gost][profile]['i_y_cm4']
            moment_section_of_inertia = min(i_x_cm4, i_y_cm4)

        elif sketch == "Швеллер":
            with open(file="db_steel_channel.json", mode="r", encoding='utf-8') as file_op:
                db_steel_in = json.load(file_op)
                i_x_cm4 = db_steel_in[sketch][gost][profile]['i_x_cm4']
                i_y_cm4 = db_steel_in[sketch][gost][profile]['i_y_cm4']
            moment_section_of_inertia = min(i_x_cm4, i_y_cm4)
        # log.info(
        #     f"Момент инерции сечения: {moment_section_of_inertia} см4")
        return moment_section_of_inertia

    def get_reduced_thickness(self):
        sectional_area = self.get_sectional_area()
        perimeter_section = self.get_perimeter_section()
        ptm = sectional_area/perimeter_section
        # log.info(f"Приведенная толщина металла: {ptm} мм")
        return ptm

    def get_loading(self):
        loading = float(self.n_load)  # кг
        # log.info(f"Усилие от нагрузки: {loading} кг")
        return loading

    def get_moment_load(self):
        a_load = float(self.len_elem) * 0.1  # см
        len_elem = float(self.len_elem) * 0.1  # см
        n_load = float(self.n_load)/100  # кг/см
        moment_load = None

        if self.loading_method == 'distributed_load_steel':  # Распределенная
            if self.fixation == 'sealing-sealing':
                moment_load = (n_load * (len_elem ** 2)) / 12
            elif self.fixation == 'seal-hinge':
                moment_load = (n_load * (len_elem ** 2)) / 8
            elif self.fixation == 'hinge-hinge':
                moment_load = (n_load * (len_elem ** 2)) / 8
            elif self.fixation == 'console':
                moment_load = (n_load * (len_elem ** 2)) / 2

        elif self.loading_method == 'concentrated_load_steel':
            if self.fixation == 'sealing-sealing':
                moment_load = (n_load * len_elem) / 8
            elif self.fixation == 'seal-hinge':
                moment_load = (3 * n_load * len_elem) / 16
            elif self.fixation == 'hinge-hinge':
                moment_load = (n_load * len_elem) / 4
            elif self.fixation == 'console':
                moment_load = n_load * 100 * a_load

        # log.info(f"Изгибающий момент: {moment_load} кг*см")
        return moment_load

    def get_coef_strength(self):
        with open('app/infrastructure/data_base/db_steel_property.json', encoding='utf-8') as file_op:
            property_steel_in = json.load(file_op)
        r_norm = float(
            property_steel_in[self.type_steel_element]["r_norm_kg_cm2"])
        # log.info(
        #     f"Начальное нормативное сопротивление металла: {r_norm} kg/cm2")
        e_n_kg_cm2 = 2_100_000
        if self.type_loading == 'stretching_element':
            sectional_area = self.get_sectional_area() * 0.01
            n_load = float(self.get_loading())
            gamma = n_load / (sectional_area * r_norm)
            # log.info(
            #     f"Коэффициент снижения предела текучести стали при растяжении: {gamma:.3f}")
            return gamma

        elif self.type_loading == 'compression_element':
            sectional_area = self.get_sectional_area() * 0.01
            # наименьший момент инерции сечения элемента, см4
            j_min = float(self.get_moment_section_of_inertia())
            # расчетная эффективная длина элемента, см
            l_eff = float(self.get_effective_length()) * 0.1
            n_load = float(self.get_loading())
            gamma_t = n_load / (sectional_area * r_norm)
            # log.info(
            #     f"Коэффициент снижения предела текучести стали при сжатии: {gamma_t:.3f} при нагрузке {n_load:.1f}")
            gamma_elasticity = (n_load * (l_eff ** 2)) / \
                ((m.pi**2) * e_n_kg_cm2 * j_min)
            # log.info(
            #     f"Коэффициент снижения модуля упругости стали при сжатии: {gamma_elasticity:.3f} при j_min {j_min:.2f} и l_eff {l_eff:.2f}")
            return gamma_t, gamma_elasticity

        elif self.type_loading == 'bend_element':
            m_load = float(self.get_moment_load())
            moment_section_resistance = float(
                self.get_moment_section_resistance())
            gamma = m_load / (moment_section_resistance * r_norm)
            # log.info(
            #     f"Коэффициент снижения предела текучести стали при изгибе: {gamma:.3f}")
            return gamma

    def get_crit_temp_steel(self):

        with open('app/infrastructure/data_base/db_grades_steel.json', encoding='utf-8') as file_op:
            prop_steel_in = json.load(file_op)
            temp = prop_steel_in[self.type_steel_element]["heating_temperature"]
            coef = prop_steel_in[self.type_steel_element]["coeff_reduction_of_yield_strength"]
            coef_elast = prop_steel_in[self.type_steel_element]["coeff_module_elasticity"]
        t_critic_list = []
        if self.type_loading == 'compression_element':
            gamma_t, gamma_elasticity = self.get_coef_strength()

            if gamma_t <= coef[-1]:
                t_critic_yt = temp[-1]
                t_critic_list.append(t_critic_yt)
            elif gamma_t >= coef[0]:
                t_critic_yt = temp[0]
                t_critic_list.append(t_critic_yt)
            else:
                temp_cor_yt = interp1d(coef, temp, kind='slinear',
                                       bounds_error=False, fill_value=0)
                t_critic_yt = float(temp_cor_yt(gamma_t))
                t_critic_list.append(t_critic_yt)
            # log.info(
            #     f"Критическая температура при сжатии от yt={gamma_t:.3f}: {t_critic_yt:.3f} С")

            if gamma_elasticity <= coef_elast[-1]:
                t_critic_ye = temp[-1]
                t_critic_list.append(t_critic_ye)
            elif gamma_elasticity >= coef_elast[0]:
                t_critic_ye = temp[0]
                t_critic_list.append(t_critic_ye)
            else:
                temp_cor_ye = interp1d(coef_elast, temp, kind='slinear',
                                       bounds_error=False, fill_value=0)
                t_critic_ye = float(temp_cor_ye(gamma_elasticity))
                t_critic_list.append(t_critic_ye)
            t_critic_list.sort()
            t_critic = t_critic_list.copy()[0]

            # log.info(
            #     f"Критическая температура при сжатии от ye={gamma_elasticity:.3f}: {t_critic_ye:.3f} С")

            # log.info(f"Критическая температура при сжатии: {t_critic:.3f} С")

        elif self.type_loading == 'stretching_element':
            gamma = self.get_coef_strength()
            if gamma <= coef[-1]:
                t_critic = temp[-1]
            elif gamma >= coef[0]:
                t_critic = temp[0]
            else:
                temp_correl = interp1d(coef, temp, kind='slinear',
                                       bounds_error=False, fill_value=0)
                t_critic = float(temp_correl(gamma))
            # log.info(
            #     f"Критическая температура при растяжении: {t_critic:.3f} С")

        elif self.type_loading == 'bend_element':
            gamma = self.get_coef_strength()
            if gamma <= coef[-1]:
                t_critic = temp[-1]
            elif gamma >= coef[0]:
                t_critic = temp[0]
            else:
                temp_correl = interp1d(coef, temp, kind='slinear',
                                       bounds_error=False, fill_value=0)
                t_critic = float(temp_correl(gamma))
            # log.info(f"Критическая температура при изгибе: {t_critic:.3f} С")

        # with open('app/infrastructure/init_data/init_data_thermal_steel.json', encoding='utf-8') as file_op:
        #     init_thermal_in = json.load(file_op)
        #     init_thermal_in[self.chat_id]["t_critic_C"] = t_critic
        # with open('app/infrastructure/init_data/init_data_thermal_steel.json', 'w', encoding='utf-8') as file_w:
        #     json.dump(init_thermal_in, file_w, ensure_ascii=False, indent=4)

        return t_critic

    def get_data_steel_strength(self):
        # Добавляем вид профиля "Двутавр", "Швеллер", "Уголок", "Профиль"
        profile = self.num_profile
        # Section = section  # "RECTANGLE"
        sketch = self.sketch
        gost = self.reg_document                     # Добавляем наименование документа

        if sketch == "Двутавр":
            Name_File = 'db_steel_ibeam.json'
        elif sketch == "Швеллер":
            Name_File = 'db_steel_chanell.json'

        table_title = [
            ["Ведомость стальных несущих конструкций, подлежащих огнезащите"], [""]]
        data_title = [["№ п/п",
                       "Наименование конструкции, шифр",
                       "Эскиз",
                       "Профиль по ГОСТ",
                       "Масса, т",
                       "Кол-во, м",
                       "Нагрузка, кг",
                       "Количество сторон обогрева",
                       "ПТМ, мм",
                       "Ткр, С",
                       "Rсобст., мин",
                       "Rтр., мин",
                       "Толщина огнезащитного слоя, мм",
                       "Площадь защищаемой поверхности, м2",
                       "Расход, кг/м2",
                       ]]
        table_note = [[""], ["ПТМ - приведенная толщина метала"], ["Ткр - критическая температура"],
                      ["Rсобст. - Собственный предел огнестойкости"], ["Rтрю. - Требуемый предел огнестойкости"]]

        with open(Name_File, encoding='utf-8') as file_op:
            profile_steel_dict_in = json.load(file_op)

        data_profile = []
        for i in range(1, self.quan_elem+1):
            data_profile.append([i, profile, self.name_profile, gost, "1.5", "1",
                                "3500", "4", "4.8", "500", "15.5", "45", "1.2", "2.5", "3.5"],)

        data = table_title + data_title + data_profile + table_note
        return data

    def get_surface_area_element(self):
        perimeter = self.get_perimeter_section()
        len_element = self.len_elem
        surface_area = perimeter * len_element
        # log.info(f"Площадь поверхности элемента: {surface_area} м2")
        return surface_area

    def get_output_strength(self):
        log.info("Экспорт данных прочностного расчета")
        """Функция возвращает данные для формирования таблицы csv при экспорте"""

        table_title = [
            ["Данные  стальной контрукции"], [""]]

        data_title = [["№ п/п", "Сортамент", "Обогрев, шт", "ПТМ, мм",
                       "Rсобст., мин", "S, м2", "Ткр, С", "Расход, кг/с", "Кол-во краски"]]

        table_note = [[""],
                      ["Обогрев - количество сторон обогрева, шт"],
                      ["ПТМ - приведенная толщина метала, мм"],
                      ["Rсобст. - собственный предел огнестойкости, мин"],
                      ["Ткр - критическая температура элемента, С"]]

        data_profile = []
        for i in range(1, 11, 1):
            data_profile.append(
                [i, "Сортамент"+[i], 4, "ПТМ", "Rсобст.", "S", "Ткр", "-", "-",])

        data = table_title + data_title + data_profile + table_note

        return data


class SteelFireResistance:
    def __init__(self, i18n: TranslatorRunner, chat_id=None, data=None):
        self.i18n = i18n
        self.chat_id = chat_id
        self.get_init_data(data)

    def get_init_data(self, data):
        self.ptm: float = float(data.get('ptm'))
        self.mode: str = data.get('mode')
        self.s_0: float = float(data.get('s_0'))
        self.s_1: float = float(data.get('s_1'))
        self.T_0: float = float(data.get('T_0'))
        self.t_critic: float = float(data.get('t_critic_C'))
        self.x_min: int = 0
        self.x_max: int = 90 * 60
        self.a_convection: float = float(data.get('a_convection'))
        self.density_steel: float = float(data.get('density_steel'))
        self.heat_capacity: float = float(data.get('heat_capacity'))
        self.heat_capacity_change: float = float(
            data.get('heat_capacity_change'))

    def get_initial_data_thermal(self):
        log.info("Исходные данные для теплотехнического расчета")
        if self.mode == "Углеводородный":
            a_convection = 50
        else:
            a_convection = self.a_convection
        label = 'Теплотехнический расчет'
        headers = ('Параметр', 'Значение', 'Ед.изм.')
        data = [

            {'id': 'Коэффициент изм.\nтеплоемкости стали',
                'var': self.heat_capacity_change, 'unit_1': 'Дж/кг\u00D7К\u00B2'},
            {'id': 'Теплоемкость стали', 'var': self.heat_capacity,
                'unit_1': 'Дж/кг\u00D7К'},
            {'id': 'Степень черноты стали, Sст', 'var': self.s_1, 'unit_1': '-'},
            {'id': 'Плотность стали, \u03C1',
                'var': self.density_steel, 'unit_1': 'кг/м\u00B3'},
            {'id': 'Степень черноты среды, S0', 'var': self.s_0, 'unit_1': '-'},
            {'id': 'Конвективный коэффициент\nтеплоотдачи, \u03B1к',
                'var': a_convection, 'unit_1': 'Вт/м\u00B2\u00D7К'},
            {'id': 'Начальная температура', 'var': self.T_0-273, 'unit_1': '\u00B0С'},
            {'id': 'Критическая температура стали',
                'var': f'{self.t_critic:.2f}', 'unit_1': '\u00B0С'},
            {'id': 'Приведенная толщина\nметалла',
                'var': f'{self.ptm:.2f}', 'unit_1': 'мм'},
            {'id': 'Температурный режим', 'var': self.mode, 'unit_1': '-'}
        ]

        return data, headers, label

    def get_fire_mode(self):
        """Функция возвращает значения изменения температуры от времени"""
        x_max = self.x_max
        if self.t_critic > 750.0 or self.mode == 'Тлеющий':
            x_max = 150 * 60

        Tm = []
        for i in range(self.x_min, x_max, 1):
            if self.mode == 'Углеводородный':
                Tm.append((round(1080 * (1 - 0.325 * m.exp(-0.167 *
                                                           (i / 60)) - 0.675 * m.exp(-2.5 * (i / 60))) + (self.T_0-273))))
            elif self.mode == 'Наружный':
                Tm.append((round(660 * (1 - 0.687 * m.exp(-0.32 * (i / 60)
                                                          ) - 0.313 * m.exp(-3.8 * (i / 60))) + (self.T_0-273))))
            elif self.mode == 'Тлеющий':
                if i <= 21 * 60:
                    Tm.append(
                        (round(154 * ((i / 60) ** 0.25)) + (self.T_0-273)))
                elif i > 21 * 60:
                    Tm.append(
                        (round(345 * m.log10(8 * ((i / 60) - 20) + 1) + (self.T_0-273))))
            else:
                # Стандартный
                Tm.append(
                    round((345 * m.log10(8 / 60 * i + 1) + (self.T_0-273))))

        return Tm

    def get_steel_heating(self):
        log.info("Прогрев элемента конструкции по уравнению Яковлева А.И.")
        '''Прогрев элемента конструкции по уравнению Яковлева А.И. при тепловом воздействии по ГОСТ 30247.0 и ГОСТ Р ЕН 1363-2'''
        # приведенная степень черноты
        if self.mode == "Углеводородный":
            a_convection = 50
        else:
            a_convection = self.a_convection

        spr = 1 / ((1 / self.s_0) + (1 / self.s_1) - 1)
        x_max = self.x_max
        if self.t_critic > 750.0 or self.mode == 'Тлеющий':
            x_max = 150 * 60

        Tst = [self.T_0]
        time = [0]
        temperature_element = [20]

        for i in range(1, x_max, 1):
            time.append(i)

            if self.mode == 'Углеводородный':
                Tn = 1080 * (1 - 0.325 * m.exp(-0.167 * (i / 60)) -
                             0.675 * m.exp(-2.5 * (i / 60))) + self.T_0  # Углеводородный
            elif self.mode == 'Наружный':
                Tn = 660 * (1 - 0.687 * m.exp(-0.32 * (i / 60)) -
                            0.313 * m.exp(-3.8 * (i / 60))) + self.T_0  # Наружный
            elif self.mode == 'Тлеющий':
                if i <= 21 * 60:
                    Tn = (154 * ((i / 60) ** 0.25)) + self.T_0  # Тлеющий
                elif i > 21 * 60:
                    Tn = 345 * m.log10(8 * ((i / 60) - 20) + 1) + self.T_0
            else:
                Tn = 345 * m.log10(8 / 60 * i + 1) + self.T_0  # Стандартный

            an = a_convection + 5.77 * spr * \
                (((Tn / 100) ** 4 - (Tst[i - 1] / 100)
                 ** 4) / (Tn - Tst[i - 1]))

            Tsti = Tst[i - 1] + an * ((Tn - Tst[i - 1]) * (1 /
                                                           (self.density_steel * (self.ptm*0.001) * (self.heat_capacity + self.heat_capacity_change * Tst[i - 1]))))
            Tst.append((Tsti))
            temperature_element.append(Tsti - 273)

        return temperature_element

    def get_steel_fsr(self):
        Tst = self.get_steel_heating()
        time = [0]
        x_max = self.x_max
        if self.t_critic > 750.0 or self.mode == 'Тлеющий':
            x_max = 150 * 60

        for i in range(1, x_max, 1):
            time.append(i)

        t_fsr = interp1d(Tst, time, kind='slinear',
                         bounds_error=False, fill_value=0)

        # Определение времени прогрева от температуры
        time_fsr = float(t_fsr(self.t_critic))/60
        # log.info(f"Предел огнестойкости стального элемента: {time_fsr} мин")
        return time_fsr

    def get_plot_steel(self, label_plot):
        log.info("График прогрева элемента конструкции")
        # размеры рисунка в дюймах
        px = 96.358115  # 1 дюйм = 2.54 см = 96.358115 pixel
        w = 700  # px
        h = 700  # px
        left = 0.130
        bottom = 0.090
        right = 0.970
        top = 0.900
        hspace = 0.100
        # xmin = 0.0
        # ymin = 0.0
        xmax = 4.0
        # ymax = 0.5

        margins = {
            "left": left,  # 0.030
            "bottom": bottom,  # 0.030
            "right": right,  # 0.970
            "top": top,  # 0.900
            "hspace": hspace  # 0.200
        }
        fig = plt.figure(figsize=(w / px, h / px),
                         dpi=300, constrained_layout=False)
        fig.subplots_adjust(**margins)
        # plt.style.use('bmh')
        plt.style.use('Solarize_Light2')
        widths = [1.0]
        heights = [xmax]
        gs = gridspec.GridSpec(
            ncols=1, nrows=1, width_ratios=widths, height_ratios=heights)
        ft_label_size = {'fontname': 'Arial', 'fontsize': w*0.021}
        # ft_title_size = {'fontname': 'Arial', 'fontsize': 8}
        ft_size = {'fontname': 'Arial', 'fontsize': 12}
        logo = plt.imread('temp_files/temp/logo.png')
        # logo = image.imread('temp_files/temp/logo.png')
        # logo = plt.imread('logo.png')
        # [left, bottom, width, height]
        fig_ax_1 = fig.add_axes(
            [0.03, 0.0, 1.0, 1.86], frameon=True, aspect=1.0, xlim=(0.0, xmax+0.25))
        fig_ax_1.axis('off')
        fig_ax_1.text(x=0.0, y=0.025, s='Прогрев элемента конструкции',
                      weight='bold', ha='left', **ft_label_size)
        fig_ax_1.plot([0, xmax], [0.0, 0.0], lw='1.0',
                      color=(0.913, 0.380, 0.082, 1.0))
        imagebox = OffsetImage(logo, zoom=w*0.000085, dpi_cor=True)
        ab = AnnotationBbox(imagebox, (xmax-(xmax/33.3), 0.025),
                            frameon=False, pad=0, box_alignment=(0.00, 0.0))
        fig_ax_1.add_artist(ab)

        fig_ax_2 = fig.add_subplot(gs[0, 0])

        # fig_ax_2.set_xlim(0.0, cols+0.5)
        # fig_ax_2.set_ylim(-.75, rows+0.55)

        # title_plot = 'График прогрева стального элемента'
        # fig_ax_2.set_title(f'{title_plot}\n', fontsize=18,
        #                    alpha=1.0, clip_on=False, y=1.0)
        # if self.mode == 'Углеводородный':
        #     rl = "Углеводородный режим"
        # elif self.mode == 'Наружный':
        #     rl = "Наружный"
        # elif self.mode == 'Тлеющий':
        #     rl = "Тлеющий"
        # else:
        #     rl = "Стандартный"

        label_plot_Tst = f'Температура элемента'
        Tm = self.get_fire_mode()
        Tst = self.get_steel_heating()
        Tcr = self.t_critic
        time_fsr = self.get_steel_fsr() * 60

        x_max = self.x_max
        y_max = max(Tm)  # if self.mode != 'Наружный' else 500
        if self.t_critic > 750.0 or self.mode == 'Тлеющий':
            x_max = 150 * 60

        tt = range(0, x_max, 1)
        x_t = []
        for i in tt:
            x_t.append(i)

        fig_ax_2.plot(x_t, Tm, '-', linewidth=3,
                      label=label_plot, color=(0.9, 0.1, 0, 0.9))
        fig_ax_2.plot(x_t, Tst, '-', linewidth=3,
                      label=label_plot_Tst, color=(0, 0, 0, 0.9))

        fig_ax_2.hlines(y=Tcr, xmin=0, xmax=time_fsr*0.96, linestyle='--',
                        linewidth=1, color=(0.1, 0.1, 0, 1.0))
        fig_ax_2.vlines(x=time_fsr, ymin=0, ymax=Tcr*0.98, linestyle='--',
                        linewidth=1, color=(0.1, 0.1, 0, 1.0))
        fig_ax_2.scatter(time_fsr, Tcr, s=90, marker='o',
                         color=(0.9, 0.1, 0, 1))

        # Ось абсцисс Xaxis
        fig_ax_2.set_xlim(-100.0, self.x_max+100)
        fig_ax_2.set_xlabel(xlabel="Время, с", fontdict=None,
                            labelpad=None, weight='bold', loc='center', **ft_size)
        # Ось абсцисс Yaxis
        fig_ax_2.set_ylim(0, y_max + 200)
        fig_ax_2.set_ylabel(ylabel="Температура, \u00B0С",
                            fontdict=None, labelpad=None, weight='bold', loc='center', **ft_size)

        fig_ax_2.annotate(f"Режим пожара: {self.mode}\n"
                          f"Предел огнестойкости: {(time_fsr / 60):.2f} мин\n"
                          f"Критическая температура: {Tcr:.1f} \u00B0С\n"
                          f"Приведенная толщина элемента: {self.ptm:.2f} мм",
                          xy=(0.0, y_max), xycoords='data', xytext=(0.0, y_max + 25), textcoords='data', weight='bold', **ft_size)

        # Легенда
        fig_ax_2.legend(fontsize=12, framealpha=0.85, facecolor="w", loc=4)

        # Цветовая шкала
        # plt.colorbar()
        # Подпись горизонтальной оси абсцисс OY -> cbar.ax.set_xlabel();
        # Подпись вертикальной оси абсцисс OY -> cbar.ax.set_ylabel();

        # Деления на оси абсцисс OX
        fig_ax_2.set_xticks(np.arange(min(x_t), max(x_t), 1000.0), minor=False)

        # Деления на оси ординат OY
        fig_ax_2.set_yticks(np.arange(0, y_max+200, 100.0), minor=False)

        # Вспомогательная сетка (grid)
        fig_ax_2.grid(visible=True,
                      which='major',
                      axis='both',
                      color=(0, 0, 0, 0.5),
                      linestyle=':',
                      linewidth=0.250)

        # directory = get_temp_folder(fold_name='temp_pic')
        # name_plot = "".join(['fig_steel_fr_', str(self.chat_id), '.png'])
        # name_dir = '/'.join([directory, name_plot])
        # fig.savefig(name_dir, format='png', transparent=True)
        # plt.cla()
        # plt.close(fig)
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        plot_thermal_png = buffer.getvalue()
        buffer.close()
        plt.cla()
        plt.style.use('default')
        plt.close(fig)

        return time_fsr, plot_thermal_png

    def get_data_steel_heating(self):
        log.info("Экспорт данных теплотехнического расчета")
        table_title = [
            ["Данные прогрева незащищенной стальной контрукции"],
            [""],
            [f"Режим пожара: {self.mode}"],
            [f"ПТМ: {round(self.ptm, 2)}"],
            [""]]

        table_note = [
            ["ПТМ - приведенная толщина метала, мм"],
            ["Тв - температура среды"],
            ["Тст - температура элемента"],
            [""]]

        data_title = [["Время, с", "Тв, С", "Тст, С", ]]

        Tm = self.get_fire_mode()
        Tst = self.get_steel_heating()

        data_profile = []
        for i in range(self.x_min, self.x_max, 1):
            data_profile.append(
                [i, Tm[i], Tst[i],])
        data = table_title + table_note + data_title + data_profile

        return data


class SteelFireProtection(SteelFireStrength, SteelFireResistance):

    def __init__(self, i18n: TranslatorRunner, chat_id=None):
        self.i18n = i18n
        self.chat_id = chat_id
        self.creat_init_data_table()

    def creat_init_data_table(self):
        chat_id = self.chat_id
        with open('app/infrastructure/init_data/init_data_protection_steel.json', encoding='utf-8') as file_op:
            init_protection_in = json.load(file_op)
            if chat_id not in init_protection_in:
                init_protection_in[chat_id] = []
                with open('app/infrastructure/init_data/init_data_protection_steel.json', 'w', encoding='utf-8') as file_w:
                    json.dump(init_protection_in, file_w,
                              ensure_ascii=False, indent=4)

    def get_init_data_table(self) -> list:
        chat_id = self.chat_id
        with open('app/infrastructure/init_data/init_data_protection_steel.json', encoding='utf-8') as file_op:
            init_protection_in = json.load(file_op)
            if len(init_protection_in[chat_id]) == 0:
                init_protection_in[chat_id].append(
                    {'id': '-',
                     'num_profile': '-',
                     'type_steel_element': '-',
                     'num_sides_heated': '-',
                     'ptm': '-',
                     'len_elem': '-',
                     'area_surface_elem_m2': '-',
                     'n_load': '-',
                     't_critic_C': '-',
                     'time_fsr': '-'})
                with open('app/infrastructure/init_data/init_data_protection_steel.json', 'w', encoding='utf-8') as file_w:
                    json.dump(init_protection_in, file_w,
                              ensure_ascii=False, indent=4)

        data_table = init_protection_in[chat_id]
        return data_table

    def get_init_data_other_table(self, element: str = None) -> list:
        chat_id = self.chat_id
        if element != None:
            with open('app/infrastructure/init_data/init_data_protection_steel.json', encoding='utf-8') as file_op:
                init_protection_in = json.load(file_op)
                num_elem = len(init_protection_in[chat_id])
                elements = []
                for i in range(num_elem):
                    elements.append(
                        init_protection_in[chat_id][i]["num_profile"])
                log.info(f"список номеров профилей: {elements}")
                if len(init_protection_in[chat_id]) == 0:
                    init_protection_in[chat_id].append(
                        {'id': len(init_protection_in[chat_id])+1,
                         'num_profile': element,
                         'type_steel_element': '-',
                         'num_sides_heated': '-',
                         'ptm': '-',
                         'len_elem': '-',
                         'area_surface_elem_m2': '-',
                         'n_load': '-',
                         't_critic_C': '-',
                         'time_fsr': '-'})
                    with open('app/infrastructure/init_data/init_data_protection_steel.json', 'w', encoding='utf-8') as file_w:
                        json.dump(init_protection_in, file_w,
                                  ensure_ascii=False, indent=4)
                elif len(init_protection_in[chat_id]) == 1:
                    if init_protection_in[chat_id][-1]["id"] == 1 and init_protection_in[chat_id][num_elem -
                                                                                                  1]["num_profile"] == element:

                        init_protection_in[chat_id][num_elem -
                                                    1]["id"] = num_elem
                        init_protection_in[chat_id][num_elem -
                                                    1]["num_profile"] = element
                        with open('app/infrastructure/init_data/init_data_protection_steel.json', 'w', encoding='utf-8') as file_w:
                            json.dump(init_protection_in, file_w,
                                      ensure_ascii=False, indent=4)

                    elif init_protection_in[chat_id][-1]["id"] == '-':
                        init_protection_in[chat_id][num_elem -
                                                    1]["id"] = num_elem
                        init_protection_in[chat_id][num_elem -
                                                    1]["num_profile"] = element
                        with open('app/infrastructure/init_data/init_data_protection_steel.json', 'w', encoding='utf-8') as file_w:
                            json.dump(init_protection_in, file_w,
                                      ensure_ascii=False, indent=4)
                    else:
                        init_protection_in[chat_id].append(
                            {'id': num_elem+1,
                             'num_profile': element,
                             'type_steel_element': '-',
                             'num_sides_heated': '-',
                             'ptm': '-',
                             'len_elem': '-',
                             'area_surface_elem_m2': '-',
                             'n_load': '-',
                             't_critic_C': '-',
                             'time_fsr': '-'})
                        with open('app/infrastructure/init_data/init_data_protection_steel.json', 'w', encoding='utf-8') as file_w:
                            json.dump(init_protection_in, file_w,
                                      ensure_ascii=False, indent=4)
                elif len(init_protection_in[chat_id]) > 1 and element not in elements:
                    init_protection_in[chat_id].append(
                        {'id': num_elem+1,
                            'num_profile': element,
                            'type_steel_element': '-',
                            'num_sides_heated': '-',
                            'ptm': '-',
                            'len_elem': '-',
                            'area_surface_elem_m2': '-',
                            'n_load': '-',
                            't_critic_C': '-',
                            'time_fsr': '-'})
                    with open('app/infrastructure/init_data/init_data_protection_steel.json', 'w', encoding='utf-8') as file_w:
                        json.dump(init_protection_in, file_w,
                                  ensure_ascii=False, indent=4)

        with open('app/infrastructure/init_data/init_data_protection_steel.json', encoding='utf-8') as file_op:
            init_protection_in = json.load(file_op)
            data_table = init_protection_in[chat_id]
        return data_table

    def get_initial_data_protection(self, data):
        log.info("Исходные данные для пакетного расчета")
        # data = self.get_init_data_table()
        rows = len(data)
        cols = len(list(data[0]))
        label_key = list(data[0])
        # log.info(f'{list(data[0])}')
        title_colm = ['№ п/п',
                      'Сортамент',
                      'Марка стали',
                      'Стороны\nобогрева',
                      'ПТМ, мм',
                      'Длина, мм',
                      'Поверхность\nэлемента, м\u00B2',
                      'Нагрузка, кг',
                      'Ткр, С',
                      'Rсобств, мин']

        # размеры рисунка в дюймах
        # 1 дюйм = 2.54 см = 96.358115 pixel
        px = 96.358115
        w = 1200 * (cols/10)  # px
        h = 600 * (rows/10)  # px
        if w > 1200:
            w = 1200
        elif w < 400:
            w = 400

        if h > 1200:
            h = 1100
        elif h < 150:
            h = 150

        log.info(f"ширина таблицы (w)={w}, высота таблицы (h)={h}")

        max_x = cols
        coef_colm = max_x / cols

        # Создание объекта Figure
        margins = {
            "left": 0.030,  # 0.030
            "bottom": 0.030,  # 0.030
            "right": 0.970,  # 0.970
            "top": 0.900  # 0.900
        }
        if rows <= 3:
            margins = {
                "left": 0.030,  # 0.030
                "bottom": 0.030,  # 0.030
                "right": 0.970,  # 0.970
                "top": 0.800  # 0.900
            }
        fig = plt.figure(figsize=(w / px, h / px), dpi=350)
        fig.subplots_adjust(**margins)
        ax = fig.add_subplot()

        ax.set_xlim(0.0, max_x*0.95)
        ax.set_ylim(-.5, rows*1.025)

        # добавить заголовки столбцов на высоте y=..., чтобы уменьшить пространство до первой строки данных
        ft_title_size = {'fontname': 'Arial', 'fontsize': 10}

        hor_up_line = rows-0.35
        for colm in range(0, cols):
            ha = 'center'
            weight = 'bold'
            if colm == 0:
                ha = 'left'
            ax.text(x=colm*coef_colm, y=hor_up_line,
                    s=title_colm[colm], weight=weight, ha=ha, **ft_title_size)

        # добавить основной разделитель заголовка
        ax.plot([0, cols], [rows-0.5, rows-0.5], lw='2', c='black')
        # ax.plot([0, cols + .5], [- 0.5, - 0.5], lw='2', c='black')

        # линия сетки
        for row in range(rows):
            ax.plot([0, cols], [row - .5, row - .5],
                    ls=':', lw='.8', c='grey')

        # заполнение таблицы данных
        ft_size = {'fontname': 'Arial', 'fontsize': 12}

        data = data[::-1]
        for row in np.arange(rows):
            for colm in np.arange(cols):
                d = data[row]
                ha = 'center'
                va = 'center'
                weight = 'bold'
                if colm == 0:
                    ha = 'left'
                ax.text(x=colm*coef_colm, y=row,
                        s=d[label_key[colm]], va=va, ha=ha, **ft_size)

        # выделите столбец, используя прямоугольную заплатку
        # rect = patches.Rectangle((2.0, -0.5),  # нижняя левая начальная позиция (x,y)
        #                          width=1,
        #                          height=hor_up_line+0.95,
        #                          ec='none',
        #                          fc='grey',
        #                          alpha=.2,
        #                          zorder=-1)
        # ax.add_patch(rect)

        ax.set_title(label='Ведомость огнестойкости стальных элементов',
                     loc='left', fontsize=12, weight='bold')
        ax.axis('off')

        buffer = io.BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.cla()
        plt.close(fig)

        return image_png

    def clear_table_protection(self):
        chat_id = self.chat_id
        with open('app/infrastructure/init_data/init_data_protection_steel.json', encoding='utf-8') as file_op:
            init_protection_in = json.load(file_op)
            if chat_id in init_protection_in:
                init_protection_in[chat_id] = []
                with open('app/infrastructure/init_data/init_data_protection_steel.json', 'w', encoding='utf-8') as file_w:
                    json.dump(init_protection_in, file_w,
                              ensure_ascii=False, indent=4)
        data_table = self.get_init_data_table()
        return data_table
