import logging

import os
import csv
import io
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

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


def get_data_table(data, headers: str, label: str, results: bool | None = False, row_num: int | None = None) -> bytes:
    rows = len(data)
    cols = len(list(data[0]))
    # log.info(f'rows:{rows}, cols:{cols}')
    px = 96.358115  # 1 дюйм = 2.54 см = 96.358115 pixel
    marg = 50
    w = rows * marg + marg + (cols / 10)  # px
    h = rows * marg  # px 450
    left = 0.030
    bottom = 0.030
    right = 0.970
    top = 0.950
    hspace = 0.000
    xmin = 0.0
    ymin = 0.0
    xmax = 4.0
    ymax = 0.5
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
    # plt.style.use('Solarize_Light2')
    widths = [1]
    heights = [0.20, 7.8]
    # heights = [xmax, xmax]
    gs = gridspec.GridSpec(
        ncols=1, nrows=2, width_ratios=widths, height_ratios=heights)
    ft_label_size = {'fontname': 'Arial', 'fontsize': h*0.023}
    ft_title_size = {'fontname': 'Arial', 'fontsize': h*0.020}
    ft_size = {'fontname': 'Arial', 'fontsize': h*0.020}

    fig_ax_1 = fig.add_subplot(gs[0, 0])
    logo = plt.imread('temp_files/temp/logo.png')
    # logo = image.imread('temp_files/temp/logo.png')
    x_bound_right = 0.9
    step = 0.5
    # fig_ax_1.plot()

    fig_ax_1.axis('off')

    fig_ax_1.set_xlim(0.0, x_bound_right)
    fig_ax_1.set_ylim(-0.250, 0.3)

    fig_ax_1.text(x=0.0, y=0.0, s=label, weight='bold',
                  ha='left', **ft_label_size)

    fig_ax_1.plot([0, x_bound_right], [-0.25, -0.25],
                  lw=(h*0.000080) * 50, color=(0.913, 0.380, 0.082, 1.0))

    imagebox = OffsetImage(logo, zoom=h*0.000080,
                           dpi_cor=True, resample=False, filternorm=False)

    ab = AnnotationBbox(imagebox, (x_bound_right - h*0.0000080, 0.0),  frameon=False,
                        pad=0, box_alignment=(x_bound_right, 0.0))

    fig_ax_1.add_artist(ab)

    fig_ax_2 = fig.add_subplot(gs[1, 0])
    fig_ax_2.set_xlim(0.0, cols+0.5)
    fig_ax_2.set_ylim(-.75, rows+0.55)

    # добавить заголовки столбцов на высоте y=..., чтобы уменьшить пространство до первой строки данных
    hor_up_line = rows-0.25
    if len(list(headers)) == 4:
        fig_ax_2.text(x=0, y=hor_up_line, s=headers[0],
                      weight='bold', ha='left', color=(0.4941, 0.5686, 0.5843, 1.0), **ft_title_size)
        fig_ax_2.text(x=2.5, y=hor_up_line, s=headers[1],
                      weight='bold', ha='center', color=(0.4941, 0.5686, 0.5843, 1.0), **ft_title_size)
        fig_ax_2.text(x=cols-step, y=hor_up_line, s=headers[2],
                      weight='bold', ha='center', color=(0.4941, 0.5686, 0.5843, 1.0), **ft_title_size)
        fig_ax_2.text(x=cols+step, y=hor_up_line, s=headers[3],
                      weight='bold', ha='right', color=(0.4941, 0.5686, 0.5843, 1.0), **ft_title_size)
    else:
        fig_ax_2.text(x=0, y=hor_up_line, s=headers[0],
                      weight='bold', ha='left', color=(0.4941, 0.5686, 0.5843, 1.0), **ft_title_size)
        fig_ax_2.text(x=2.5, y=hor_up_line, s=headers[1],
                      weight='bold', ha='center', color=(0.4941, 0.5686, 0.5843, 1.0), **ft_title_size)
        fig_ax_2.text(x=cols+step, y=hor_up_line, s=headers[2],
                      weight='bold', ha='right', color=(0.4941, 0.5686, 0.5843, 1.0), **ft_title_size)

    # results: bool | None = False, row_num: int | None = None

    if results:
        # линия сетки
        for row in range(1, rows):
            fig_ax_2.plot([0.0, cols+step], [row - step, row - step],
                          ls=':', lw=h*0.002, c='black')
        # добавить основной разделитель заголовка
        fig_ax_2.plot([0, cols + step], [rows-step, rows-step],
                      lw=h*0.005, color=(0.4941, 0.5686, 0.5843, 1.0))

        fig_ax_2.plot([0, cols + step], [rows - row_num + step, rows - row_num + step], lw=h*0.005,
                      color=(0.4941, 0.5686, 0.5843, 1.0))

        fig_ax_2.plot([0, cols + step], [- step, - step], lw=h*0.005,
                      color=(0.4941, 0.5686, 0.5843, 1.0))

    else:
        # линия сетки
        for row in range(1, rows):
            fig_ax_2.plot([0.0, cols+step], [row - step, row - step],
                          ls=':', lw=h*0.002, c='black')
        # добавить основной разделитель заголовка
        fig_ax_2.plot([0, cols + step], [rows-step, rows-step],
                      lw=h*0.005, color=(0.4941, 0.5686, 0.5843, 1.0))
        fig_ax_2.plot([0, cols + step], [- step, - step], lw=h*0.005,
                      color=(0.4941, 0.5686, 0.5843, 1.0))

    # # заполнение таблицы данных
    # if len(list(headers)) == 4:
    #     for row in range(rows):
    #         d = data[row]
    #         fig_ax_2.text(x=0, y=row, s=d['id'],
    #                       va='center', ha='left', **ft_size)
    #         # var column это мой «основной» столбец, поэтому текст выделен жирным шрифтом
    #         fig_ax_2.text(x=2.5, y=row, s=d['var'], va='center',
    #                       ha='center', weight='bold', **ft_size)
    #         fig_ax_2.text(x=cols-0.5, y=row, s=d['unit'],
    #                       va='center', ha='center', **ft_size)
    #         fig_ax_2.text(x=cols+0.5, y=row, s=d['EFS'],
    #                       va='center', ha='right', **ft_size)
    # else:
    #     for row in range(rows):
    #         d = data[row]
    #         fig_ax_2.text(x=0, y=row, s=d['id'],
    #                       va='center', ha='left', **ft_size)
    #         fig_ax_2.text(x=2.5, y=row, s=d['var'], va='center',
    #                       ha='center', weight='bold', **ft_size)
    #         fig_ax_2.text(x=3.5, y=row, s=d['unit'],
    #                       va='center', ha='right', **ft_size)

    # # выделите столбец, используя прямоугольную заплатку
    # rect = patches.Rectangle((2.0, -0.5),  # нижняя левая начальная позиция (x,y)
    #                          width=1,
    #                          height=hor_up_line+0.95,
    #                          ec='none',
    #                          color=(0.9372, 0.9098, 0.8353, 1.0),
    #                          alpha=1.0,
    #                          zorder=-1)
    # заполнение таблицы данных
    if len(list(headers)) == 4:
        for row in range(rows):
            d = data[row]
            fig_ax_2.text(x=0, y=row, s=d.get('id'),
                          va='center', ha='left', **ft_size)
            # var column это мой «основной» столбец, поэтому текст выделен жирным шрифтом
            fig_ax_2.text(x=2.5, y=row, s=d.get('var'), va='center',
                          ha='center', weight='bold', **ft_size)
            fig_ax_2.text(x=cols-step, y=row, s=d.get('unit_1'),
                          va='center', weight='bold', ha='center', **ft_size)
            fig_ax_2.text(x=cols+step, y=row, s=d.get('unit_2'),
                          va='center', ha='right', **ft_size)
    else:
        for row in range(rows):
            d = data[row]
            fig_ax_2.text(x=0, y=row, s=d.get('id'),
                          va='center', ha='left', **ft_size)
            fig_ax_2.text(x=2.5, y=row, s=d.get('var'), va='center',
                          ha='center', weight='bold', **ft_size)
            fig_ax_2.text(x=3.5, y=row, s=d.get('unit_1'),
                          va='center', ha='right', **ft_size)

    # выделите столбец, используя прямоугольную заплатку
    if len(list(headers)) == 4:
        rect = patches.Rectangle((3.0, -step),  # нижняя левая начальная позиция (x,y)
                                 width=1.00,
                                 height=hor_up_line+0.95,
                                 ec='none',
                                 color=(0.9372, 0.9098, 0.8353, 1.0),
                                 alpha=1.0,
                                 zorder=-1)
    else:
        rect = patches.Rectangle((2.0, -step),  # нижняя левая начальная позиция (x,y)
                                 width=1.00,
                                 height=hor_up_line+0.95,
                                 ec='none',
                                 color=(0.9372, 0.9098, 0.8353, 1.0),
                                 alpha=1.0,
                                 zorder=-1)

    fig_ax_2.add_patch(rect)
    # fig_ax_2.set_title(label=label,
    #              loc='left', fontsize=12, weight='bold')
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
