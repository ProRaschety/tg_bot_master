import logging

import io
import json
import pandas as pd
import numpy as np
import six
import matplotlib

import math as m
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from scipy.interpolate import interp1d

# Что нужно получить ? <- заголовок таблицы,
# кол-во строк таблицы, данные для заполнения строк,
# кол-во столбцов, заголовки столбцов,
label = "Исходные данные\nдля прочностного расчета"
label_data = {'label_1': 'Параметр',
              'label_2': 'Значение',
              'label_3': 'Ед.изм'}
data = [
    {'id': 'Способ закрепления', 'var': 'fixation', 'unit': '-', 'unit2': '32'},
    {'id': 'Усилие', 'var': 'type_loading', 'unit': '-', 'unit2': '55'},]

# data = [
#     {'id': 'Способ закрепления', 'var': 'fixation', 'unit': '-'},
#     {'id': 'Усилие', 'var': 'type_loading', 'unit': '-'},
#     {'id': 'Тип нагружения', 'var': 'loading_method', 'unit': '-'},
#     {'id': 'Нагрузка', 'var': 'n_load * 9.807', 'unit': 'unit_load'},
#     {'id': 'Длина пролета', 'var': 'self.len_elem', 'unit': 'мм'},
#     {'id': 'Приведенная толщина\nметалла', 'var': 'ptm', 'unit': 'мм'},
#     {'id': 'Количество сторон обогрева',
#         'var': 'self.num_sides_heated', 'unit': 'шт'},
#     {'id': 'Тип стали', 'var': 'self.type_steel_element', 'unit': '-'},
#     {'id': 'Сечение', 'var': 'self.name_profile', 'unit': '-'},
#     {'id': 'Сортамент', 'var': 'self.sketch', 'unit': '-'},
#     {'id': 'Профиль по ГОСТ', 'var': 'self.reg_document', 'unit': '-'}]


def get_init_data_table(data: list, label_data: dict, label: str):
    rows = len(data)
    cols = len(list(data[0]))
    print(f'Кол-во строк: {rows}')
    print(f'Кол-во столбцов: {cols}')
    rows_table = rows
    colomns_table = cols

    if cols == 2:
        name_col_firsth = list(data[0].keys())[0]
        name_col_second = list(data[0].keys())[1]
    elif cols == 3:
        name_col_firsth = list(data[0].keys())[0]
        name_col_second = list(data[0].keys())[1]
        name_col_third = list(data[0].keys())[2]
    elif cols == 4:
        name_col_firsth = list(data[0].keys())[0]
        name_col_second = list(data[0].keys())[1]
        name_col_third = list(data[0].keys())[2]
        name_col_fourth = list(data[0].keys())[3]

    table_header_firsth = label_data.get('label_1', 'Unknown')
    table_header_second = label_data.get('label_2', 'Unknown')
    table_header_third = label_data.get('label_3', 'Unknown')
    table_header_fourth = label_data.get('label_4', 'Unknown')

    # data = []
    # for row in range(1, rows_table):
    #     if colomns_table == 2:
    #         data.append({f'{name_col_firsth}': row,
    #                      f'{name_col_second}': row, })
    #     elif colomns_table == 3:
    #         data.append({f'{name_col_firsth}': row,
    #                      f'{name_col_second}': row, f'{name_col_third}': row})
    #     elif colomns_table == 4:
    #         data.append({f'{name_col_firsth}': row, f'{name_col_second}': row,
    #                      f'{name_col_third}': row, f'{name_col_fourth}': row})

    # размеры рисунка в дюймах
    # 1 дюйм = 2.54 см = 96.358115 pixel
    px = 96.358115
    # w = 500  # px 500
    # h = 500  # px 500
    w = colomns_table * 150  # px 500 =3*200=600, 2*200=400
    h = rows_table * 50  # px 500

    margins = {
        "left": 0.090,  # 0.030
        "bottom": 0.070,  # 0.030
        "right": 0.970,  # 0.970
        "top": 0.900,  # 0.900
        "wspace": 0.2,  # 0.200
        "hspace": 0.2,  # 0.200
    }

    fig = plt.figure(figsize=(w / px, h / px), dpi=300)
    fig.subplots_adjust(**margins)
    ax = fig.add_subplot()

    ax.set_xlim(0.0, colomns_table)
    ax.set_ylim(-.75, rows_table+0.25)

    # добавить заголовки столбцов на высоте y=..., чтобы уменьшить пространство до первой строки данных
    ft_title_size = {'fontname': 'Arial', 'fontsize': 10}
    hor_up_line = rows_table-0.35  # - ось строки заголовка
    if colomns_table == 2:
        ax.text(x=colomns_table-2, y=hor_up_line, s=table_header_firsth,
                weight='bold', ha='left', **ft_title_size)
        ax.text(x=colomns_table, y=hor_up_line, s=table_header_second,
                weight='bold', ha='right', **ft_title_size)
    elif colomns_table == 3:
        ax.text(x=colomns_table-3, y=hor_up_line, s=table_header_firsth,
                weight='bold', ha='left', **ft_title_size)
        ax.text(x=colomns_table-1.0, y=hor_up_line, s=table_header_second,
                weight='bold', ha='center', **ft_title_size)
        ax.text(x=colomns_table, y=hor_up_line, s=table_header_third,
                weight='bold', ha='right', **ft_title_size)
    elif colomns_table == 4:
        ax.text(x=colomns_table-4, y=hor_up_line, s=table_header_firsth,
                weight='bold', ha='left', **ft_title_size)
        ax.text(x=colomns_table-1.0, y=hor_up_line, s=table_header_second,
                weight='bold', ha='center', **ft_title_size)
        ax.text(x=colomns_table, y=hor_up_line, s=table_header_third,
                weight='bold', ha='center', **ft_title_size)
        ax.text(x=colomns_table+1.0, y=hor_up_line, s=table_header_fourth,
                weight='bold', ha='right', **ft_title_size)
    # добавить основной разделитель заголовка (жирная линия)
    ax.plot([0, colomns_table + 1.0], [rows-0.5, rows-0.5], lw='2', c='black')
    # ax.plot([0, cols + .5], [- 0.5, - 0.5], lw='2', c='black')
    # линия сетки
    for row in range(rows):
        ax.plot([0, colomns_table + 1.0], [row - 0.5, row - 0.5],
                ls=':', lw='.5', c='grey')
    # заполнение таблицы данных
    ft_size = {'fontname': 'Arial', 'fontsize': 10}
    for row in range(rows):
        if colomns_table == 2:
            ax.text(x=colomns_table-2, y=row, s=data[row][name_col_firsth],
                    va='center', ha='left', **ft_size)
            ax.text(x=colomns_table, y=row, s=data[row][name_col_second], va='center',
                    ha='center', weight='bold', **ft_size)
        elif colomns_table == 3:
            ax.text(x=colomns_table-3, y=row, s=data[row][name_col_firsth],
                    va='center', ha='left', **ft_size)
            ax.text(x=colomns_table-1.0, y=row, s=data[row][name_col_second], va='center',
                    ha='center', weight='bold', **ft_size)
            ax.text(x=colomns_table, y=row, s=data[row][name_col_third],
                    va='center', ha='right', **ft_size)
        elif colomns_table == 4:
            ax.text(x=colomns_table-4, y=row, s=data[row][name_col_firsth],
                    va='center', ha='left', **ft_size)
            ax.text(x=colomns_table-1.0, y=row, s=data[row][name_col_second], va='center',
                    ha='center', weight='bold', **ft_size)
            ax.text(x=colomns_table, y=row, s=data[row][name_col_third],
                    va='center', ha='right', **ft_size)
            ax.text(x=colomns_table+1.0, y=row, s=data[row][name_col_fourth],
                    va='center', ha='right', **ft_size)

    # выделите столбец, используя прямоугольную заплатку
    patches_column = 2
    rect = None
    if patches_column == 1:
        rect = patches.Rectangle((0.0, -0.5),  # нижняя левая начальная позиция (x,y)
                                 width=2,
                                 height=hor_up_line+1.0,
                                 ec='none',
                                 fc='grey',
                                 alpha=.2,
                                 zorder=-1)
    elif patches_column == 2:
        rect = patches.Rectangle((colomns_table-0.5, -0.5),  # нижняя левая начальная позиция (x,y)
                                 width=1,
                                 height=hor_up_line+1.0,
                                 ec='none',
                                 fc='grey',
                                 alpha=.2,
                                 zorder=-1)
    elif patches_column == 3:
        rect = patches.Rectangle((colomns_table-0.5, -0.5),  # нижняя левая начальная позиция (x,y)
                                 width=1,
                                 height=hor_up_line+1.0,
                                 ec='none',
                                 fc='grey',
                                 alpha=.2,
                                 zorder=-1)
    ax.add_patch(rect)

    ax.set_title(label=label,
                 loc='left', fontsize=12, weight='bold')
    ax.axis('on')

    plt.show()

    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.cla()
    plt.close(fig)
    return image_png


pic = get_init_data_table(data=data,
                          label_data=label_data,
                          label=label)
# Что нужно вернуть ? -> таблицу в виде картинки в формате байтов в буфере пмяти
