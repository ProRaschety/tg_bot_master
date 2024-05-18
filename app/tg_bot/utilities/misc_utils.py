import logging
import os
import csv
import io
import pandas as pd
import numpy as np
# import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import inspect
from datetime import datetime

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


# def get_txt_file(data, name_file):
#     pass


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


def get_data_table(data, headers: str, label: str, column: int = 4, results: bool | None = False, row_num: int | None = None, sel_row_num: int = 0) -> bytes:
    log.info("Таблица данных")
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
    # plt.style.use('Solarize_Light2')
    widths = [1]
    heights = [0.20, rows]  # 0.20, 7.8
    # heights = [xmax, xmax]
    gs = gridspec.GridSpec(
        ncols=1, nrows=2, width_ratios=widths, height_ratios=heights)
    ft_label_size = {'fontname': 'Arial', 'fontsize': H*2.0}  # h*0.023
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
        fig_ax_2.text(x=0, y=hor_up_line, s=headers[0],
                      weight='bold', ha='left', color=(0.4941, 0.5686, 0.5843, 1.0), **ft_title_size)
        fig_ax_2.text(x=cols-step * 2, y=hor_up_line, s=headers[1],
                      weight='bold', ha='center', color=(0.4941, 0.5686, 0.5843, 1.0), **ft_title_size)
        fig_ax_2.text(x=cols, y=hor_up_line, s=headers[2],
                      weight='bold', ha='center', color=(0.4941, 0.5686, 0.5843, 1.0), **ft_title_size)
        fig_ax_2.text(x=ax2_xmax, y=hor_up_line, s=headers[3],
                      weight='bold', ha='right', color=(0.4941, 0.5686, 0.5843, 1.0), **ft_title_size)
    else:
        fig_ax_2.text(x=0, y=hor_up_line, s=headers[0],
                      weight='bold', ha='left', color=(0.4941, 0.5686, 0.5843, 1.0), **ft_title_size)
        fig_ax_2.text(x=cols - step, y=hor_up_line, s=headers[1],
                      weight='bold', ha='center', color=(0.4941, 0.5686, 0.5843, 1.0), **ft_title_size)
        fig_ax_2.text(x=ax2_xmax, y=hor_up_line, s=headers[2],
                      weight='bold', ha='right', color=(0.4941, 0.5686, 0.5843, 1.0), **ft_title_size)

    # линия сетки и основной разделитель заголовка
    if results:
        for row in range(1, rows + 1):
            fig_ax_2.plot([0.0, ax2_xmax], [row - step, row - step],
                          ls=':', lw=h*0.002, c='black')
        # основной разделитель заголовка
        fig_ax_2.plot([0, ax2_xmax], [rows+step, rows+step],
                      lw=h*0.005, color=(0.4941, 0.5686, 0.5843, 1.0))
        fig_ax_2.plot([0, ax2_xmax], [rows - row_num + step, rows - row_num + step],
                      lw=h*0.005,
                      color=(0.4941, 0.5686, 0.5843, 1.0))
        fig_ax_2.plot([0, ax2_xmax], [step, step],
                      lw=h*0.010,
                      color=(0.4941, 0.5686, 0.5843, 1.0))
    else:
        # линия сетки
        for row in range(1, rows + 1):
            fig_ax_2.plot([0.0, ax2_xmax], [row - step, row - step],
                          ls=':', lw=h*0.002, c='black')
        # основной разделитель заголовка
        fig_ax_2.plot([0, ax2_xmax], [rows+step, rows+step],
                      lw=h*0.005, color=(0.4941, 0.5686, 0.5843, 1.0))
        fig_ax_2.plot([0, ax2_xmax], [step, step], lw=h*0.010,
                      color=(0.4941, 0.5686, 0.5843, 1.0))

    # заполнение таблицы данных
    if column == 4:
        for row in range(1, rows + 1):
            d = data[row - 1]
            fig_ax_2.text(x=0, y=row, s=d.get(rows_keys[0]),
                          va='center', ha='left', **ft_size)
            fig_ax_2.text(x=cols - step * 2, y=row, s=d.get(rows_keys[1]), va='center',
                          ha='center', weight='bold', **ft_size)
            fig_ax_2.text(x=cols, y=row, s=d.get(rows_keys[2]) if not isinstance(d.get(rows_keys[2]), datetime) else d.get(rows_keys[2]).strftime("%Y-%m-%d"),
                          va='center', weight='bold', ha='center', **ft_size)
            fig_ax_2.text(x=ax2_xmax, y=row, s=d.get(rows_keys[3]) if not isinstance(d.get(rows_keys[2]), datetime) else d.get(rows_keys[3]).strftime("%Y-%m-%d"),
                          va='center', ha='right', **ft_size)
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
        rect = patches.Rectangle((cols - step, step),  # нижняя левая начальная позиция (x,y)
                                 width=0.950,
                                 height=ax2_ymax - step + 0.125,
                                 ec='none',
                                 color=(0.9372, 0.9098, 0.8353, 1.0),
                                 alpha=1.0,
                                 zorder=-1)
    else:
        rect = patches.Rectangle((cols - step * 2, step),  # нижняя левая начальная позиция (x,y)
                                 width=1.00,
                                 height=ax2_ymax - step + 0.125,
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


def get_plot_graph(x_values, y_values, label, x_label, y_label, ylim: int | float = None,
                   add_annotate: bool = False, text_annotate: str = None, x_ann: int | float = None, y_ann: int | float = None,
                   add_legend: bool = False, loc_legend: int = 1,
                   add_fill_between: bool = False, param_fill: int | float = None, label_fill: str = None,
                   add_axhline: bool = False, label_axline: str = None, plot_color=(0.9, 0.1, 0, 0.9), **kwargs):
    # размеры рисунка в дюймах
    px = 96.358115  # 1 дюйм = 2.54 см = 96.358115 pixel
    w = 650  # px
    h = 650  # px
    bottom = 0.090
    right = 0.970
    left = 0.110 if ylim == None else 0.100
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

    """____Первая часть таблицы____"""
    # [left, bottom, width, height]
    fig_ax_1 = fig.add_axes(
        [0.03, 0.0, 1.0, 1.86], frameon=True, aspect=1.0, xlim=(0.0, xmax+0.25))
    fig_ax_1.axis('off')

    fig_ax_1.text(x=0.0, y=0.025, s=label,
                  weight='bold', ha='left', **ft_label_size)
    fig_ax_1.plot([0, xmax], [0.0, 0.0], lw='1.0',
                  color=(0.913, 0.380, 0.082, 1.0))
    imagebox = OffsetImage(logo, zoom=w*0.000085, dpi_cor=True)
    ab = AnnotationBbox(imagebox, (xmax-(xmax/33.3), 0.025),
                        frameon=False, pad=0, box_alignment=(0.00, 0.0))
    fig_ax_1.add_artist(ab)

    """____Вторая часть таблицы____"""
    fig_ax_2 = fig.add_subplot(gs[0, 0])
    fig_ax_2.plot(x_values, y_values, '-',
                  #   linewidth=3,
                  color=plot_color, **kwargs)
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
                        labelpad=None, weight='bold', loc='center', **ft_size)

    # Ось ординат Yaxis
    if ylim == None:
        fig_ax_2.set_ylim(0.0, max(y_values) + max(y_values)*0.01)
    else:
        fig_ax_2.set_ylim(0.0, ylim)
        fig_ax_2.ticklabel_format(
            axis='y', style='sci', scilimits=(0, 2), useOffset=True)
    fig_ax_2.set_ylabel(ylabel=y_label,
                        fontdict=None, labelpad=None, weight='bold', loc='center', **ft_size)

    if add_annotate:
        fig_ax_2.annotate(text_annotate,
                          xy=(0, max(y_values) + max(y_values)
                              * 0.01 if ylim == None else ylim),
                          xytext=(x_ann + (x_ann / 50) if x_ann else min(x_values),
                                  y_ann + (y_ann / 50) if y_ann else min(y_values)),
                          xycoords='data', textcoords='data', weight='bold', **ft_size)

        if y_ann:
            fig_ax_2.hlines(y=y_ann, xmin=0, xmax=x_ann*0.99, linestyle='--',
                            linewidth=1, color=(0.1, 0.1, 0, 1.0))
        if x_ann:
            fig_ax_2.vlines(x=x_ann, ymin=0, ymax=y_ann*0.99, linestyle='--',
                            linewidth=1, color=(0.1, 0.1, 0, 1.0))
        if y_ann and x_ann:
            fig_ax_2.scatter(x_ann, y_ann, s=90, marker='o',
                             color=(0.9, 0.1, 0.0, 0.90))

    if add_axhline:
        fig_ax_2.axhline(param_fill,
                         color="red", linestyle="--", lw=1, label=f'{label_axline} ≥ {param_fill} м²/м²')

    if add_fill_between:
        fig_ax_2.fill_between(x_values,
                              y_values,
                              param_fill,
                              where=[d > param_fill for d in y_values],
                              color='red', alpha=0.25, label=label_fill)

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
                  color=(0, 0, 0, 0.5),
                  linestyle=':',
                  linewidth=0.250)

    if add_legend:
        fig_ax_2.legend(fontsize=10, framealpha=0.95,
                        facecolor="w", loc=loc_legend)
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
