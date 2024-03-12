import logging
import io
# import json
import math as m
import numpy as np
import matplotlib.pyplot as plt
# import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from scipy.constants import physical_constants
from scipy.interpolate import interp1d

from app.calculation.physics.physics_utils import compute_area_circle

log = logging.getLogger(__name__)


class PhysicTool:
    def __init__(self, type_substance: str | None = None) -> None:
        self.type_substance = type_substance
        self.pressure_ambient = physical_constants.get(
            'standard atmosphere')[0]  # Па
        self.R = physical_constants.get('molar gas constant')[0]  # Дж/моль*К
        self.K = 273.15  # К
        self.g = physical_constants.get('standard acceleration of gravity')[0]

    def get_init_data(self, *args, **kwargs):
        head = ('Наименование', 'Параметр', 'Значение', 'Ед.изм.')
        if self.type_substance == 'liquid':
            label = 'Расход жидкости'
        elif self.type_substance == 'liq_gas':
            label = 'Расход сжиженного газа'
        elif self.type_substance == 'comp_gas':
            label = 'Расход сжатого газа'
        elif self.type_substance == 'evaporation_rate':
            label = 'Испарение жидкой фазы'
        else:
            label = 'Расход паров жидкости'

        if self.type_substance == 'liquid':
            data_table = [
                {'id': 'Коэффициент истечения', 'var': 'μ', 'unit_1': kwargs.get(
                    'tool_liquid_mu'), 'unit_2': '-'},
                {'id': 'Диаметр отверстия', 'var': 'dотв', 'unit_1': kwargs.get(
                    'tool_liquid_hole_diameter'), 'unit_2': 'м'},
                {'id': 'Расстояние от дна резервуара\nдо центра отверстия', 'var': 'rh', 'unit_1': kwargs.get(
                    'tool_liquid_hole_distance'), 'unit_2': 'м'},
                {'id': 'Степень заполнения резервуара', 'var': 'k', 'unit_1': kwargs.get(
                    'tool_liquid_fill_factor'), 'unit_2': 'м\u00B3/м\u00B3'},
                {'id': 'Высота резервуара', 'var': 'Hp',  'unit_1': kwargs.get(
                    'tool_liquid_height_vessel'), 'unit_2': 'м'},
                {'id': 'Объем резервуара', 'var': 'Vр',
                    'unit_1': f"{float((kwargs.get('tool_liquid_volume_vessel', 1000))):.1f}", 'unit_2': 'м\u00B3'},
                {'id': 'Темепература жидкости в резервуаре', 'var': 'tж', 'unit_1': kwargs.get(
                    'tool_liquid_temperature'), 'unit_2': '\u00B0С'},
                {'id': 'Плотность жидкости', 'var': 'ρ', 'unit_1': f"{float((kwargs.get('tool_liquid_density', 1000))):.1f}", 'unit_2': 'кг/м\u00B3'}]
        elif self.type_substance == 'comp_gas':
            pres_init = float(kwargs.get('tool_comp_gas_pres_init'))
            molar_mass = float(kwargs.get('tool_comp_gas_molar_mass'))
            temperature = float(kwargs.get('tool_comp_gas_temperature'))
            density_gas = self.compute_density_gas(
                pres_init=pres_init, molar_mass=molar_mass, temperature=temperature)
            data_table = [
                {'id': 'Коэффициент истечения', 'var': 'μ',
                    'unit_1': kwargs.get('tool_comp_gas_mu'), 'unit_2': '-'},
                {'id': 'Диаметр отверстия', 'var': 'dотв', 'unit_1': kwargs.get(
                    'tool_comp_gas_hole_diameter'), 'unit_2': 'м'},
                {'id': 'Объем резервуара', 'var': 'Vр',
                    'unit_1': f"{float((kwargs.get('tool_comp_gas_volume_vessel', 1000))):.1f}", 'unit_2': 'м\u00B3'},
                {'id': 'Удельная теплоемкость газа', 'var': 'Cv',
                    'unit_1': kwargs.get('tool_comp_gas_specific_heat_const_vol'), 'unit_2': 'кДж/кг∙K'},
                {'id': 'Плотность газа в резервуаре\nпри начальном давлении',
                    'var': 'ρₒ', 'unit_1': f"{density_gas:.3f}", 'unit_2': 'кг/м\u00B3'},
                {'id': 'Коэффициент Пуассона (адиабата газа)', 'var': 'ϒ',
                    'unit_1': kwargs.get('tool_comp_gas_coef_poisson'), 'unit_2': '-'},
                {'id': 'Молярная масса газа', 'var': 'M',
                    'unit_1': molar_mass, 'unit_2': 'кг/моль'},
                {'id': 'Темепература газа в оборудовании', 'var': 'tг',
                    'unit_1': temperature, 'unit_2': '\u00B0С'},
                {'id': 'Начальное давление газа в резервуаре',
                    'var': 'Pvₒ', 'unit_1': f"{pres_init:.2e}", 'unit_2': 'Па'},
                {'id': 'Атмосферное давление', 'var': 'Pa',
                    'unit_1': self.pressure_ambient, 'unit_2': 'Па'}
            ]
        elif self.type_substance == 'liq_gas_vap':
            pres_init = float(kwargs.get('tool_comp_gas_pres_init'))
            molar_mass = float(kwargs.get('tool_comp_gas_molar_mass'))
            temperature = float(kwargs.get('tool_comp_gas_temperature'))
            density_gas = self.compute_density_gas(
                pres_init=pres_init, molar_mass=molar_mass, temperature=temperature)
            data_table = [
                {'id': 'Коэффициент истечения', 'var': 'μ',
                    'unit_1': kwargs.get('tool_comp_gas_mu'), 'unit_2': '-'},
                {'id': 'Диаметр отверстия', 'var': 'dотв', 'unit_1': kwargs.get(
                    'tool_comp_gas_hole_diameter'), 'unit_2': 'м'},
                {'id': 'Объем резервуара', 'var': 'Vр',
                    'unit_1': f"{float((kwargs.get('tool_comp_gas_volume_vessel', 1000))):.1f}", 'unit_2': 'м\u00B3'},
                {'id': 'Молярная масса газа', 'var': 'M',
                    'unit_1': molar_mass, 'unit_2': 'кг/моль'},
                {'id': 'Безразмерное давление сжиженного газа', 'var': 'PR',
                    'unit_1': 'Pv/Рс', 'unit_2': 'Па'},
                {'id': 'Критическое давление сжиженного газа', 'var': 'Pc',
                    'unit_1': 'Рс', 'unit_2': 'Па'},
                {'id': 'Критическая темепература сжиженного газа', 'var': 'Tc',
                    'unit_1': 'Tc', 'unit_2': '\u00B0С'},
                {'id': 'Начальное давление cжиженного газа в резервуаре',
                    'var': 'Pvₒ', 'unit_1': f"{pres_init:.2e}", 'unit_2': 'Па'},
            ]
        elif self.type_substance == 'liq_gas_liq':
            pass

        return data_table, head, label

    def get_result_data(self, *args, **kwargs):
        head = ('Наименование', 'Параметр', 'Значение', 'Ед.изм.')
        if self.type_substance == 'liquid':
            label = 'Расход жидкости'
        elif self.type_substance == 'liq_gas':
            label = 'Расход сжиженного газа'
        elif self.type_substance == 'comp_gas':
            label = 'Расход сжатого газа'
        else:
            label = 'Расход паров жидкости'

        if self.type_substance == 'liquid':
            density_liq = float(kwargs.get('tool_liquid_density'))
            mass_flow = self.compute_init_mass_flow_rate(**kwargs)
            vol_ves = float(kwargs.get('tool_liquid_volume_vessel'))
            data_table = [
                {'id': 'Начальный объемный расход жидкости',
                    'var': 'Gvₒ', 'unit_1': f"{(mass_flow/density_liq):.3f}", 'unit_2': 'м\u00B3/с'},
                {'id': 'Начальный массовый расход жидкости',
                    'var': 'Gmₒ', 'unit_1': f"{mass_flow:.2f}", 'unit_2': 'кг/с'},
                {'id': 'Начальная масса жидкости в резервуаре',
                    'var': 'mₒ', 'unit_1': f"{(density_liq * vol_ves):.1f}", 'unit_2': 'кг'},
                {'id': 'Коэффициент истечения', 'var': 'μ', 'unit_1': kwargs.get(
                    'tool_liquid_mu'), 'unit_2': '-'},
                {'id': 'Диаметр отверстия', 'var': 'dотв', 'unit_1': kwargs.get(
                    'tool_liquid_hole_diameter'), 'unit_2': 'м'},
                {'id': 'Расстояние от дна резервуара\nдо центра отверстия', 'var': 'rh', 'unit_1': kwargs.get(
                    'tool_liquid_hole_distance'), 'unit_2': 'м'},
                {'id': 'Степень заполнения резервуара', 'var': 'k', 'unit_1': kwargs.get(
                    'tool_liquid_fill_factor'), 'unit_2': 'м\u00B3/м\u00B3'},
                {'id': 'Высота резервуара', 'var': 'Hp',  'unit_1': kwargs.get(
                    'tool_liquid_height_vessel'), 'unit_2': 'м'},
                {'id': 'Объем резервуара', 'var': 'Vр',
                    'unit_1': f"{vol_ves:.1f}", 'unit_2': 'м\u00B3'},
                {'id': 'Темепература жидкости в резервуаре', 'var': 'tж', 'unit_1': kwargs.get(
                    'tool_liquid_temperature'), 'unit_2': '\u00B0С'},
                {'id': 'Плотность жидкости', 'var': 'ρ',
                    'unit_1': f"{density_liq:.1f}", 'unit_2': 'кг/м\u00B3'}
            ]

        elif self.type_substance == 'comp_gas':
            pres_init = float(kwargs.get('tool_comp_gas_pres_init'))
            molar_mass = float(kwargs.get('tool_comp_gas_molar_mass'))
            temperature = float(kwargs.get('tool_comp_gas_temperature'))
            density_gas = self.compute_density_gas(
                pres_init=pres_init, molar_mass=molar_mass, temperature=temperature)
            mass_flow = self.compute_outflow_comp_gas(**kwargs)
            pres_init = float(kwargs.get('tool_comp_gas_pres_init'))
            coef_k = self._compute_coef_k(pres_init=pres_init, **kwargs)
            gamma = float(kwargs.get('tool_comp_gas_coef_poisson'))
            coef_p = (2 / (gamma + 1)) ** (gamma / (gamma - 1))
            data_table = [
                {'id': 'Начальный объемный расход газа',
                    'var': 'Gvₒ', 'unit_1': f"{(mass_flow/density_gas):.3f}", 'unit_2': 'м\u00B3/с'},
                {'id': 'Начальный массовый расход газа',
                    'var': 'Gmₒ', 'unit_1': f"{mass_flow:.3f}", 'unit_2': 'кг/с'},
                {'id': 'Режим истечения', 'var': '-',
                    'unit_1': "до-\nкритический" if coef_k >= coef_p else "сверх-\nкритический", 'unit_2': '-'},
                {'id': 'Начальная масса газа в резервуаре',
                    'var': 'mₒ', 'unit_1': f"{(density_gas * float((kwargs.get('tool_comp_gas_volume_vessel')))):.1f}", 'unit_2': 'кг'},
                {'id': 'Коэффициент истечения', 'var': 'μ',
                    'unit_1': kwargs.get('tool_comp_gas_mu'), 'unit_2': '-'},
                {'id': 'Диаметр отверстия', 'var': 'dотв', 'unit_1': kwargs.get(
                    'tool_comp_gas_hole_diameter'), 'unit_2': 'м'},
                {'id': 'Объем резервуара', 'var': 'Vр',
                    'unit_1': f"{float((kwargs.get('tool_comp_gas_volume_vessel', 1000))):.1f}", 'unit_2': 'м\u00B3'},
                {'id': 'Удельная теплоемкость газа', 'var': 'Cv',
                    'unit_1': kwargs.get('tool_comp_gas_specific_heat_const_vol'), 'unit_2': 'кДж/кг∙K'},
                {'id': 'Плотность газа в резервуаре\nпри начальном давлении',
                    'var': 'ρₒ', 'unit_1': f"{density_gas:.3f}", 'unit_2': 'кг/м\u00B3'},
                {'id': 'Коэффициент Пуассона (адиабата газа)', 'var': 'ϒ',
                    'unit_1': kwargs.get('tool_comp_gas_coef_poisson'), 'unit_2': '-'},
                {'id': 'Молярная масса газа', 'var': 'M',
                    'unit_1': molar_mass, 'unit_2': 'кг/моль'},
                {'id': 'Темепература газа в оборудовании', 'var': 'tг',
                    'unit_1': temperature, 'unit_2': '\u00B0С'},
                {'id': 'Начальное давление газа в резервуаре',
                    'var': 'Pv', 'unit_1': f"{pres_init:.2e}", 'unit_2': 'Па'},
                # {'id': 'Атмосферное давление', 'var': 'Pa',
                #     'unit_1': self.pressure_ambient, 'unit_2': 'Па'}
            ]

        elif self.type_substance == 'liq_gas_vap':
            pass
        elif self.type_substance == 'liq_gas_liq':
            pass

        return data_table, head, label

    def compute_init_mass_flow_rate(self, **kwargs):
        density_liq = float((kwargs.get('tool_liquid_density')))
        height_vessel = float((kwargs.get('tool_liquid_height_vessel')))
        fill_factor = float((kwargs.get('tool_liquid_fill_factor')))
        hole_diameter = float((kwargs.get('tool_liquid_hole_diameter')))
        mu = float((kwargs.get('tool_liquid_mu')))
        # p_s = 17.499  # давление насыщенного пара, кПа
        hole_area = compute_area_circle(diameter=hole_diameter)
        # столб жидкости в резервуаре, м
        initial_height_liquid = fill_factor * height_vessel
        # h_hol = 1  # высота расположения отверстия от днища, м
        # hi_hol = h_liq0 - h_hol  # Высота столба жидкости над отверстием, м
        initial_pressure_in_vessel = density_liq * self.g * \
            initial_height_liquid + self.pressure_ambient  # Давление в оборудовании, Па
        # начальный массовый расход, кг/с
        initial_mass_flow = mu * hole_area * \
            m.sqrt(2 * (initial_pressure_in_vessel -
                   self.pressure_ambient) * density_liq)
        return initial_mass_flow

    def _compute_mass_flow_rate(self, **kwargs):
        density_liq = float((kwargs.get('tool_liquid_density')))
        volume_vessel = float((kwargs.get('tool_liquid_volume_vessel')))
        height_vessel = float((kwargs.get('tool_liquid_height_vessel')))
        fill_factor = float((kwargs.get('tool_liquid_fill_factor')))
        hole_diameter = float((kwargs.get('tool_liquid_hole_diameter')))
        mu = float((kwargs.get('tool_liquid_mu')))
        initial_mass_flow = self.compute_init_mass_flow_rate(**kwargs)
        hole_area = compute_area_circle(diameter=hole_diameter)
        initial_mass = fill_factor * volume_vessel * density_liq
        # V_0 = initial_mass / density_liq  # Начальный объем жидкости в резервуаре, м3
        # a_equip = volume_vessel / height_vessel  # площадь сечения резервуара, м2
        # h_0 = V_0 / a_equip  # Начальный уровень жидкости в резервуаре, м
        initial_volume_flow = initial_mass_flow / density_liq
        max_range = int(volume_vessel / initial_volume_flow)
        delta_t = max_range / 60
        # масса жидкости в резервуаре в момент времни t, кг (M(0)-dMi)
        m_equip = [initial_mass]
        t_i = []  # шаг по времени, с
        fill_f = []  # степень заполнения, -
        # h_liq = []  # высота столба жидкости над отверстием, м
        p_stat = []  # гидростатичесое давление в момент времени t, Па
        G_t = []  # массовый расход жидкости в момент времени t, кг/с
        delta_m = [0]  # масса идкости вышедшее из резервуара за время t, кг
        total_m = [0]  # общая масса вышедшее из оборудования, кг (dMi-1+dMi)
        velocity_outflow = []

        for t in range(0, max_range, 1):
            if t == 0:
                fi = m_equip[t] / (volume_vessel * density_liq)
                h_liq_i = fi * height_vessel
                p_equip = density_liq * self.g * h_liq_i + self.pressure_ambient
                G_i = mu * hole_area * \
                    m.sqrt((2 * (p_equip - self.pressure_ambient) * density_liq))
                delta_m_i = G_i * delta_t
                # h_i = h_liq_i * (m_equip[-1] - delta_m_i) / m_equip[-1]
            elif t > 0:
                fi = m_equip[-1] / (volume_vessel * density_liq)
                h_liq_i = fi * height_vessel
                p_equip = density_liq * self.g * h_liq_i + self.pressure_ambient
                if float(p_equip) > self.pressure_ambient:
                    G_i = mu * hole_area * \
                        m.sqrt(
                            (2 * (p_equip - self.pressure_ambient) * density_liq))
                    delta_m_i = G_i * delta_t
                    # скорость истечения (м/с) по формуле Торричелли
                    velocity_outflow.append(m.sqrt(2 * self.g * h_liq_i))

                    # длина струи жидкости, м
                    # lenght_jet = m.sqrt((2 * self.g * h_liq_i)
                    #                     * 2 * (height_vessel - h_liq_i))
                    # h_i = h_liq_i * (m_equip[-1] - delta_m_i) / m_equip[-1]
                    # print(velocity_outflow[-1], lenght_jet)
                else:
                    break
            else:
                break

            m_equip.append(m_equip[t] - delta_m_i)
            t_i.append(t * delta_t)
            fill_f.append(fi)
            p_stat.append(p_equip)
            G_t.append(G_i)
            delta_m.append(delta_m_i)
            total_m.append(delta_m[t] + delta_m_i)

        return t_i, G_t

    def _compute_coef_k(self, pres_init: int | float, **kwargs):
        return self.pressure_ambient / pres_init

    def compute_density_gas(self, pres_init: int | float, molar_mass: int | float, temperature: int | float):
        return (pres_init * molar_mass) / (self.R * (self.K + temperature))

    def compute_outflow_comp_gas(self, **kwargs):
        pres_init = float(kwargs.get('tool_comp_gas_pres_init'))
        molar_mass = float(kwargs.get('tool_comp_gas_molar_mass'))
        temperature = float(kwargs.get('tool_comp_gas_temperature'))
        coef_poisson = float((kwargs.get('tool_comp_gas_coef_poisson')))
        hole_diameter = float((kwargs.get('tool_comp_gas_hole_diameter')))
        mu = float((kwargs.get('tool_comp_gas_mu')))
        hole_area = compute_area_circle(diameter=hole_diameter)
        coef_k = self._compute_coef_k(pres_init=pres_init)
        density_gas = self.compute_density_gas(
            pres_init=pres_init, molar_mass=molar_mass, temperature=temperature)

        if coef_k >= ((2 / (coef_poisson + 1)) ** (coef_poisson / (coef_poisson - 1))):
            outflow_rate = hole_area * mu * m.sqrt(pres_init * density_gas * ((2 * coef_poisson)/(coef_poisson - 1)) * (
                coef_k ** (2 / coef_poisson)) * (1 - (coef_k ** ((coef_poisson - 1) / coef_poisson))))
        else:
            outflow_rate = hole_area * mu * m.sqrt(pres_init * density_gas * coef_poisson * (
                (2 / (coef_poisson + 1)) ** ((coef_poisson + 1) / (coef_poisson - 1))))
        return outflow_rate

    def _compute_mass_flow_rate_gas(self, **kwargs):
        pres_init = float(kwargs.get('tool_comp_gas_pres_init'))
        molar_mass = float(kwargs.get('tool_comp_gas_molar_mass'))
        temperature = float(kwargs.get('tool_comp_gas_temperature'))
        coef_poisson = float(kwargs.get('tool_comp_gas_coef_poisson'))
        specific_heat_const_vol = float(kwargs.get(
            'tool_comp_gas_specific_heat_const_vol'))
        hole_diameter = float((kwargs.get('tool_comp_gas_hole_diameter')))
        vol_ves = float(kwargs.get('tool_comp_gas_volume_vessel'))
        mu = float((kwargs.get('tool_comp_gas_mu')))
        hole_area = compute_area_circle(diameter=hole_diameter)
        mass_flow = self.compute_outflow_comp_gas(**kwargs)
        density_gas = self.compute_density_gas(
            pres_init=pres_init, molar_mass=molar_mass, temperature=temperature)

        temp = [temperature + self.K]
        pres = [pres_init]
        density = [density_gas]
        t = []
        outflow = []
        delta_time = 1
        for i in np.arange(0, 3601, delta_time):
            coef_k = self._compute_coef_k(pres_init=pres[i])
            if coef_k >= ((2 / (coef_poisson + 1)) ** (coef_poisson / (coef_poisson - 1))):
                outflow_rate = hole_area * mu * m.sqrt(pres[i] * density[i] * ((2 * coef_poisson)/(coef_poisson - 1)) * (
                    coef_k ** (2 / coef_poisson)) * (1 - (coef_k ** ((coef_poisson - 1) / coef_poisson))))
            else:
                outflow_rate = hole_area * mu * m.sqrt(pres[i] * density[i] * coef_poisson * (
                    (2 / (coef_poisson + 1)) ** ((coef_poisson + 1) / (coef_poisson - 1))))

            delta_density = (outflow_rate / vol_ves) * delta_time
            delta_temp = (pres[-1] / ((density[-1] ** 2) *
                                      specific_heat_const_vol * 1000)) * delta_density
            density_new = density[-1] - delta_density
            temp_i = temp[-1] - delta_temp
            pres_i = self.R * temp_i * (density_new / molar_mass)

            density.append(density_new)
            pres.append(pres_i)
            temp.append(temp_i)
            outflow.append(outflow_rate)
            ti = i
            t.append(ti)
            if pres[-1] <= self.pressure_ambient:
                break
        return t, outflow

    def get_plot_mass_flow_rate(self, add_annotate: bool = False, add_legend: bool = False, **kwargs):
        if self.type_substance == 'liquid':
            s = 'График расхода жидкости'
            abscissa, plot_first = self._compute_mass_flow_rate(**kwargs)
            density = float(kwargs.get('tool_liquid_density'))
            log.info(s)
        elif self.type_substance == 'liq_gas':
            s = 'График расхода сжиженного газа'
            log.info(s)
        elif self.type_substance == 'comp_gas':
            pres_init = float(kwargs.get('tool_comp_gas_pres_init'))
            molar_mass = float(kwargs.get('tool_comp_gas_molar_mass'))
            temperature = float(kwargs.get('tool_comp_gas_temperature'))
            density = self.compute_density_gas(
                pres_init=pres_init, molar_mass=molar_mass, temperature=temperature)
            abscissa, plot_first = self._compute_mass_flow_rate_gas(**kwargs)
            s = 'График расхода сжатого газа'
            log.info(s)
        else:
            s = 'График расхода паров жидкости'
            log.info(s)

        # размеры рисунка в дюймах
        px = 96.358115  # 1 дюйм = 2.54 см = 96.358115 pixel
        w = 700  # px
        h = 700  # px
        left = 0.110
        bottom = 0.090
        right = 0.970
        top = 0.900
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

        fig_ax_1.text(x=0.0, y=0.025, s=s,
                      weight='bold', ha='left', **ft_label_size)
        fig_ax_1.plot([0, xmax], [0.0, 0.0], lw='1.0',
                      color=(0.913, 0.380, 0.082, 1.0))
        imagebox = OffsetImage(logo, zoom=w*0.000085, dpi_cor=True)
        ab = AnnotationBbox(imagebox, (xmax-(xmax/33.3), 0.025),
                            frameon=False, pad=0, box_alignment=(0.00, 0.0))
        fig_ax_1.add_artist(ab)

        """____Вторая часть таблицы____"""
        fig_ax_2 = fig.add_subplot(gs[0, 0])

        text_legend_first = 'Массовый расход, кг/с'
        text_legend_second = 'Расход 2'
        set_x_label = 'Время, с'
        set_y_label = 'Массовый расход, кг/с'

        # abscissa, plot_first = self._compute_mass_flow_rate(**kwargs)
        # plot_second = self.get_steel_heating()

        # abscissa = [x for x in range(0, xmax, 1)]

        fig_ax_2.plot(abscissa, plot_first, '-', linewidth=3,
                      label=text_legend_first, color=(0.9, 0.1, 0, 0.9))
        # fig_ax_2.plot(abscissa, plot_second, '-', linewidth=3,
        #               label=text_legend_second, color=(0, 0, 0, 0.9))
        # fig_ax_2.hlines(y=Tcr, xmin=0, xmax=time_fsr*0.96, linestyle='--',
        #                 linewidth=1, color=(0.1, 0.1, 0, 1.0))
        # fig_ax_2.vlines(x=time_fsr, ymin=0, ymax=Tcr*0.98, linestyle='--',
        #                 linewidth=1, color=(0.1, 0.1, 0, 1.0))
        # fig_ax_2.scatter(time_fsr, Tcr, s=90, marker='o',
        #                  color=(0.9, 0.1, 0, 1))
        # Ось абсцисс Xaxis
        fig_ax_2.set_xlim(0.0, max(abscissa) + max(abscissa)*0.05)
        fig_ax_2.set_xlabel(xlabel=set_x_label, fontdict=None,
                            labelpad=None, weight='bold', loc='center', **ft_size)
        # Ось ординат Yaxis
        fig_ax_2.set_ylim(0.0, max(plot_first) + max(plot_first)*0.05)
        fig_ax_2.set_ylabel(ylabel=set_y_label,
                            fontdict=None, labelpad=None, weight='bold', loc='center', **ft_size)

        if add_annotate:
            fig_ax_2.annotate(f"Начальный массовый расход: {max(plot_first):.2f} кг/с\n"
                              f"Начальный объемный расход: {(max(plot_first) / density):.4f} м\u00B3/с\n\n"
                              f"Время полного истечения: {max(abscissa):.1f} с\n"
                              f"Время полного истечения: {(max(abscissa)/60):.1f} мин\n",
                              xy=(0, max(plot_first)), xycoords='data', xytext=(max(abscissa)*0.03, 0), textcoords='data', weight='bold', **ft_size)

        if add_legend:
            fig_ax_2.legend(fontsize=12, framealpha=0.95, facecolor="w", loc=1)

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

    def calc_lower_heat_combustion(self, molec_mass: int | float = None,
                                   Cn: int | float = 0,
                                   Hn: int | float = 0,
                                   Oxn: int | float = 0,
                                   Bn: int | float = 0,
                                   Nn: int | float = 0,
                                   Sin: int | float = 0,
                                   Pn: int | float = 0,
                                   Sn: int | float = 0,
                                   Sen: int | float = 0,
                                   Ten: int | float = 0):
        C, H, N, S, P, Se, Te, Si, B, Ox = 12.0107, 1.00794, 14.0067, 32.065, 30.973762, 78.963, 127.603, 28.0855, 10.821, 15.9994
        if molec_mass:
            M = molec_mass
        else:
            M = C * Cn + H * Hn + N * Nn + S * Sn + P * Pn + \
                Se * Sen + Te * Ten + Si * Sin + B * Bn + Ox * Oxn
        heat_comb = 418 * ((81 * C * Cn + 246 * H * Hn + 26 * (N * Nn + S *
                           Sn + P * Pn + Se * Sen + Te * Ten + Si * Sin + B * Bn - Ox * Oxn))/M)
        log.info(f'M: {M}')
        log.info(f'heat_comb: {heat_comb}')
        return M, heat_comb

    def parse_phase_key(self, key):
        """
        Convert phase string identifier into value for phys library.
        All values besides 'gas' and 'liquid' will be converted to None

        Parameters
        ----------
        key : str
            Phase identifier key

        Returns
        -------
        str or None

        """
        return key if key in ['gas', 'liquid'] else None

    def compute_tank_mass_param(self, species=None, phase=None, temp=None, pres=None, vol=None, mass=None):
        log.info("Tank Mass calculation requested")
        phase = self.parse_phase_key(phase)
        if (temp is not None or phase is not None) and pres is not None and vol is not None and mass is not None:
            msg = 'Too many inputs provided - three of [temperature (or phase), pressure, volume, mass] required'
            raise ValueError(msg)

        if vol is not None and mass is not None:
            density = mass / vol  # kg/m3
        else:
            density = None

        # fluid = create_fluid(species, temp, pres, density, phase)

        if density is None:
            if vol is None:
                result1 = mass / fluid.rho
            else:
                result1 = vol * fluid.rho
        elif pres is None:
            result1 = fluid.P
        else:
            result1 = fluid.T

        if phase is not None:  # saturated phase
            result2 = fluid.T
        else:
            result2 = None

        log.info("Tank Mass calculation complete")
        return mass
