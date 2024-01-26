import logging
import io
import re
import json

from fluentogram import TranslatorRunner

from app.tg_bot.utilities.misc_utils import get_temp_folder

import math as m
import matplotlib as mpl
from math import pi
import numpy as np
import matplotlib.image as image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from scipy.interpolate import interp1d

# logging.getLogger('matplotlib.font_manager').disabled = True
# logging.getLogger('PIL.PngImagePlugin').disabled = True

for name in ["matplotlib", "matplotlib.font", "matplotlib.pyplot", "PngImagePlugin", "PIL.PngImagePlugin"]:
    logger = logging.getLogger(name)
    logger.setLevel(logging.CRITICAL)
    logger.disabled = True

log = logging.getLogger(__name__)


class Climate:
    def __init__(self):
        pass

    def get_climate_info(self, data):
        log.info("Годовая повторяемость направления ветра")
        data = {"pwindn": data.pwindn,  # 0
                "pwindne": data.pwindne,  # 45
                "pwinde": data.pwinde,  # 90
                "pwindse": data.pwindse,  # 135
                "pwinds": data.pwinds,  # 180
                "pwindsw": data.pwindsw,  # 225
                "pwindw": data.pwindw,  # 270
                "pwindnw": data.pwindnw  # 315
                }
        px = 96.358115
        w = 500  # px
        h = 600  # px
        # Создание объекта Figure
        margins = {
            "left": 0.080,  # 0.030
            "bottom": 0.060,  # 0.030
            "right": 0.950,  # 0.970
            "top": 0.950,  # 0.900
            "hspace": 0.250  # 0.200
        }
        fig = plt.figure(figsize=(w / px, h / px), dpi=300)
        fig.subplots_adjust(**margins)

        # fg = plt.figure(figsize=(7, 7), constrained_layout=True)
        widths = [1]
        heights = [0.5, 5]
        gs = gridspec.GridSpec(
            ncols=1, nrows=2, width_ratios=widths, height_ratios=heights)

        fig_ax_1 = fig.add_subplot(gs[0, 0])
        logo = plt.imread('temp_files/temp/logo.png')
        fig_ax_1.plot()
        fig_ax_1.axis('off')
        ft_title_size = {'fontname': 'Arial', 'fontsize': 18}
        fig_ax_1.set_xlim(0.0, 0.9)
        fig_ax_1.set_ylim(-.5, 0.5)
        fig_ax_1.text(x=0.05, y=-0.5, s='Годовая повторяемость ветра',
                      weight='bold', ha='left', **ft_title_size)
        # fig_ax_1.figure.figimage(logo, 10, 10, alpha=.15, zorder=1)
        # fig_ax_1.imshow(logo, alpha=.15, zorder=.1)
        imagebox = OffsetImage(logo, zoom=0.1)
        ab = AnnotationBbox(imagebox, (0, 0))
        fig_ax_1.add_artist(ab)

        fig_ax_2 = fig.add_subplot(gs[1, 0], projection='polar')
        angles = np.arange(0, 2*pi, pi/4.0)  # Задаём массив направлений
        r = [data.get(value, "0") for value in data]  # массив значений
        fig_ax_2.plot(angles, r, color='r', linewidth=2.5)
        fig_ax_2.set_theta_direction(-1)
        fig_ax_2.set_theta_offset(pi / 2.0)
        fig_ax_2.plot((angles[-1], angles[0]), (r[-1], r[0]), color='r',
                      linewidth=2.5)
        x_labels = ['С', 'СВ', 'В', 'ЮВ', 'Ю', 'ЮЗ', 'З', 'СЗ']
        fig_ax_2.set_xticklabels(x_labels)

        # # размеры рисунка в дюймах
        # inch = 2.54  # 1 дюйм = 2.54 см = 96.358115 pixel
        # px = 96.358115
        # w = 600  # px
        # h = 600  # px
        # # Создание объекта Figure
        # fig = plt.figure(figsize=(w / px, h / px), dpi=200)
        # # fig = plt.figure() # Создаём новое полотно, на котором будем рисовать

        # mpl.style.use('classic')
        # # plt.xkcd()
        # mpl.rcParams['font.family'] = 'fantasy'
        # mpl.rcParams['font.fantasy'] = 'Arial'
        # mpl.rcParams["axes.labelsize"] = 16
        # mpl.rcParams["axes.titlesize"] = 16
        # # mpl.rcParams["xtick.labelsize"] = 14
        # # mpl.rcParams["ytick.labelsize"] = 14

        # x_labels = ['С', 'СВ', 'В', 'ЮВ', 'Ю', 'ЮЗ', 'З', 'СЗ']
        # angles = np.arange(0, 2*m.pi, m.pi/4.0)  # Задаём массив направлений
        # r = [data.get(value, "0") for value in data]  # массив значений
        # # ax - полотно в полярной проекции, занимающее всё пространство полотно fig
        # ax = fig.add_subplot(111, projection='polar')
        # ax.set_title("Годовая повторяемость направления ветра, %", y=1.08)
        # # Рисуем график и его название
        # ax.plot(angles, r, color='r', linewidth=2.5)
        # # теперь увеличение угла theta будет по часовой (-1 - увеличение угла
        # ax.set_theta_direction(-1)
        # # идёт против часовой стрелки)
        # # изменим положение нуля (ставим его на положение 'N', которое
        # ax.set_theta_offset(m.pi / 2.0)
        # # сейчас равно 90 градусам)
        # ax.plot((angles[-1], angles[0]), (r[-1], r[0]), color='r',
        #         linewidth=2.5)  # Добавляем ещё один plot-линию,
        # # которая соединяет последнюю и первую точки.
        # ax.set_xticklabels(x_labels)

        # # ax.annotate('text', xy=(45, 95))

        # # logo = plt.imread('temp_files/temp/fsr_logo.png')
        # # plt.imshow(logo)
        # # imagebox = OffsetImage(logo, zoom=.5)
        # # ab = AnnotationBbox(imagebox, (0, 0))
        # # ax.add_artist(ab)

        buffer = io.BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        wind_rose = buffer.getvalue()
        buffer.close()
        plt.cla()
        plt.close(fig)
        return wind_rose
