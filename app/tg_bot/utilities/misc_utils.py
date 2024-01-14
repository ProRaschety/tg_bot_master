import logging

import os
import csv
import io
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as patches

log = logging.getLogger(__name__)


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


def get_txt_file(data, name_file):
    pass


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
        buffer.write(file_r)
    buffer.seek(0)
    byte_pic = buffer.getvalue()
    buffer.close()
    return byte_pic


def get_dict(list_: list) -> dict:
    first, *rest = list_
    return {first: get_dict(rest)} if rest else first


def get_initial_data_table(data, label) -> bytes:
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

    ax.set_title(label=label,
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
