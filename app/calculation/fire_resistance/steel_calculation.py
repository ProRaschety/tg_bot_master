import logging

from app.tg_bot.utilities.misc_utils import get_temp_folder

import math as m
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from scipy.interpolate import interp1d

logger = logging.getLogger(__name__)


class SteelStrength:
    def __init__(self,
                 chat_id,
                 name_profile,
                 sketch,
                 reg_document,
                 num_sides_heated=4,
                 fixation='beams_sealing_both_ends',
                 q_load=1,
                 n_load=1,
                 a_load=1,
                 type_loading='stretching_element',
                 len_elem=1):

        self.chat_id
        self.name_profile: str = name_profile
        self.sketch: str = sketch
        self.gost: str = reg_document
        self.num_sides_heated: int = num_sides_heated
        self.len_elem: float = len_elem
        self.fixation: str = fixation
        self.q_load: float = q_load
        self.n_load: float = n_load  # kgs
        self.a_load: float = a_load
        # 'stretching_element', 'compression_element'
        self.type_loading: str = type_loading
        self.e_n: float = 2_100_000  # начальный модуль упругости металла, кг/см2
        self.quan_elem: int = 5

    def get_initial_data_strength(self):
        num_sides_heated = self.num_sides_heated     # 4
        profile = self.name_profile     # "Двутавр"
        sketch = self.sketch            #
        gost = self.gost                # "ГОСТ_Р_57837_2017"
        ptm = self.get_reduced_thickness
        t_critic = self.get_crit_temp_steel
        if profile == "Двутавр":
            with open(file="app/infrastructure/data_base/db_steel_ibaem.json", mode="r", encoding='utf-8') as file_op:
                db_steel_in = json.load(file_op)
                h_mm = db_steel_in[profile][gost][sketch]["h_mm"]
                b_mm = db_steel_in[profile][gost][sketch]["b_mm"]
                s_mm = db_steel_in[profile][gost][sketch]["s_mm"]

            data = [
                {'id': 'Способ закрепления', 'var': self.T_0-273, 'unit': '\u00B0С'},
                {'id': 'Требуемый предел огнестойкости',
                    'var': self.sketch, 'unit': '-'},
                {'id': 'Собстенный предел огнестойкости',
                    'var': self.sketch, 'unit': '-'},
                {'id': 'Критическая температура стали',
                    'var': t_critic, 'unit': '\u00B0С'},
                {'id': 'Приведенная толщина\nметалла', 'var': ptm, 'unit': 'мм'},
                {'id': 'Количество сторон обогрева',
                    'var': self.sketch, 'unit': 'шт'},
                {'id': 'Нагрузка', 'var': self.sketch, 'unit': 'кг'},
                {'id': 'Профиль по ГОСТ', 'var': self.gost, 'unit': '-'},
                {'id': 'Эскиз', 'var': self.sketch, 'unit': '-'},
                {'id': 'Профиль', 'var': self.name_profile, 'unit': '-'}
            ]

        elif profile == "Швеллер":
            data = [
                {'id': 'Коэффициент изм.\nтеплоемкости стали',
                 'var': self.heat_capacity_change, 'unit': 'Дж/кг\u00D7град\u00B2'},
                {'id': 'Теплоемкость стали', 'var': self.heat_capacity,
                 'unit': 'Дж/кг\u00D7град'},
                {'id': 'Степень черноты стали, Sст', 'var': self.s_1, 'unit': '-'},
                {'id': 'Плотность стали, \u03C1',
                 'var': self.density_steel, 'unit': 'кг/м\u00B3'},
                {'id': 'Степень черноты среды, S0', 'var': self.s_0, 'unit': '-'},
                {'id': 'Конвективный коэффициент\nтеплоотдачи, \u03B1к',
                 'var': self.a_convection, 'unit': 'Вт/м\u00B2\u00D7К'},
                {'id': 'Начальная температура',
                    'var': self.T_0-273, 'unit': '\u00B0С'},
                {'id': 'Критическая температура стали',
                 'var': self.t_critic, 'unit': '\u00B0С'},
                {'id': 'Приведенная толщина\nметалла',
                    'var': self.ptm, 'unit': 'мм'},
                {'id': 'Температурный режим', 'var': self.mode, 'unit': '-'}
            ]

            with open(file="app/infrastructure/data_base/db_steel_channel.json", mode="r", encoding='utf-8') as file_op:
                db_steel_in = json.load(file_op)
                h_mm = db_steel_in[profile][gost][sketch]["h_mm"]

        # data = [

        #     {'id': 'Коэффициент изм.\nтеплоемкости стали',
        #         'var': self.heat_capacity_change, 'unit': 'Дж/кг\u00D7град\u00B2'},
        #     {'id': 'Теплоемкость стали', 'var': self.heat_capacity,
        #         'unit': 'Дж/кг\u00D7град'},
        #     {'id': 'Степень черноты стали, Sст', 'var': self.s_1, 'unit': '-'},
        #     {'id': 'Плотность стали, \u03C1',
        #         'var': self.density_steel, 'unit': 'кг/м\u00B3'},
        #     {'id': 'Степень черноты среды, S0', 'var': self.s_0, 'unit': '-'},
        #     {'id': 'Конвективный коэффициент\nтеплоотдачи, \u03B1к',
        #         'var': self.a_convection, 'unit': 'Вт/м\u00B2\u00D7К'},
        #     {'id': 'Начальная температура', 'var': self.T_0-273, 'unit': '\u00B0С'},
        #     {'id': 'Критическая температура стали',
        #         'var': self.t_critic, 'unit': '\u00B0С'},
        #     {'id': 'Приведенная толщина\nметалла', 'var': self.ptm, 'unit': 'мм'},
        #     {'id': 'Температурный режим', 'var': self.mode, 'unit': '-'}
        # ]

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
        fig = plt.figure(figsize=(w / px, h / px), dpi=200)
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
            # unit column
            ax.text(x=3.5, y=row, s=d['unit'],
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

        directory = get_temp_folder()
        name_plot = "".join(
            ['fig_init_data_strength_', str(self.chat_id), '.png'])
        name_dir = '/'.join([directory, name_plot])

        fig.savefig(name_dir, format='png')
        plt.cla()
        plt.close(fig)

        return name_dir

    def get_sectional_area(self):
        """Опеределение площади сечения элемента в мм2"""
        profile = self.name_profile     # "Двутавр"
        sketch = self.sketch            # 30К10
        gost = self.gost                # "ГОСТ_Р_57837_2017"
        if profile == "Двутавр":
            with open(file="db_steel_ibeam.json", mode="r", encoding='utf-8') as file_op:
                db_steel_in = json.load(file_op)
                sec_area_cm2 = db_steel_in[profile][gost][sketch]['a_cm2']
        elif profile == "Швеллер":
            with open(file="db_steel_channel.json", mode="r", encoding='utf-8') as file_op:
                db_steel_in = json.load(file_op)
                sec_area_cm2 = db_steel_in[profile][gost][sketch]['a_cm2']
        sectional_area = float(sec_area_cm2) * 100  # мм2
        return sectional_area

    def get_perimeter_section(self):
        num_sides_heated = self.num_sides_heated     # 4
        profile = self.name_profile     # "Двутавр"
        sketch = self.sketch            #
        gost = self.gost                # "ГОСТ_Р_57837_2017"

        if profile == "Двутавр":
            with open(file="db_steel_ibeam.json", mode="r", encoding='utf-8') as file_op:
                db_steel_in = json.load(file_op)
                h_mm = db_steel_in[profile][gost][sketch]["h_mm"]
                b_mm = db_steel_in[profile][gost][sketch]["b_mm"]
                s_mm = db_steel_in[profile][gost][sketch]["s_mm"]

        elif profile == "Швеллер":
            with open(file="db_steel_channel.json", mode="r", encoding='utf-8') as file_op:
                db_steel_in = json.load(file_op)
                h_mm = db_steel_in[profile][gost][sketch]["h_mm"]

        if profile == "Двутавр":
            if num_sides_heated == 3:
                perimeter_section = 2 * \
                    float(h_mm) + 3 * float(b_mm) - 2 * float(s_mm)
            else:
                perimeter_section = 2 * \
                    float(h_mm) + 4 * float(b_mm) - 2 * float(s_mm)

        elif profile == "Швеллер":
            if num_sides_heated == 3:
                perimeter_section = 2 * \
                    float(h_mm) + 3 * float(b_mm) - 2 * float(s_mm)
            else:
                perimeter_section = 2 * \
                    float(h_mm) + 4 * float(b_mm) - 2 * float(s_mm)

        return perimeter_section

    def get_moment_section_resistance(self):
        """момент сопротивления сечения, см3"""
        type_loading = self.type_loading
        len_elem = self.len_elem
        fixation = self.fixation

        moment_section_resistance = 0
        if type_loading == 'distributed_load':                              # распределенная нагрузка
            if fixation == 'beams_sealing_both_ends':                       # балок с заделкой по обоим концам
                # для консольных балок с заделкой с одного конца без опирания с другого
                moment_section_resistance = (q_load * len_elem ** 2)/12
            elif fixation == 'cantilever_beams_sealing_one_end':
                moment_section_resistance = (q_load * len_elem ** 2) / 2

        elif type_loading == 'concentrated_load':                           # сосредоточенная нагрузка
            # балок с заделкой с обоих концов и сосредоточенной силе N_n посередине
            if fixation == 'beams_sealing_both_ends':
                moment_section_resistance = (q_load * len_elem ** 2) / 12
            # для балок с заделкой с одного конца, второй свободен, где сила N_n давит на свободный конец
            elif fixation == 'beams_sealing_one_end_second_free_dist':
                moment_section_resistance = n_load * len_elem
            # для балок с заделкой с одного конца, второй свободен, где сила N_n давит на расстоянии a от заделки
            elif fixation == 'beams_sealing_one_end_second_free_dist':
                moment_section_resistance = n_load * a_load

        return moment_section_resistance

    def get_reduced_thickness(self):
        sectional_area = self.get_sectional_area()
        perimeter_section = self.get_perimeter_section()
        ptm = sectional_area/perimeter_section
        return ptm

    def get_coef_strength(self):
        sectional_area = self.get_sectional_area()
        moment_section_resistance = self.get_moment_section_resistance()
        fixation = self.fixation

        m_norm = 1              # максимальный изгибающий момент, kg*cm

        type_loading = self.type_loading  # stretching_element, compression_element

        if type_loading == 1:
            # если элемент защемлен с одного конца, с другого конца свободен(консоль);
            mu = 2
        elif type_loading == 2:
            mu = 1              # если элемент имеет шарнирное опирание по обоим  концам;
        elif type_loading == 3:
            mu = 0.7            # если элемент защемлен с одного конца, с другого шарнирно оперт;
        elif type_loading == 4:
            # если рассматриваемый элемент защемлен по обоим концам.
            mu = 0.5

        mu = 1                  # коэффициент приведения длины элемента;

        j_min = 1               # наименьший момент инерции сечения элемента, см4;
        l_eff = mu * self.len_elem   # расчетная эффективная длина элемента, см;
        r_norm = 3850           # нормативное сопротивление металла, кг/см2;

        # Температурный коэффициент снижения предела текучести стали при изгибе
        gamma_t_bending = self.n_load / (moment_section_resistance * r_norm)
        # Температурный коэффициент снижения предела текучести стали при растяжении (сжатии)
        gamma_t_comp = self.n_load / (sectional_area * r_norm)
        # Температурный коэффициент снижения модуля упругости стали при сжатии
        gamma_elasticity = (self.n_load * l_eff ** 2) / \
            (3.14159**2 * self.e_n * j_min)

        gamma = 1

        return gamma

    def get_crit_temp_steel(self):
        gamma_t = self.get_coef_strength()

        t_critic = 1

        return t_critic

    def get_data_steel_strength(self):
        # Добавляем вид профиля "Двутавр", "Швеллер", "Уголок", "Профиль"
        profile = self.name_profile
        # Section = section  # "RECTANGLE"
        name_profile = self.sketch
        gost = self.gost                        # Добавляем наименование документа

        if profile == "Двутавр":
            Name_File = 'db_steel_ibeam.json'
        elif profile == "Швеллер":
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
            data_profile.append([i, profile, name_profile, gost, "1.5", "1",
                                "3500", "4", "4.8", "500", "15.5", "45", "1.2", "2.5", "3.5"],)

        data = table_title + data_title + data_profile + table_note
        return data


class SteelFR:
    def __init__(
            self,
            chat_id=0,
            ptm=4.8,
            mode='Стандартный',
            s_0=0.85,
            s_1=0.625,
            T_0=293.0,
            t_critic=500.0,
            xmax=90,
            a_convection=29.0,
            density_steel=7800.0,
            heat_capacity=310.0,
            heat_capacity_change=0.469,
    ):

        self.chat_id = chat_id
        self.ptm = float(ptm)
        self.mode = mode
        self.s_0 = s_0
        self.s_1 = s_1
        self.T_0 = T_0
        self.t_critic = float(t_critic)
        self.x_min = 0
        self.x_max = xmax * 60
        self.a_convection = float(a_convection)
        self.density_steel = float(density_steel)
        self.heat_capacity = float(heat_capacity)
        self.heat_capacity_change = float(heat_capacity_change)

    def get_initial_data_thermal(self):
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
        fig = plt.figure(figsize=(w / px, h / px), dpi=200)
        fig.subplots_adjust(**margins)
        ax = fig.add_subplot()

        data = [

            {'id': 'Коэффициент изм.\nтеплоемкости стали',
                'var': self.heat_capacity_change, 'unit': 'Дж/кг\u00D7град\u00B2'},
            {'id': 'Теплоемкость стали', 'var': self.heat_capacity,
                'unit': 'Дж/кг\u00D7град'},
            {'id': 'Степень черноты стали, Sст', 'var': self.s_1, 'unit': '-'},
            {'id': 'Плотность стали, \u03C1',
                'var': self.density_steel, 'unit': 'кг/м\u00B3'},
            {'id': 'Степень черноты среды, S0', 'var': self.s_0, 'unit': '-'},
            {'id': 'Конвективный коэффициент\nтеплоотдачи, \u03B1к',
                'var': self.a_convection, 'unit': 'Вт/м\u00B2\u00D7К'},
            {'id': 'Начальная температура', 'var': self.T_0-273, 'unit': '\u00B0С'},
            {'id': 'Критическая температура стали',
                'var': self.t_critic, 'unit': '\u00B0С'},
            {'id': 'Приведенная толщина\nметалла', 'var': self.ptm, 'unit': 'мм'},
            {'id': 'Температурный режим', 'var': self.mode, 'unit': '-'}
        ]

        rows = len(data)
        cols = len(list(data[0]))

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
            # unit column
            ax.text(x=3.5, y=row, s=d['unit'],
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

        ax.set_title(label='Исходные данные\nдля теплотехнического расчета',
                     loc='left', fontsize=12, weight='bold')
        ax.axis('off')

        directory = get_temp_folder(
            fold_name='temp_pic')
        name_plot = f'fig_init_data_thermal_{str(self.chat_id)}.png'
        # "".join(
        # ['fig_init_data_thermal_', str(self.chat_id), '.png'])
        name_dir = '/'.join([directory, name_plot])

        fig.savefig(name_dir, format='png')
        plt.cla()
        plt.close(fig)

        return name_dir

    def get_fire_mode(self):
        """
        функция возвращает значения изменения температуры от времени

        Параметры
        ----------
        Args:
            mode: str, режим теплового воздействия (стандартный, углеводородный, наружный, тлеющий)
            time: int, длительность теплового воздействия (с)

        Результат
        ----------
        Tm: [int], список значений температуры

        """
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

        logger.info("Steel heating analysis requested")

        '''Прогрев элемента конструкции по уравнению Яковлева А.И. при тепловом воздействии по ГОСТ 30247.0 и ГОСТ Р ЕН 1363-2'''
        # приведенная степень черноты
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

            an = self.a_convection + 5.77 * spr * \
                (((Tn / 100) ** 4 - (Tst[i - 1] / 100)
                 ** 4) / (Tn - Tst[i - 1]))

            Tsti = Tst[i - 1] + an * ((Tn - Tst[i - 1]) * (1 /
                                                           (self.density_steel * (self.ptm*0.001) * (self.heat_capacity + self.heat_capacity_change * Tst[i - 1]))))
            Tst.append((Tsti))
            temperature_element.append(Tsti - 273)

        return temperature_element

    def get_steel_fsr(self):
        logger.info("Steel fsr analysis requested")

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
        time_fsr = round(float(t_fsr(self.t_critic))/60, 1)

        return time_fsr

    def get_plot_steel(self):
        logger.info("Steel heating plot requested")
        # размеры рисунка в дюймах
        inch = 2.54  # 1 дюйм = 2.54 см = 96.358115 pixel
        px = 96.358115
        w = 700  # px
        h = 700  # px

        # Создание объекта Figure
        fig = plt.figure(figsize=(w/px, h/px), dpi=200)

        mpl.style.use('classic')
        # plt.xkcd()
        mpl.rcParams['font.family'] = 'fantasy'
        mpl.rcParams['font.fantasy'] = 'Arial'
        mpl.rcParams["axes.labelsize"] = 14
        mpl.rcParams["axes.titlesize"] = 18
        mpl.rcParams["xtick.labelsize"] = 12
        mpl.rcParams["ytick.labelsize"] = 12

        # Область рисования Axes
        ax = fig.add_subplot(1, 1, 1)

        title_plot = 'График прогрева стального элемента'
        ax.set_title(f'{title_plot}\n')

        if self.mode == 'Углеводородный':
            rl = "Углеводородный режим"
        elif self.mode == 'Наружный':
            rl = "Наружный режим"
        elif self.mode == 'Тлеющий':
            rl = "Тлеющий режим"
        else:
            rl = "Стандартный режим"

        label_plot_Tst = f'Температура элемента'

        Tm = self.get_fire_mode()
        Tst = self.get_steel_heating()
        Tcr = self.t_critic
        time_fsr = self.get_steel_fsr() * 60

        x_max = self.x_max
        if self.t_critic > 750.0 or self.mode == 'Тлеющий':
            x_max = 150 * 60

        tt = range(0, x_max, 1)
        x_t = []
        for i in tt:
            x_t.append(i)

        ax.plot(x_t, Tm, '-', linewidth=3,
                label=f'{rl}', color=(0.9, 0.1, 0, 0.9))
        ax.plot(x_t, Tst, '-', linewidth=3,
                label=label_plot_Tst, color=(0, 0, 0, 0.9))

        ax.hlines(y=Tcr, xmin=0, xmax=time_fsr*0.96, linestyle='--',
                  linewidth=1, color=(0.1, 0.1, 0, 1.0))
        ax.vlines(x=time_fsr, ymin=0, ymax=Tcr*0.98, linestyle='--',
                  linewidth=1, color=(0.1, 0.1, 0, 1.0))

        ax.scatter(time_fsr, Tcr, s=90, marker='o', color=(0.9, 0.1, 0, 1))

        # Ось абсцисс Xaxis
        ax.set_xlim(-100.0, self.x_max+100)
        ax.set_xlabel(xlabel=r"Время, [с]", fontdict=None,
                      labelpad=None, loc='right')

        # Ось абсцисс Yaxis
        ax.set_ylim(0, max(Tm) + 200)
        set_y_label = str(f'Температура, [\u00B0С]')
        ax.set_ylabel(ylabel=f"{set_y_label}",
                      fontdict=None, labelpad=None, loc='top')

        ax.annotate(f'Предел огнестойкости: {round((time_fsr / 60), 1)} мин\n'
                    f'Критическая температура: {round((Tcr), 1)} \u00B0С\n'
                    f'Приведенная толщина элемента: {round((self.ptm), 3)} мм',
                    xy=(0, max(Tm)), xycoords='data', xytext=(time_fsr, max(Tm)+50), textcoords='data')

        # Легенда
        plt.legend(fontsize=12, framealpha=0.95, facecolor="w", loc=4)

        # Цветовая шкала
        # plt.colorbar()
        # Подпись горизонтальной оси абсцисс OY -> cbar.ax.set_xlabel();
        # Подпись вертикальной оси абсцисс OY -> cbar.ax.set_ylabel();

        # Деления на оси абсцисс OX
        plt.xticks(np.arange(min(x_t), max(x_t), 1000.0))

        # Деления на оси ординат OY
        plt.yticks(np.arange(0, max(Tm)+100, 100.0))

        # Вспомогательная сетка (grid)
        ax.grid(visible=True,
                which='major',
                axis='both',
                color=(0, 0, 0, 0.5),
                linestyle=':',
                linewidth=0.250)

        directory = get_temp_folder(fold_name='temp_pic')
        name_plot = "".join(['fig_steel_fr_', str(self.chat_id), '.png'])
        name_dir = '/'.join([directory, name_plot])

        fig.savefig(name_dir, format='png', transparent=True)
        plt.cla()
        plt.close(fig)

        return name_dir

    def get_data_steel_heating(self):
        table_title = [
            ["Данные прогрева незащищенной стальной контрукции"], [""], [f"Режим пожара: {self.mode}"], [f"ПТМ: {self.ptm}"], [""]]
        data_title = [["Время, с", "Тв, С", "Тст, С", ]]
        table_note = [[""], ["ПТМ - приведенная толщина метала, мм"], ["Тв - температура среды"],
                      ["Тст - температура элемента"]]

        Tm = self.get_fire_mode()
        Tst = self.get_steel_heating()

        data_profile = []
        for i in range(self.x_min, self.x_max, 1):
            data_profile.append(
                [i, Tm[i], Tst[i],])

        data = table_title + data_title + data_profile + table_note
        return data
