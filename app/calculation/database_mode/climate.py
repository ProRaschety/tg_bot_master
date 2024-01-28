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
        log.info("Метеоданные")
        clim_data = {"pwindn": data.pwindn,  # 0
                     "pwindne": data.pwindne,  # 45
                     "pwinde": data.pwinde,  # 90
                     "pwindse": data.pwindse,  # 135
                     "pwinds": data.pwinds,  # 180
                     "pwindsw": data.pwindsw,  # 225
                     "pwindw": data.pwindw,  # 270
                     "pwindnw": data.pwindnw  # 315
                     }

        px = 96.358115  # 1 дюйм = 2.54 см = 96.358115 pixel
        w = 500  # px
        h = 500  # px
        left = 0.030
        bottom = 0.080
        right = 0.970
        top = 0.920
        hspace = 0.100
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

        widths = [1.0]
        heights = [xmax, xmax]
        gs = gridspec.GridSpec(
            ncols=1, nrows=2, width_ratios=widths, height_ratios=heights)
        ft_label_size = {'fontname': 'Arial', 'fontsize': w*0.021}
        ft_title_size = {'fontname': 'Arial', 'fontsize': 10}
        ft_size = {'fontname': 'Arial', 'fontsize': 10}
        logo = plt.imread('temp_files/temp/logo.png')
        # logo = image.imread('temp_files/temp/logo.png')
        # logo = plt.imread('logo.png')
        # [left, bottom, width, height]
        fig_ax_1 = fig.add_axes(
            [left, 0.0, 1.0, 1.86], frameon=True, aspect=1.0, xlim=(0.0, xmax+0.25))
        fig_ax_1.axis('off')
        fig_ax_1.text(x=0.0, y=0.025, s='Метеоданные',
                      weight='bold', ha='left', **ft_label_size)
        fig_ax_1.plot([0, xmax], [0.0, 0.0], lw='1.0',
                      color=(0.913, 0.380, 0.082, 1.0))
        imagebox = OffsetImage(logo, zoom=w*0.000085, dpi_cor=True)
        ab = AnnotationBbox(imagebox, (xmax-(xmax/33.3), 0.025),
                            frameon=False, pad=0, box_alignment=(0.00, 0.0))
        fig_ax_1.add_artist(ab)

        fig_ax_2 = fig.add_subplot(gs[0, 0])
        rows = 7
        cols = 4
        fig_ax_2.set_xlim(0.0, cols)
        fig_ax_2.set_ylim(0.0, rows+0.5)

        fig_ax_2.text(x=0.0, y=rows-0.2, s='Регион:', ha='left', **ft_size)
        fig_ax_2.text(x=2.05, y=rows-0.2, s='Московская область',
                      weight='bold', ha='left', **ft_size)
        fig_ax_2.text(x=0.0, y=rows-1.2, s='Населенный пункт:',
                      ha='left', **ft_size)
        fig_ax_2.text(x=2.05, y=rows-1.2, s='Москва',
                      weight='bold', ha='left', **ft_size)
        fig_ax_2.text(
            x=0.0, y=rows-2.2, s='Максимальная температура, \u00B0С:', ha='left', **ft_size)
        fig_ax_2.text(x=2.05, y=rows-2.2, s='35',
                      weight='bold', ha='left', **ft_size)
        fig_ax_2.text(
            x=0.0, y=rows-3.2, s='Максимальная скорость ветра, м/с:', ha='left', **ft_size)
        fig_ax_2.text(x=2.05, y=rows-3.2, s='3.5',
                      weight='bold', ha='left', **ft_size)
        fig_ax_2.text(x=0.0, y=rows-4.2, s='Вероятность штиля:',
                      ha='left', **ft_size)
        fig_ax_2.text(x=2.05, y=rows-4.2, s='0.35',
                      weight='bold', ha='left', **ft_size)

        fig_ax_2.text(x=0.0, y=rows-5.2, s='Направление:',
                      ha='left', **ft_size)
        fig_ax_2.text(x=1.25, y=rows - 5.2, s='С', ha='center', **ft_size)
        fig_ax_2.text(x=1.60, y=rows - 5.2, s='СВ', ha='center', **ft_size)
        fig_ax_2.text(x=1.95, y=rows - 5.2, s='В', ha='center', **ft_size)
        fig_ax_2.text(x=2.30, y=rows - 5.2, s='ЮВ', ha='center', **ft_size)
        fig_ax_2.text(x=2.65, y=rows - 5.2, s='Ю', ha='center', **ft_size)
        fig_ax_2.text(x=3.00, y=rows - 5.2, s='ЮЗ', ha='center', **ft_size)
        fig_ax_2.text(x=3.35, y=rows - 5.2, s='З', ha='center', **ft_size)
        fig_ax_2.text(x=3.70, y=rows - 5.2, s='СЗ', ha='center', **ft_size)

        fig_ax_2.text(x=0.0, y=rows-6.2, s='Повторяемость, %:',
                      ha='left', **ft_size)
        fig_ax_2.text(x=1.25, y=rows - 6.2, s=data.pwindn,
                      weight='bold', ha='center', **ft_size)
        fig_ax_2.text(x=1.60, y=rows - 6.2, s=data.pwindne,
                      weight='bold', ha='center', **ft_size)
        fig_ax_2.text(x=1.95, y=rows - 6.2, s=data.pwinde,
                      weight='bold', ha='center', **ft_size)
        fig_ax_2.text(x=2.30, y=rows - 6.2, s=data.pwindse,
                      weight='bold', ha='center', **ft_size)
        fig_ax_2.text(x=2.65, y=rows - 6.2, s=data.pwinds,
                      weight='bold', ha='center', **ft_size)
        fig_ax_2.text(x=3.00, y=rows - 6.2, s=data.pwindsw,
                      weight='bold', ha='center', **ft_size)
        fig_ax_2.text(x=3.35, y=rows - 6.2, s=data.pwindw,
                      weight='bold', ha='center', **ft_size)
        fig_ax_2.text(x=3.70, y=rows - 6.2, s=data.pwindnw,
                      weight='bold', ha='center', **ft_size)

        # линия сетки
        for row in range(rows):
            fig_ax_2.plot([0, cols+0.5], [row+.5, row+.5],
                          ls=':', lw='.5', c='grey')

        fig_ax_2.axis('off')
        # plt.style.use('default')
        # plt.style.use('bmh')
        # plt.style.use('fivethirtyeight')
        # plt.style.use('ggplot')
        plt.style.use('Solarize_Light2')
        fig_ax_3 = fig.add_subplot(gs[1, 0], projection='polar')

        angles = np.arange(0, 2*pi, pi/4.0)  # Задаём массив направлений
        r = [clim_data.get(value, "0")
             for value in clim_data]  # массив значений
        linewidth = 1.75
        linestyle = 'solid'
        color = (0.9, 0.1, 0, 0.9)
        fig_ax_3.plot(angles, r, color=color,
                      linewidth=linewidth, linestyle=linestyle)
        fig_ax_3.set_theta_direction(-1)
        fig_ax_3.set_theta_offset(pi / 2.0)
        fig_ax_3.plot((angles[-1], angles[0]), (r[-1], r[0]), color=color,
                      linewidth=linewidth, linestyle=linestyle)
        x_labels = ['С', 'СВ', 'В', 'ЮВ', 'Ю', 'ЮЗ', 'З', 'СЗ']
        fig_ax_3.set_xticklabels(x_labels, **ft_size)
        fig_ax_3.grid(visible=True,
                      which='major',
                      axis='both',
                      color=(0, 0, 0, 0.5),
                      linestyle=':',
                      linewidth=0.350)

        buffer = io.BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        wind_rose = buffer.getvalue()
        buffer.close()
        plt.cla()
        plt.style.use('default')
        plt.close(fig)
        return wind_rose
