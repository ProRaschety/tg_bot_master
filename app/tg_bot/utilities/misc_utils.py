import logging
import re
import os
import csv
import io
import pandas as pd
import numpy as np
# import inspect
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
# from matplotlib import font_manager as fm, rcParams
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib import font_manager
from datetime import datetime
# from fluentogram import TranslatorRunner

from app.tg_bot.models.tables import DataFrameModel

# font_dirs = ['app/tg_bot/fonts']  # The path to the custom font file.
# font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
# for font_file in font_files:
#     font_manager.fontManager.addfont(font_file)

log = logging.getLogger(__name__)


def serializer(model: dict):
    pass


def deserializer(model: dict):
    pass


def compute_value_with_eval(expression: str = '0'):
    try:
        result = eval(expression)
    except ZeroDivisionError as e:
        result = 0
        log.info(f"Ошибка деления на ноль: {expression}", )
    except SyntaxError as e:
        result = 0
        log.info(f"Синтаксическая ошибка: {expression}", )
    except NameError as e:
        result = 0
        log.info(f"Ошибка имени переменной: {expression}", )
    except TypeError as e:
        result = 0
        log.info(f"Ошибка типа данных: {expression}", )
    except ValueError as e:
        result = 0
        log.info(f"Ошибка значения: {expression}", )
    return result


def check_if_string_empty(input_string: str):
    if input_string.strip() != "":
        return True
    else:
        return False


def check_string(input_string: str):
    # Паттерн для проверки: строка содержит только цифры и/или одну точку
    # pattern = r'^[\d.]+$'
    # pattern = r'^[0-9.]+$'
    pattern = r'^[0-9]*\.?[0-9]*$'
    # Проверка с использованием регулярного выражения
    if re.match(pattern, input_string):
        return True
    else:
        return False


def count_decimal_digits(number: int | float):
    # Преобразование числа в строку
    number_str = str(number)
    # Поиск позиции десятичной точки
    decimal_point_index = number_str.find('.')
    if decimal_point_index != -1:
        # Подсчет количества значимых цифр после запятой
        count = len(number_str) - decimal_point_index - 1
        return count
    else:
        return 0  # Если нет десятичной точки, значит нет значимых цифр после запятой


def count_zeros_after_decimal(number: int | float):
    # Преобразование числа в строку
    number_str = str(number)
    # Поиск позиции десятичной точки
    decimal_point_index = number_str.find('.')
    if decimal_point_index != -1:
        # Подсчет количества нулей после запятой до первой значимой цифры
        count_zeros = 0
        for char in number_str[decimal_point_index + 1:]:
            if char == '0':
                count_zeros += 1
            else:
                break  # Прерываем цикл, если встречаем не ноль
        return count_zeros
    else:
        return 0  # Если нет десятичной точки, значит нет нулей после запятой


def count_zeros_and_digits(number: int | float):
    # Преобразование числа в строку
    number_str = str(number)
    # Поиск позиции десятичной точки
    decimal_point_index = number_str.find('.')
    if decimal_point_index != -1:
        # Подсчет количества нулей после запятой до первой значимой цифры
        count_zeros = 0
        for char in number_str[decimal_point_index + 1:]:
            if char == '0':
                count_zeros += 1
            else:
                break  # Прерываем цикл, если встречаем не ноль
        # Подсчет количества цифр до следующего нуля
        count_digits_to_next_zero = 0
        for char in number_str[decimal_point_index + count_zeros + 1:]:
            if char != '0':
                count_digits_to_next_zero += 1
            else:
                break  # Прерываем цикл, если встречаем ноль
        return count_zeros, count_digits_to_next_zero
    else:
        return 0, 0  # Если нет десятичной точки, значит нет нулей после запятой и цифр до следующего нуля


def count_digits_before_dot(number: int | float):
    input_string = str(number)
    if '.' in input_string:
        digits_before_dot = input_string.index('.')
        return digits_before_dot
    else:
        return 0


def result_formatting(input_string: str | None = None, formatting: bool = False, result: int | float = 0.0):
    if formatting:
        if input_string != None:
            if check_if_string_empty(input_string):
                editable_param = float(input_string)
            else:
                editable_param = 0
        else:
            editable_param = result

        if editable_param >= -0.0009 and editable_param <= 0.0009:
            form_param = "{:.2e}".format(editable_param)

        elif editable_param >= -0.0001 and editable_param <= 0.0001:
            form_param = "{:.5f}".format(editable_param)

        elif editable_param >= -0.001 and editable_param <= 0.001:
            form_param = "{:.4f}".format(editable_param)

        elif editable_param >= -0.01 and editable_param <= 0.01:
            form_param = "{:.3f}".format(editable_param)

        elif editable_param >= -10.0 and editable_param <= 10:
            form_param = "{:.2f}".format(editable_param)

        elif editable_param >= -100.0 and editable_param <= 100:
            form_param = "{:.1f}".format(editable_param)

        elif editable_param > -100_000 and editable_param <= 100_000:
            form_param = "{:.1f}".format(editable_param)

        else:
            form_param = "{:.2e}".format(editable_param)

        return form_param

    else:
        return input_string


def custom_round(number: int | float = 0.0):
    # count = count_decimal_digits(number=number)
    # count_digits = count_digits_before_dot(number=number)
    # count_zero, count_to_next_zero = count_zeros_and_digits(number=number)
    # # adj_result = round(number, rou_int)
    # print(f'Проверка значимых чисел после запятой: {count}')
    # print(f'Количество цифр до запятой: {count_digits}')
    # print(f'Количество 0 после запятой: {count_zero}')
    # print(f'Количество цифр после 0: {count_to_next_zero}')

    # if number >= 100000:
    #     return round(number)
    # elif number <= 0.0000000001:
    #     return round(number, 10)  # Округляем до 10 знаков после запятой
    # else:
    #     return number

    if number > -0.0001 and number < 0.0001:
        # form_param = "{:.2e}".format(number)
        rou_int = 6

    # добавлено доп условие
    elif number >= -0.0001 and number <= 0.0001:
        # form_param = "{:.5f}".format(number)
        rou_int = 6
    # добавлено доп условие
    elif number >= -0.001 and number <= 0.001:
        # form_param = "{:.4f}".format(number)
        rou_int = 5

    elif number >= -0.01 and number <= 0.01:
        # form_param = "{:.3f}".format(number)
        rou_int = 3

    # добавлено доп условие
    elif number >= -10.0 and number <= 10:
        # form_param = "{:.2f}".format(number)
        rou_int = 2

    elif number >= -100.0 and number <= 100:
        # form_param = "{:.1f}".format(number)
        rou_int = 1

    elif number > -100_000 and number <= 100_000:
        # form_param = "{:,.1f}".format(number)
        rou_int = 1

    else:
        form_param = "{:.2e}".format(number)
        rou_int = 1

    return round(number, rou_int)


def find_value_path(data: dict, target: Any, path=None):
    if path is None:
        path = []

    for key, value in data.items():
        if value == target:
            return path + [key]

        if isinstance(value, dict):
            new_path = find_value_path(value, target, path + [key])
            if new_path:
                return new_path

    return None


def find_key_by_value(data: dict, target: Any):
    for key, value in data.items():
        if value == target:
            return key
        if isinstance(value, dict):
            nested_key = find_key_by_value(value, target)
            if nested_key:
                return nested_key
    return None


def find_value_path_2d(data: list[list], target: Any, path=None):
    if path is None:
        path = []

    for i, row in enumerate(data):
        for j, value in enumerate(row):
            if value == target:
                return path + [(i, j)]

    return None


def find_value_path_nested(data: dict, target: Any, path=None):
    if path is None:
        path = []

    for key, value in data.items():
        if isinstance(value, list):
            for i, row in enumerate(value):
                for j, val in enumerate(row):
                    if val == target:
                        return path + [key, (i, j)]
        elif isinstance(value, dict):
            new_path = find_value_path_nested(value, target, path + [key])
            if new_path:
                return new_path

    return None


def get_temp_folder(dir_name='temp_files', fold_name='temp'):
    """
    Возвращает местоположение временной папки
    и создает ее при необходимости

    Parameters
    ----------
    temp_dir_name : str, optional
        Name of temporary folder (default is 'temp')

    Returns
    -------
    temp_dir_path : str
        absolute path to temporary folder
    """
    temp_dir_path = os.path.join(os.getcwd(), dir_name, fold_name)
    if not os.path.isdir(temp_dir_path):
        os.mkdir(temp_dir_path)
    return temp_dir_path


def get_csv_file(data, name_file) -> csv:
    file = str(name_file)
    try:
        with open(file, 'w', newline='') as file_w:
            csv_writer = csv.writer(
                file_w, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerows(data)

    except csv.Error:
        print(f"Ошибка в CSV-файле на строке {reader.line_num}: {csv.Error}")
    except UnicodeDecodeError:
        print("Ошибка декодирования. Возможно, файл имеет другую кодировку.")
    except FileNotFoundError:
        print("Файл не найден.")
    except IOError:
        print(f"Ошибка ввода-вывода при работе с файлом. {IOError}")
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")


def get_csv_bt_file(data) -> bytes:
    output = io.StringIO()
    with output as file_w:
        writer = csv.writer(file_w, dialect='excel', delimiter=';',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(data)
        byte_file = output.getvalue().encode("ANSI")
    return byte_file


def get_xlsx_bt_file(data) -> bytes:
    writer = pd.ExcelWriter('simple-report.xlsx', engine='xlsxwriter')
    df.to_excel(writer, index=False)
    df_footer.to_excel(writer, startrow=6, index=False)
    writer.save()
    output = io.StringIO()
    with output as file_w:
        writer = csv.writer(file_w, dialect='excel', delimiter=';',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(data)
        byte_file = output.getvalue().encode("ANSI")
    return byte_file


def get_picture_filling(file_path) -> bytes:
    buffer = io.BytesIO()
    file = file_path
    with open(file, 'rb') as f:
        file_r = f.read()
        byte_pic = buffer.write(file_r)
    buffer.seek(0)
    byte_pic = buffer.getvalue()
    buffer.close()
    return byte_pic


def get_dict(list_: list) -> dict:
    first, *rest = list_
    return {first: get_dict(rest)} if rest else first


def get_dataframe_table(data: DataFrameModel, std_table: bool = True, results: bool | None = False, row_num: int | None = None, row_num_patch: int | None = None, sel_row_num: int = 0) -> bytes:
    log.info(f'Requst dataframe table: {data.label}')

    """Рисует таблицу по данным полученным из функции get_dataframe()"""

    font_dirs = ['app/tg_bot/fonts']  # The path to the custom font file.
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)
    # px = 96.358115  # 1 дюйм = 2.54 см = 96.358115 pixel
    cols = len(list(data.dataframe[-1]))
    rows = len(data.dataframe)

    color = {
        'violet': (0.19367589, 0.20948617, 0.43478261, 0.80),  # 49,53,110
        'white': (1.00, 1.00, 1.00, 1.00),  #
        'rich_black': (1/253, 11/253, 19/253, 0.80),  # 1,11,19
        'total_black': (0.0, 0.0, 0.0, 1.0),
        'orange': (0.913, 0.380, 0.082, 0.80),  # 49,53,110
        'yellow': (0.9372, 0.9098, 0.8353, 1.00),
        'grey': (229/253, 228/253, 226/253, 1.00),  # 247,247,247
        'light_green': (238/253, 244/253, 232/253, 1.00),  # 238,244,232
        'brown_sugar': (95/253, 96/253, 92/253, 1.00),  # 95,96,92
        'anitracite_gray': (15/253, 18/253, 19/253, 0.95)  # 15, 18, 19
    }  # (0.4941, 0.5686, 0.5843, 1.0) ранее были окрашены заголовки в этот цвет https://get-color.ru/grey/

    """"Параметры фигуры"""
    if cols == 4:
        if rows < 10:
            log.info(f'Таблица_4/9: cols={cols}, rows={rows}')
            w_fig, h_fig, dpi = 13.0, 13.0, 100  # 12.8, 12.8
            w_size, h_size = cols * dpi, rows * dpi
            font_size_title = 22
            font_size_header = 20
            font_size_text = 22
            lw_line = 3
            logo_size = 17
            x_st = 4.0
            hspace = 0.105
            zoom = 0.085
        elif rows < 15:
            log.info(f'Таблица_4/14: cols={cols}, rows={rows}')
            w_fig, h_fig, dpi = 15.0, 15.0, 100  # 12.8, 12.8
            w_size, h_size = cols * dpi, rows * dpi
            font_size_title = 25
            font_size_header = 23
            font_size_text = 25
            lw_line = 4
            logo_size = 15
            x_st = 4.5
            hspace = 0.10
            zoom = 0.095
        else:
            log.info(f'Таблица_4/n: cols={cols}, rows={rows}')
            w_fig, h_fig, dpi = 12.8, 12.8, 100  # 12.8, 12.8
            w_size, h_size = cols * dpi, rows * dpi
            font_size_title = 22
            font_size_header = 20
            font_size_text = 22
            lw_line = 3
            logo_size = 17
            x_st = 3.5
            hspace = 0.085
            zoom = 0.095
    elif cols == 9:
        if rows < 16:
            log.info(f'Таблица_9/16: cols={cols}, rows={rows}')
            w_fig, h_fig, dpi = 22, 14, 100  # 12.8, 12.8
            w_size, h_size = cols * dpi, rows * dpi
            font_size_title = 22
            font_size_header = 18
            font_size_text = 20
            lw_line = 4
            logo_size = 17
            x_st = 2.0
            hspace = 0.125
            zoom = 0.095
        else:
            log.info(f'Таблица_9/n: cols={cols}, rows={rows}')
            w_fig, h_fig, dpi = 22, 14, 100  # 12.8, 12.8
            w_size, h_size = cols * dpi, rows * dpi
            font_size_title = 22
            font_size_header = 18
            font_size_text = 20
            lw_line = 4
            logo_size = 17
            x_st = 2.0
            hspace = 0.085
            zoom = 0.095
    elif cols > 9:
        if rows < 16:
            log.info(f'Таблица_11/16: cols={cols}, rows={rows}')
            w_fig, h_fig, dpi = 22, 14, 100  # 12.8, 12.8
            w_size, h_size = cols * dpi, rows * dpi
            font_size_title = 22
            font_size_header = 18
            font_size_text = 20
            lw_line = 4
            logo_size = 17
            x_st = 2.0
            hspace = 0.125
            zoom = 0.095
        else:
            log.info(f'Таблица_11/n: cols={cols}, rows={rows}')
            w_fig, h_fig, dpi = 26, 14, 100  # 12.8, 12.8
            w_size, h_size = cols * dpi, rows * dpi
            font_size_title = 22
            font_size_header = 18
            font_size_text = 22
            lw_line = 4
            logo_size = 17
            x_st = 2.0
            hspace = 0.085
            zoom = 0.095

    left = 0.025
    bottom = 0.020
    right = 1.0 - left
    top = 0.945  # 1.0 - bottom
    margins = {
        "left": left,  # 0.030
        "bottom": bottom,  # 0.030
        "right": right,  # 0.970
        "top": top,  # 0.900
        "hspace": hspace  # 0.200
    }
    fig = plt.figure(figsize=(w_fig, h_fig), dpi=dpi,
                     facecolor=color['white'], clear=False, constrained_layout=False, frameon=False)
    fig.subplots_adjust(**margins)
    # plt.style.use('bmh')
    # plt.style.use('Solarize_Light2')
    width_ratios = [1]
    height_ratios = [0.10, h_fig]
    gs = gridspec.GridSpec(
        nrows=2, ncols=1, width_ratios=width_ratios, height_ratios=height_ratios)

    """Первая часть таблицы"""
    w_fig_ax_1, h_fig_ax_1 = 1, height_ratios[0]
    # 'baseline', 'bottom', 'center', 'center_baseline', 'top'
    # fontstyle {'normal', 'italic', 'oblique'}; толщина рифта: 0-1000 или 'light', 'normal', 'regular', 'book', 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy', 'extra bold', 'black'
    font_st_ttl = {'fontname': 'Acrobat', 'fontsize': font_size_title}
    fig_ax_1 = fig.add_subplot(gs[0, 0])
    fig_ax_1.set_facecolor(color=color['total_black'])
    fig_ax_1.axis('off')
    logo = plt.imread('temp_files/temp/logo.png')
    fig_ax_1.set_xlim(0.0, w_fig_ax_1)
    fig_ax_1.set_ylim(0.0, h_fig_ax_1)
    fig_ax_1.text(x=0.0, y=h_fig_ax_1, s=data.label, weight='normal', ha='left', va='baseline',
                  c=color['anitracite_gray'], fontstyle='oblique', **font_st_ttl
                  )
    fig_ax_1.plot([0, w_fig_ax_1], [0.0, 0.0],
                  lw=lw_line * 1.4, c=color['orange'])
    imagebox = OffsetImage(logo,
                           zoom=zoom,
                           dpi_cor=True, resample=False, filternorm=False)
    fig_ax_1.add_artist(AnnotationBbox(
        imagebox, (1.0, h_fig_ax_1), frameon=False, pad=0, box_alignment=(1.0, 0.0)))

    """Вторая часть таблицы"""
    w_fig_ax_2, h_fig_ax_2 = cols + w_fig/5, rows/2  # + 0.125
    font_nd_ttl = {'fontname': 'Acrobat', 'fontsize': font_size_header}
    font_nd = {'fontname': 'Roboto', 'fontsize': font_size_text}
    fig_ax_2 = fig.add_subplot(gs[1, 0])
    fig_ax_2.set_facecolor(color=color['white'])
    fig_ax_2.axis('off')
    fig_ax_2.set_xticks(np.arange(0, w_fig_ax_2, 0.50), minor=False)
    fig_ax_2.set_yticks(np.arange(0, h_fig_ax_2, 0.50), minor=False)
    step = 0.5
    fig_ax_2.set_xlim(0.0, w_fig_ax_2)
    fig_ax_2.set_ylim(0.0, h_fig_ax_2)
    n = cols - 2
    m = w_fig_ax_2 - (x_st + w_fig_ax_2 * 0.00)
    y_title = (rows / 2 + 0.05)
    m_per_n = m / n
    if std_table:
        fig_ax_2.add_patch(patches.Rectangle((x_st + m_per_n - step, 0),  # нижняя левая начальная позиция (x, y)
                                             width=1, height=rows/2, ec='none', color=color['yellow'], alpha=1.0, zorder=-1))
    df = data.dataframe[::-1]
    for row in np.arange(0, rows):
        fig_ax_2.plot([0.0, w_fig_ax_2], [row / 2 + step, row / 2 + step], ls=':', lw=lw_line *
                      0.5, c=color['anitracite_gray']) if row < rows-1 else None  # линия сетки
        y = step / 2 + row / 2 if row > 0 else step / 2
        for i in np.arange(0, cols):
            d = df[row]
            if i == 0:
                x = 0
                ha = 'left'
                wh = 'bold' if d[1] == '' else 'normal'
            elif i == 1:
                x = x_st
                ha = 'center'
                wh = 'normal'
            elif i < cols-1:
                x = x_st + m_per_n * (i - 1)
                ha = 'center'
                wh = 'bold'
            else:
                x = w_fig_ax_2
                ha = 'right'
                wh = 'bold' if d[cols - 2] == '' else 'normal'
            fig_ax_2.text(x=x, y=y_title, s=data.headers[i], weight='normal', ha=ha, va='baseline',
                          c=color['violet'], **font_nd_ttl) if row == 0 else None  # заголовки таблицы
            fig_ax_2.text(x=x, y=y, s=d[i], weight=wh, ha=ha,
                          va='center_baseline', c=color['anitracite_gray'], **font_nd)

            if d[1] == '' and d[cols - 2] == '' and std_table == False:
                fig_ax_2.add_patch(patches.Rectangle((x, row/2 if row > 0 else step/2),  # нижняя левая начальная позиция (x, y)
                                                     width=w_fig_ax_2,
                                                     height=step,
                                                     ec='none',
                                                     color=color['yellow'],
                                                     alpha=1.0,
                                                     zorder=-1))

    """Дополнительные декоративные выделения второй таблицы"""
    # основной разделитель заголовка
    fig_ax_2.plot([0, w_fig_ax_2], [rows/2-0.01, rows/2-0.01],
                  lw=lw_line, c=color['violet'])
    fig_ax_2.plot([0, w_fig_ax_2], [0.0, 0.0],
                  lw=lw_line * 2.0, c=color['violet'])
    fig_ax_2.plot([0, w_fig_ax_2], [(rows-row_num)*step, (rows-row_num)
                  * step], lw=lw_line, c=color['violet']) if results else None

    """Сохранение картинки в буфер памяти"""
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    # plt.show()
    buffer.close()
    plt.cla()
    plt.clf()
    plt.style.use('default')
    plt.close(fig)
    return image_png


def get_data_table(data: list[dict], headers: str, label: str, column: int = 4, results: bool | None = False, row_num: int | None = None, row_num_patch: int | None = None, sel_row_num: int = 0) -> bytes:
    log.info(f"Таблица данных: {label}")
    # plt.rcParams['font.family'] = 'Roboto'
    # font_dirs = r"/app/tg_bot/fonts"  # The path to the custom font file.
    # font_files = fm.findSystemFonts(fontpaths=font_dirs)
    # log.info(f"font_files: {font_files}")
    rows = len(data)
    if rows > 0:
        data = data
    else:
        data = [{'id': '-', 'var': '-', 'unit_1': '-', 'unit_2': '-'}]
    rows_keys = list(data[0].keys())
    cols = len(list(data[0]))

    px = 96.358115  # 1 дюйм = 2.54 см = 96.358115 pixel
    marg = 50
    h = rows * marg  # px 450
    W, H = (cols + (rows - cols), rows)

    left = 0.030
    bottom = 0.030
    right = 0.970
    top = 0.950
    hspace = 0.000
    margins = {
        "left": left,  # 0.030
        "bottom": bottom,  # 0.030
        "right": right,  # 0.970
        "top": top,  # 0.900
        "hspace": hspace  # 0.200
    }

    fig = plt.figure(figsize=(W, H),
                     dpi=170, constrained_layout=False)
    fig.subplots_adjust(**margins)
    # plt.style.use('Solarize_Light2')
    widths = [1]
    heights = [0.20, rows]  # 0.20, 7.8
    # heights = [xmax, xmax]
    gs = gridspec.GridSpec(
        ncols=1, nrows=2, width_ratios=widths, height_ratios=heights)

    # fpath =

    ft_label_size = {'fontname': 'Arial',
                     'fontsize': H*2.0}  # h*0.023
    ft_title_size = {'fontname': 'Arial', 'fontsize': H*1.7}  # h*0.020
    ft_size = {'fontname': 'Arial', 'fontsize': H*1.7}  # h*0.020

    """____Первая часть таблицы____"""
    fig_ax_1 = fig.add_subplot(gs[0, 0])

    logo = plt.imread('temp_files/temp/logo.png')
    # logo = image.imread('temp_files/temp/logo.png')
    x_bound_right = 0.9
    zoom = H*0.000080 * px

    fig_ax_1.axis('off')
    fig_ax_1.set_xlim(0.0, x_bound_right)
    fig_ax_1.set_ylim(-0.25, 0.25)
    fig_ax_1.text(x=0.0, y=0.0, s=label, weight='bold',
                  ha='left', **ft_label_size)
    fig_ax_1.plot([0, x_bound_right], [-0.25, -0.25],
                  lw=zoom * 50, color=(0.913, 0.380, 0.082, 1.0))
    imagebox = OffsetImage(logo, zoom=zoom,
                           dpi_cor=True, resample=False, filternorm=False)
    ab = AnnotationBbox(imagebox, (x_bound_right - zoom * 0.1, 0.0),  frameon=False,
                        pad=0, box_alignment=(x_bound_right, 0.0))
    fig_ax_1.add_artist(ab)

    """____Вторая часть таблицы____"""
    fig_ax_2 = fig.add_subplot(gs[1, 0])
    step = 0.5
    ax2_xmax = (cols + step + step) if cols == 4 else cols + step
    ax2_ymax = (rows + step * 1.5)  # if cols == 4 else rows + step
    hor_up_line = (rows + step * 1.25)  # if cols == 4 else rows - step + 0.125
    fig_ax_2.set_xlim(0.0, ax2_xmax)
    fig_ax_2.set_ylim(step, ax2_ymax + step / 2)

    # добавить заголовки столбцов на высоте y=..., чтобы уменьшить пространство до первой строки данных
    if column == 4:
        # (0.4941, 0.5686, 0.5843, 1.0)
        color_head = (0.1936, 0.2094, 0.4347, .90)
        fig_ax_2.text(x=0, y=hor_up_line, s=headers[0],
                      weight='bold', ha='left', color=color_head, **ft_title_size)
        fig_ax_2.text(x=cols-step * 2, y=hor_up_line, s=headers[1],
                      weight='bold', ha='center', color=color_head, **ft_title_size)
        fig_ax_2.text(x=cols, y=hor_up_line, s=headers[2],
                      weight='bold', ha='center', color=color_head, **ft_title_size)
        fig_ax_2.text(x=ax2_xmax, y=hor_up_line, s=headers[3],
                      weight='bold', ha='right', color=color_head, **ft_title_size)
    else:
        color_head = (0.1936, 0.2094, 0.4347, .90)
        fig_ax_2.text(x=0, y=hor_up_line, s=headers[0],
                      weight='bold', ha='left', color=color_head, **ft_title_size)
        fig_ax_2.text(x=cols - step, y=hor_up_line, s=headers[1],
                      weight='bold', ha='center', color=color_head, **ft_title_size)
        fig_ax_2.text(x=ax2_xmax, y=hor_up_line, s=headers[2],
                      weight='bold', ha='right', color=color_head, **ft_title_size)

    # линия сетки и основной разделитель заголовка
    if results:
        for row in range(1, rows + 1):
            fig_ax_2.plot([0.0, ax2_xmax], [row - step, row - step],
                          ls=':', lw=h*0.002, c='black')
        # основной разделитель заголовка
        color_head = (0.1936, 0.2094, 0.4347, .90)
        fig_ax_2.plot([0, ax2_xmax], [rows + step, rows + step],
                      lw=h*0.005, color=color_head)
        fig_ax_2.plot([0, ax2_xmax], [rows - row_num + step, rows - row_num + step],
                      lw=h*0.005,
                      color=color_head)
        fig_ax_2.plot([0, ax2_xmax], [step, step],
                      lw=h*0.010,
                      color=color_head)
    else:
        # линия сетки
        for row in range(1, rows + 1):
            fig_ax_2.plot([0.0, ax2_xmax], [row - step, row - step],
                          ls=':', lw=h*0.002, c='black')
        # основной разделитель заголовка
        color_head = (0.1936, 0.2094, 0.4347, .90)
        fig_ax_2.plot([0, ax2_xmax], [rows + step, rows + step],
                      lw=h*0.005, color=color_head)
        fig_ax_2.plot([0, ax2_xmax], [step, step], lw=h*0.010,
                      color=color_head)

    # заполнение таблицы данных
    if column == 4:

        text_weight = 'normal' if row_num_patch == None else 'bold'

        for row in range(1, rows + 1):
            d = data[row - 1]
            fig_ax_2.text(x=0, y=row, s=d.get(rows_keys[0]),
                          va='center', weight=text_weight if (row == rows and len(str(d.get(rows_keys[3]))) == 0) else 'normal', ha='left', **ft_size)
            fig_ax_2.text(x=cols - step * 2, y=row, s=d.get(rows_keys[1]), va='center',
                          ha='center', weight='bold', **ft_size)
            fig_ax_2.text(x=cols, y=row, s=d.get(rows_keys[2]) if not isinstance(d.get(rows_keys[2]), datetime) else d.get(rows_keys[2]).strftime("%Y-%m-%d"),
                          va='center', weight='bold', ha='center', **ft_size)
            fig_ax_2.text(x=ax2_xmax, y=row, s=d.get(rows_keys[3]) if not isinstance(d.get(rows_keys[2]), datetime) else d.get(rows_keys[3]).strftime("%Y-%m-%d"),
                          va='center', weight=text_weight if row == rows else 'normal', ha='right', **ft_size)
    else:
        for row in range(1, rows + 1):
            d = data[row - 1]
            fig_ax_2.text(x=0, y=row, s=d.get(rows_keys[0]),
                          va='center', ha='left', **ft_size)
            fig_ax_2.text(x=cols - step, y=row, s=d.get(rows_keys[1]), va='center',
                          ha='center', weight='bold', **ft_size)
            fig_ax_2.text(x=ax2_xmax, y=row, s=d.get(rows_keys[2]),
                          va='center', ha='right', **ft_size)

    # выделите столбец, используя прямоугольную заплатку
    if column == 4:
        rect = patches.Rectangle((cols - step, step),  # нижняя левая начальная позиция (x, y)
                                 width=0.950,
                                 height=rows if row_num_patch == None else rows - row_num_patch,
                                 #  height=ax2_ymax - step * 2 + 0.0,
                                 ec='none',
                                 color=(0.9372, 0.9098, 0.8353, 1.0),
                                 alpha=1.0,
                                 zorder=-1)
    else:
        rect = patches.Rectangle((cols - step * 2, step),  # нижняя левая начальная позиция (x, y)
                                 width=1.00,
                                 height=rows,
                                 ec='none',
                                 color=(0.9372, 0.9098, 0.8353, 1.0),
                                 alpha=1.0,
                                 zorder=-1)

    fig_ax_2.add_patch(rect)
    fig_ax_2.axis('off')

    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.cla()
    plt.style.use('default')
    plt.close(fig)

    return image_png


def get_plot_graph(label, x_values, y_values,  x_label, y_label, plot_label: str = None, ylim: int | float = None, ymin: int | float = 0.0, ylim_tick: bool = False,
                   add_annotate: bool = False, text_annotate: list[str] = None, x_ann: int | float = None, y_ann: int | float = None,
                   add_annotate_nd: bool = False, text_annotate_nd: list[str] = None, x_ann_nd: int | float = None, y_ann_nd: int | float = None,
                   add_legend: bool = False, loc_legend: int = 1,
                   add_fill_between: bool = False, param_fill: int | float = None, label_fill: str = None,
                   add_axhline: bool = False, label_axline: str = None, **kwargs):
    log.info(f"График: {label}")
    font_dirs = ['app/tg_bot/fonts']  # The path to the custom font file.
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)
    # размеры рисунка в дюймах
    px = 96.358115  # 1 дюйм = 2.54 см = 96.358115 pixel
    w = 650  # px
    h = 650  # px
    bottom = 0.090
    right = 0.970
    left = 0.110 if ylim == None else 0.115  # 0.100
    top = 0.900 if ylim == None else 0.890
    hspace = 0.100
    xmax = 4.0
    margins = {
        "left": left,  # 0.030
        "bottom": bottom,  # 0.030
        "right": right,  # 0.970
        "top": top,  # 0.900
        "hspace": hspace  # 0.200
    }

    color = {
        'red': (0.9, 0.1, 0.0, 0.90),
        'violet': (0.19367589, 0.20948617, 0.43478261, 0.80),  # 49,53,110
        'white': (1.00, 1.00, 1.00, 1.00),  #
        'rich_black': (1/253, 11/253, 19/253, 0.80),  # 1,11,19
        'total_black': (0.0, 0.0, 0.0, 1.0),
        'orange': (0.913, 0.380, 0.082, 0.80),  # 49,53,110
        'yellow': (0.9372, 0.9098, 0.8353, 1.00),
        'grey': (229/253, 228/253, 226/253, 1.00),  # 247,247,247
        'light_green': (238/253, 244/253, 232/253, 1.00),  # 238,244,232
        'brown_sugar': (95/253, 96/253, 92/253, 1.00),  # 95,96,92
        'anitracite_gray': (15/253, 18/253, 19/253, 0.90)  # 15, 18, 19
    }  # (0.4941, 0.5686, 0.5843, 1.0) ранее были окрашены заголовки в этот цвет https://get-color.ru/grey/

    fig = plt.figure(figsize=(w / px, h / px),
                     dpi=300, constrained_layout=False)
    fig.subplots_adjust(**margins)
    # plt.style.use('bmh')
    plt.style.use('Solarize_Light2')
    widths = [1.0]
    heights = [xmax]
    gs = gridspec.GridSpec(
        ncols=1, nrows=1, width_ratios=widths, height_ratios=heights)
    ft_label_size = {'fontname': 'Acrobat', 'fontsize': w*0.018}
    # ft_title_size = {'fontname': 'Arial', 'fontsize': 8}
    ft_size = {'fontname': 'Roboto', 'fontsize': 12}
    logo = plt.imread('temp_files/temp/logo.png')

    """____Первая часть таблицы____"""
    # [left, bottom, width, height]
    fig_ax_1 = fig.add_axes(
        [0.03, 0.0, 1.0, 1.86], frameon=True, aspect=1.0, xlim=(0.0, xmax+0.25))
    fig_ax_1.axis('off')

    fig_ax_1.text(x=0.0, y=0.025, s=label,
                  weight='normal', ha='left', va='baseline', c=color['anitracite_gray'], fontstyle='oblique', **ft_label_size)
    fig_ax_1.plot([0, xmax], [0.0, 0.0], lw='1.0', c=color['orange'])
    imagebox = OffsetImage(logo, zoom=w*0.000085, dpi_cor=True)
    # ab = AnnotationBbox(imagebox, (xmax-(xmax/33.3), 0.025),
    #                     frameon=False, pad=0, box_alignment=(0.00, 0.0))
    fig_ax_1.add_artist(AnnotationBbox(imagebox, (xmax-(xmax/33.3), 0.025),
                        frameon=False, pad=0, box_alignment=(0.00, 0.0)))

    """____Вторая часть таблицы____"""
    fig_ax_2 = fig.add_subplot(gs[0, 0])
    # log.info(plot_label)
    fig_ax_2.plot(x_values, y_values, '-',
                  #   linewidth=3,
                  color=color['red'],
                  label=plot_label if plot_label != None else label,
                  **kwargs)

    # fig_ax_2.plot(abscissa, plot_second, '-', linewidth=3,
    #               label=text_legend_second, color=(0, 0, 0, 0.9))
    # fig_ax_2.hlines(y=Tcr, xmin=0, xmax=time_fsr*0.96, linestyle='--',
    #                 linewidth=1, color=(0.1, 0.1, 0, 1.0))
    # fig_ax_2.vlines(x=time_fsr, ymin=0, ymax=Tcr*0.98, linestyle='--',
    #                 linewidth=1, color=(0.1, 0.1, 0, 1.0))
    # fig_ax_2.scatter(time_fsr, Tcr, s=90, marker='o',
    #                  color=(0.9, 0.1, 0, 1))

    # Ось абсцисс Xaxis
    fig_ax_2.set_xlim(0.0, max(x_values) + max(x_values)*0.05)
    fig_ax_2.set_xlabel(xlabel=x_label, fontdict=None,
                        labelpad=None, weight='bold', loc='center', color=color['anitracite_gray'], **ft_size)

    # Ось ординат Yaxis
    if ylim == None:
        fig_ax_2.set_ylim(ymin, max(y_values) + max(y_values)*0.01)
    else:
        fig_ax_2.set_ylim(ymin, ylim)
        fig_ax_2.ticklabel_format(
            axis='y', style='sci', scilimits=(0, 2), useOffset=True)
    if ylim_tick:
        fig_ax_2.set_yticks(np.arange(
            0, max(y_values) + 0.1, 0.10), minor=False)
        fig_ax_2.ticklabel_format(
            axis='y', style='plain', scilimits=(0, 2), useOffset=True)

    fig_ax_2.set_ylabel(ylabel=y_label,
                        fontdict=None, labelpad=None, weight='bold', loc='center', color=color['anitracite_gray'], **ft_size)

    if add_annotate:
        fig_ax_2.annotate(text_annotate,
                          xy=(0, max(y_values) + max(y_values)
                              * 0.01 if ylim == None else ylim),
                          xytext=(x_ann + (x_ann / 50) if x_ann else 0.05,
                                  y_ann + (y_ann / 50) if y_ann else (min(y_values) + 0.01)),
                          xycoords='data', textcoords='data', weight='bold', **ft_size)
        if y_ann:
            fig_ax_2.hlines(y=y_ann, xmin=0, xmax=x_ann*0.99, linestyle='--',
                            linewidth=1, color=color['anitracite_gray'],)
        if x_ann:
            fig_ax_2.vlines(x=x_ann, ymin=0, ymax=y_ann*0.99, linestyle='--',
                            linewidth=1, color=color['anitracite_gray'],)
        if y_ann and x_ann:
            fig_ax_2.scatter(x_ann, y_ann, s=90, marker='o',
                             color=color['red'],)

    if add_annotate_nd:
        fig_ax_2.annotate(text_annotate_nd,
                          xy=(0, max(y_values) + max(y_values)
                              * 0.01 if ylim == None else ylim),
                          xytext=(x_ann_nd + (x_ann_nd / 50) if x_ann_nd else 0.05,
                                  y_ann_nd + (y_ann_nd / 50) if y_ann_nd else (min(y_values) + 0.01)),
                          xycoords='data', textcoords='data', weight='bold', **ft_size)
        if y_ann_nd:
            fig_ax_2.hlines(y=y_ann_nd, xmin=0, xmax=x_ann_nd*0.99, linestyle='--',
                            linewidth=1, c=color['anitracite_gray'])
        if x_ann_nd:
            fig_ax_2.vlines(x=x_ann_nd, ymin=0, ymax=y_ann_nd*0.99, linestyle='--',
                            linewidth=1, c=color['anitracite_gray'])
        if y_ann_nd and x_ann_nd:
            fig_ax_2.scatter(x_ann_nd, y_ann_nd, s=90, marker='o',
                             c=color['red'])

    if add_axhline:
        fig_ax_2.axhline(param_fill,
                         c=color['red'], linestyle="--", lw=1, label=f'{label_axline} ≥ {param_fill} м²/м²')

    if add_fill_between:
        fig_ax_2.fill_between(x_values,
                              y_values,
                              param_fill,
                              where=[d > param_fill for d in y_values],
                              c=color['red'], alpha=0.25, label=label_fill)

    # Цветовая шкала
    # plt.colorbar()
    # Подпись горизонтальной оси абсцисс OY -> cbar.ax.set_xlabel();
    # Подпись вертикальной оси абсцисс OY -> cbar.ax.set_ylabel();

    # Деления на оси абсцисс OX
    # fig_ax_2.set_xticks(np.arange(min(x_t), max(x_t), 1000.0), minor=False)

    # Деления на оси ординат OY
    # fig_ax_2.set_yticks(np.arange(0, max(Tm)+100, 100.0), minor=False)

    # Вспомогательная сетка (grid)
    fig_ax_2.grid(visible=True,
                  which='major',
                  axis='both',
                  c=color['anitracite_gray'],
                  linestyle=':',
                  linewidth=0.250)

    if add_legend:
        fig_ax_2.legend(fontsize=10, framealpha=0.95,
                        facecolor=color['white'], loc=loc_legend)
    # directory = get_temp_folder(fold_name='temp_pic')
    # name_plot = "".join(['fig_steel_fr_', str(self.chat_id), '.png'])
    # name_dir = '/'.join([directory, name_plot])
    # fig.savefig(name_dir, format='png', transparent=True)
    # plt.cla()
    # plt.close(fig)
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    plot = buffer.getvalue()
    buffer.close()
    plt.cla()
    plt.style.use('default')
    plt.close(fig)

    return plot


def get_init_data_table(data, headers: str, label: str, column: int = 4, results: bool | None = False, row_num: int | None = None, sel_row_num: int = 0) -> bytes:
    log.info("Таблица исходных данных")
    rows = len(data)
    if rows > 0:
        data = data
    else:
        data = [{'id': '-', 'var': '-', 'unit_1': '-', 'unit_2': '-'}]
    rows_keys = list(data[0].keys())
    cols = len(list(data[0]))

    px = 96.358115  # 1 дюйм = 2.54 см = 96.358115 pixel
    marg = 50
    h = rows * marg  # px 450
    W, H = (cols + (rows - cols), rows)
    left = 0.030
    bottom = 0.030
    right = 0.970
    top = 0.950
    hspace = 0.000
    margins = {
        "left": left,  # 0.030
        "bottom": bottom,  # 0.030
        "right": right,  # 0.970
        "top": top,  # 0.900
        "hspace": hspace  # 0.200
    }

    fig = plt.figure(figsize=(W, H),
                     dpi=150, constrained_layout=False)
    fig.subplots_adjust(**margins)

    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.cla()
    plt.style.use('default')
    plt.close(fig)
    return image_png

# def get_plot_graph(data, add_annotate: bool = False, add_legend: bool = False, add_colorbar: bool = False, **kwargs) -> bytes:
#     log.info("График данных")
#     # размеры рисунка в дюймах
#     px = 96.358115  # 1 дюйм = 2.54 см = 96.358115 pixel
#     w = 700  # px
#     h = 700  # px
#     left = 0.130
#     bottom = 0.100
#     right = 0.970
#     top = 0.900
#     hspace = 0.100
#     xmax = 4.0
#     margins = {
#         "left": left,  # 0.030
#         "bottom": bottom,  # 0.030
#         "right": right,  # 0.970
#         "top": top,  # 0.900
#         "hspace": hspace  # 0.200
#     }
#     fig = plt.figure(figsize=(w / px, h / px),
#                      dpi=300, constrained_layout=False)
#     fig.subplots_adjust(**margins)
#     # plt.style.use('bmh')
#     plt.style.use('Solarize_Light2')
#     widths = [1.0]
#     heights = [xmax]
#     gs = gridspec.GridSpec(
#         ncols=1, nrows=1, width_ratios=widths, height_ratios=heights)
#     ft_label_size = {'fontname': 'Arial', 'fontsize': w*0.021}
#     # ft_title_size = {'fontname': 'Arial', 'fontsize': 8}
#     ft_size = {'fontname': 'Arial', 'fontsize': 12}
#     logo = plt.imread('temp_files/temp/logo.png')
#     # [left, bottom, width, height]
#     fig_ax_1 = fig.add_axes(
#         [0.03, 0.0, 1.0, 1.86], frameon=True, aspect=1.0, xlim=(0.0, xmax+0.25))
#     fig_ax_1.axis('off')
#     fig_ax_1.text(x=0.0, y=0.025, s='Прогрев элемента конструкции',
#                   weight='bold', ha='left', **ft_label_size)
#     fig_ax_1.plot([0, xmax], [0.0, 0.0], lw='1.0',
#                   color=(0.913, 0.380, 0.082, 1.0))
#     imagebox = OffsetImage(logo, zoom=w*0.000085, dpi_cor=True)
#     ab = AnnotationBbox(imagebox, (xmax-(xmax/33.3), 0.025),
#                         frameon=False, pad=0, box_alignment=(0.00, 0.0))
#     fig_ax_1.add_artist(ab)

#     fig_ax_2 = fig.add_subplot(gs[0, 0])

#     # fig_ax_2.set_xlim(0.0, cols+0.5)
#     # fig_ax_2.set_ylim(-.75, rows+0.55)

#     # title_plot = 'График прогрева стального элемента'
#     # fig_ax_2.set_title(f'{title_plot}\n', fontsize=18,
#     #                    alpha=1.0, clip_on=False, y=1.0)
#     if mode == 'Углеводородный':
#         rl = "Углеводородный режим"
#     elif mode == 'Наружный':
#         rl = "Наружный режим"
#     elif mode == 'Тлеющий':
#         rl = "Тлеющий режим"
#     else:
#         rl = "Стандартный режим"
#     label_plot_Tst = f'Температура элемента'
#     Tm = get_fire_mode()
#     Tst = get_steel_heating()
#     Tcr = t_critic
#     time_fsr = get_steel_fsr() * 60

#     x_max = x_max
#     if t_critic > 750.0 or mode == 'Тлеющий':
#         x_max = 150 * 60

#     tt = range(0, x_max, 1)
#     x_t = []
#     for i in tt:
#         x_t.append(i)

#     fig_ax_2.plot(x_t, Tm, '-', linewidth=3,
#                   label=f'{rl}', color=(0.9, 0.1, 0, 0.9))
#     fig_ax_2.plot(x_t, Tst, '-', linewidth=3,
#                   label=label_plot_Tst, color=(0, 0, 0, 0.9))
#     fig_ax_2.hlines(y=Tcr, xmin=0, xmax=time_fsr*0.96,
#                     linestyle='--', linewidth=1, color=(0.1, 0.1, 0, 1.0))
#     fig_ax_2.vlines(x=time_fsr, ymin=0, ymax=Tcr*0.98, linestyle='--',
#                     linewidth=1, color=(0.1, 0.1, 0, 1.0))
#     fig_ax_2.scatter(time_fsr, Tcr, s=90, marker='o',
#                      color=(0.9, 0.1, 0, 1))
#     # Ось абсцисс Xaxis
#     fig_ax_2.set_xlim(-100.0, x_max+100)
#     fig_ax_2.set_xlabel(xlabel=r"Время, с", fontdict=None,
#                         labelpad=None, weight='bold', loc='center', **ft_size)
#     # Ось абсцисс Yaxis
#     fig_ax_2.set_ylim(0, max(Tm) + 200)
#     set_y_label = str(f'Температура, \u00B0С')
#     fig_ax_2.set_ylabel(ylabel=f"{set_y_label}",
#                         fontdict=None, labelpad=None, weight='bold', loc='top', **ft_size)
#     if add_annotate:
#         fig_ax_2.annotate(f"Предел огнестойкости: {(time_fsr / 60):.2f} мин\n"
#                           f"Критическая температура: {Tcr:.2f} \u00B0С\n"
#                           f"Приведенная толщина элемента: {ptm:.2f} мм",
#                           xy=(0, max(Tm)), xycoords='data', xytext=(time_fsr, max(Tm)+50), textcoords='data', weight='bold', **ft_size)

#     if add_legend:
#         fig_ax_2.legend(fontsize=12, framealpha=0.95, facecolor="w", loc=4)

#     if add_colorbar:
#         plt.colorbar()
#         # Подпись горизонтальной оси абсцисс OY -> cbar.ax.set_xlabel();
#         # Подпись вертикальной оси абсцисс OY -> cbar.ax.set_ylabel();

#     # Деления на оси абсцисс OX
#     fig_ax_2.set_xticks(np.arange(min(x_t), max(x_t), 1000.0), minor=False)

#     # Деления на оси ординат OY
#     fig_ax_2.set_yticks(np.arange(0, max(Tm)+100, 100.0), minor=False)

#     # Вспомогательная сетка (grid)
#     fig_ax_2.grid(visible=True,
#                   which='major',
#                   axis='both',
#                   color=(0, 0, 0, 0.5),
#                   linestyle=':',
#                   linewidth=0.250)

#     # directory = get_temp_folder(fold_name='temp_pic')
#     # name_plot = "".join(['fig_steel_fr_', str(self.chat_id), '.png'])
#     # name_dir = '/'.join([directory, name_plot])
#     # fig.savefig(name_dir, format='png', transparent=True)
#     # plt.cla()
#     # plt.close(fig)
#     buffer = io.BytesIO()
#     fig.savefig(buffer, format='png')
#     buffer.seek(0)
#     plot = buffer.getvalue()
#     buffer.close()
#     plt.cla()
#     plt.style.use('default')
#     plt.close(fig)

#     return plot
