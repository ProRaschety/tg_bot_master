import logging
import io
import json

import math as m
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from scipy.constants import physical_constants
from scipy.interpolate import RectBivariateSpline, interp1d


from app.calculation.physics.physics_utils import compute_stoichiometric_coefficient_with_oxygen, compute_density_gas_phase

log = logging.getLogger(__name__)


class AccidentParameters:
    def __init__(self, type_accident: str | None = None) -> None:
        self.type_accident = type_accident
        self.pressure_ambient = physical_constants.get(
            'standard atmosphere')[0]  # Па
        self.heat_capacity_air = 1010  # Дж/кг*К
        self.R = physical_constants.get('molar gas constant')[0]  # Дж/моль*К
        self.K = 273.15  # К
        self.g = physical_constants.get('standard acceleration of gravity')[0]
        self.sound_speed = 340
        self.heat_burn_specific = 44094000  # Дж/кг

    def compute_radius_LFL(self, density: int | float, mass: int | float, clfl: int | float):
        return 7.80 * (mass / (density * clfl)) ** 0.33

    def compute_height_LFL(self, density: int | float, mass: int | float, clfl: int | float):
        return 0.26 * (mass / (density * clfl)) ** 0.33

    def compute_overpres_inopen(self,
                                reduced_mass: int | float,
                                distance_run: bool = False,
                                distance: int | float = None,
                                ):
        """форм.(В.14) и (В.22) СП12 и форм.(П3.47) М404"""
        if distance_run:
            x_lim = int(distance * 2)
            dist = []
            overpres = []
            impuls = []
            for x in range(1, x_lim + 5, 1):
                dist.append(x)
                pi_1 = (0.8 * (reduced_mass ** 0.33)) / x
                pi_2 = (3.0 * (reduced_mass ** 0.66)) / x ** 2
                pi_3 = (5.0 * reduced_mass) / x ** 3
                overpres_inopen = self.pressure_ambient * (pi_1 + pi_2 + pi_3)
                overpres.append(overpres_inopen)
                impuls_inopen = (123 * reduced_mass) / x
                impuls.append(impuls_inopen)
            return overpres, impuls, dist
        else:
            pi_1 = (0.8 * (reduced_mass ** 0.33)) / distance
            pi_2 = (3.0 * (reduced_mass ** 0.66)) / distance ** 2
            pi_3 = (5.0 * reduced_mass) / distance ** 3
            overpres = self.pressure_ambient * (pi_1 + pi_2 + pi_3)
            impuls = (123 * reduced_mass) / distance
            return overpres, impuls

    def _compute_nondim_pressure_detonation(self, nondim_distance: int | float, new_methodology: bool = False):
        if new_methodology:
            if nondim_distance > 0.2 and nondim_distance < 50:
                px = m.exp(-0.9278 - 1.5415 * m.log(nondim_distance) + 0.1953 *
                           (m.log(nondim_distance) ** 2) - 0.4818 * (m.log(nondim_distance) ** 3))
            else:
                px = 18.6
        else:
            if nondim_distance > 0.2:
                px = m.exp(-1.124 - 1.66 * m.log(nondim_distance) +
                           0.260 * (m.log(nondim_distance) ** 2))
            else:
                px = 18
        return px

    def _compute_nondim_impuls_detonation(self, nondim_distance: int | float, new_methodology: bool = False):
        if new_methodology:
            if nondim_distance > 0.2 and nondim_distance < 50:
                if nondim_distance > 0.2 and nondim_distance < 0.8:
                    ix = m.exp(-3.3228 - 1.3689 * m.log(nondim_distance) - 0.9057 * (
                        m.log(nondim_distance) ** 2) - 0.4818 * (m.log(nondim_distance) ** 3))
                else:
                    ix = m.exp(-3.2656 - 0.9641 * m.log(nondim_distance) - 0.0108 * (
                        m.log(nondim_distance) ** 2) - 0.4818 * (m.log(nondim_distance) ** 3))
            else:
                ix = 0.53
        else:
            if nondim_distance > 0.2:
                ix = m.exp(-3.4217 - 0.898 * m.log(nondim_distance) -
                           0.0096 * (m.log(nondim_distance) ** 2))
            else:
                ix = m.exp(-3.4217 - 0.898 * m.log(0.14) -
                           0.0096 * (m.log(0.14) ** 2))
        return ix

    def _compute_nondim_pressure_deflagration(self, nondim_distance: int | float, front: int | float,  sigma: int):
        sigma_st = (front ** 2) / (self.sound_speed ** 2)
        sigma_nd = (sigma - 1) / sigma
        px = sigma_st * sigma_nd * ((0.83 / nondim_distance) - (0.14 / nondim_distance ** 2)) if nondim_distance > 0.34\
            else sigma_st * sigma_nd * ((0.83 / 0.34) - (0.14 / 0.34 ** 2))
        return px

    def _compute_nondim_impuls_deflagration(self, nondim_distance: int | float, front: int | float,  sigma: int):
        sigma_nd = (sigma - 1) / sigma
        w = (front / self.sound_speed) * sigma_nd
        ix = w * (1 - 0.4 * w) * ((0.06 / nondim_distance) + (0.01 / nondim_distance ** 2) - (0.0025 / nondim_distance ** 3)) if nondim_distance > 0.34 else w * (
            1 - 0.4 * w) * ((0.06 / 0.34) + (0.01 / 0.34 ** 2) - (0.0025 / 0.34 ** 3))
        return ix

    def compute_overpres_inclosed(self,
                                  energy_reserve: int | float,
                                  mode_explosion: int | None = None,
                                  distance_run: bool = False,
                                  distance: int | float = None,
                                  subst: str = 'gas',
                                  ufront: int | float = 500,
                                  new_methodology: bool = False
                                  ):
        """форм. (П3.39-П3.46) М404"""
        if distance_run:
            x_lim = int(distance * 2)
            dist = []
            overpres = []
            impuls = []
            if mode_explosion == 1:
                if new_methodology:
                    for x in range(1, x_lim + 1, 1):
                        dist.append(x)
                        rx = x / \
                            ((energy_reserve / self.pressure_ambient) ** 0.33333)
                        px = self._compute_nondim_pressure_detonation(
                            nondim_distance=rx, new_methodology=True)
                        ix = self._compute_nondim_impuls_detonation(
                            nondim_distance=rx, new_methodology=True)
                        overpres_inclosed = self.pressure_ambient * px
                        impuls_inclosed = ix * \
                            (self.pressure_ambient ** 0.66666) * \
                            ((energy_reserve ** 0.33333) / self.sound_speed)

                        overpres.append(overpres_inclosed)
                        impuls.append(impuls_inclosed)
                else:
                    for x in range(1, x_lim + 1, 1):
                        dist.append(x)

                        rx = x / \
                            ((energy_reserve / self.pressure_ambient) ** 0.33333)
                        px = self._compute_nondim_pressure_detonation(
                            nondim_distance=rx)
                        ix = self._compute_nondim_impuls_detonation(
                            nondim_distance=rx)

                        overpres_inclosed = self.pressure_ambient * px
                        impuls_inclosed = ix * \
                            (self.pressure_ambient ** 0.66666) * \
                            ((energy_reserve ** 0.33333) / self.sound_speed)

                        overpres.append(overpres_inclosed)
                        impuls.append(impuls_inclosed)

            else:
                sigma = 7.0 if subst == 'gas' else 4.0
                sigma_nd = (sigma - 1) / sigma
                energy_res = energy_reserve if subst == 'gas' else energy_reserve * sigma_nd
                if new_methodology:
                    for x in range(1, x_lim + 1, 1):
                        dist.append(x)
                        rx = x / \
                            ((energy_res / self.pressure_ambient) ** 0.33333)
                        px_defl = self._compute_nondim_pressure_deflagration(
                            nondim_distance=rx, front=ufront, sigma=sigma)
                        px_detn = self._compute_nondim_pressure_detonation(
                            nondim_distance=rx, new_methodology=True)
                        # px = min(self._compute_nondim_pressure_deflagration(nondim_distance=rx, front=ufront, sigma=sigma),
                        #          self._compute_nondim_pressure_detonation(nondim_distance=rx, new_methodology=True))
                        # log.info(f"Pdefl: {px_defl}, Pdetn: {px_detn}")
                        px = min(px_defl, px_detn)
                        overpres_inclosed = self.pressure_ambient * px
                        ix = min(self._compute_nondim_impuls_deflagration(nondim_distance=rx, front=ufront, sigma=sigma), self._compute_nondim_impuls_detonation(
                            nondim_distance=rx, new_methodology=True))
                        impuls_inclosed = ix * \
                            (self.pressure_ambient ** 0.66666) * \
                            ((energy_res ** 0.33333) / self.sound_speed)
                        overpres.append(overpres_inclosed)
                        impuls.append(impuls_inclosed)
                else:
                    for x in range(1, x_lim + 1, 1):
                        dist.append(x)
                        rx = x / \
                            ((energy_res / self.pressure_ambient) ** 0.33333)
                        px = self._compute_nondim_pressure_deflagration(
                            nondim_distance=rx, front=ufront, sigma=sigma)
                        overpres_inclosed = self.pressure_ambient * px
                        ix = self._compute_nondim_impuls_deflagration(
                            nondim_distance=rx, front=ufront, sigma=sigma)
                        impuls_inclosed = ix * \
                            (self.pressure_ambient ** 0.66666) * \
                            ((energy_res ** 0.33333) / self.sound_speed)
                        overpres.append(overpres_inclosed)
                        impuls.append(impuls_inclosed)

            return dist, overpres, impuls

        else:
            if mode_explosion == 1:
                rx = distance / \
                    ((energy_reserve / self.pressure_ambient) ** 0.33333)
                if new_methodology:
                    px = self._compute_nondim_pressure_detonation(
                        nondim_distance=rx, new_methodology=True)
                    ix = self._compute_nondim_impuls_detonation(
                        nondim_distance=rx, new_methodology=True)
                else:
                    px = self._compute_nondim_pressure_detonation(
                        nondim_distance=rx)
                    ix = self._compute_nondim_impuls_detonation(
                        nondim_distance=rx)
                overpres = self.pressure_ambient * px
                impuls = ix * \
                    (self.pressure_ambient ** 0.66666) * \
                    ((energy_reserve ** 0.33333) / self.sound_speed)

            else:
                sigma = 7.0 if subst == 'gas' else 4.0
                sigma_nd = (sigma - 1) / sigma
                energy_res = energy_reserve if subst == 'gas' else energy_reserve * sigma_nd
                rx = distance / \
                    ((energy_res / self.pressure_ambient) ** 0.33333)
                if new_methodology:
                    px_defl = self._compute_nondim_pressure_deflagration(
                        nondim_distance=rx, front=ufront, sigma=sigma)
                    px_detn = self._compute_nondim_pressure_detonation(
                        nondim_distance=rx, new_methodology=True)
                    log.info(f"Pdefl: {px_defl}, Pdetn: {px_detn}")
                    px = min(self._compute_nondim_pressure_deflagration(nondim_distance=rx, front=ufront, sigma=sigma),
                             self._compute_nondim_pressure_detonation(nondim_distance=rx, new_methodology=True))
                    overpres = self.pressure_ambient * px
                    ix = min(self._compute_nondim_impuls_deflagration(nondim_distance=rx, front=ufront, sigma=sigma), self._compute_nondim_impuls_detonation(
                        nondim_distance=rx, new_methodology=True))
                    impuls = ix * \
                        (self.pressure_ambient ** 0.66666) * \
                        ((energy_res ** 0.33333) / self.sound_speed)

                else:
                    px = self._compute_nondim_pressure_deflagration(
                        nondim_distance=rx, front=ufront, sigma=sigma)
                    overpres = self.pressure_ambient * px
                    ix = self._compute_nondim_impuls_deflagration(
                        nondim_distance=rx, front=ufront, sigma=sigma)
                    impuls = ix * \
                        (self.pressure_ambient ** 0.66666) * \
                        ((energy_res ** 0.33333) / self.sound_speed)

            return rx, px, overpres, ix, impuls

    def compute_redused_mass(self, expl_energy: int | float):
        return (expl_energy / 4.52) / 1_000_000

    def compute_expl_energy(self, k: int | float, Cp: int | float, mass: int | float, temp_liquid: int | float, boiling_point: int | float):
        return k * Cp * mass * (temp_liquid - (boiling_point + self.K))

    def compute_nonvelocity(self, wind: int | float, density_fuel: int | float, mass_burn_rate: int | float, eff_diameter: int | float):
        return wind / (np.cbrt((mass_burn_rate * self.g * eff_diameter) / density_fuel))

    def get_flame_deflection_angle(self, nonvelocity: int | float):
        if nonvelocity > 1:
            eta = m.acos(nonvelocity ** -0.5)
        else:
            eta = m.acos(1)
        angle = float(m.degrees(eta))
        return angle

    def compute_lenght_flame_pool(self, nonvelocity: int | float, density_air: int | float, mass_burn_rate: int | float, eff_diameter: int | float):
        if nonvelocity < 1:
            lenght_flame = 42 * eff_diameter * \
                (mass_burn_rate / (density_air * m.sqrt(self.g * eff_diameter))) ** 0.61
        else:
            lenght_flame = 55 * eff_diameter * \
                ((mass_burn_rate / (density_air * m.sqrt(self.g * eff_diameter)))
                 ** 0.67) * nonvelocity ** -0.21
        return lenght_flame

    def compute_surface_emissive_power(self, eff_diameter: int | float, subst: str, heat_of_comb: int | float = None, lenght_flame: int | float = None, mass_burning_rate: int | float = None):
        if heat_of_comb == None:
            if eff_diameter <= 10:
                if subst == 'gasoline':
                    sep = 60
                elif subst == 'diesel':
                    sep = 40
                elif subst == 'LNG':
                    sep = 220
                elif subst == 'LPG':
                    sep = 80
                elif subst == 'liq_hydrogen':
                    sep = 150
            elif 10 < eff_diameter < 50:
                if subst == 'gasoline':
                    sep_1 = interp1d([1, 10, 20, 30, 40, 50], [
                        60, 60, 47, 35, 28, 25], 'linear')  # Бензин
                    sep = sep_1(eff_diameter)
                    # sep = round(0.0179 * eff_diameter ** 2 - 1.9614 * eff_diameter + 78.2, 2)
                elif subst == 'diesel':
                    sep_2 = interp1d([1, 10, 20, 30, 40, 50], [
                        40, 40, 32, 25, 21, 18], 'linear')  # ДТ
                    sep = sep_2(eff_diameter)
                    # sep = round(0.0179 * eff_diameter ** 2 - 1.9614 * eff_diameter + 78.2, 2)
                elif subst == 'LNG':
                    sep_3 = interp1d([1, 10, 20, 30, 40, 50], [220, 220, 180, 150, 130, 120],
                                     'linear')  # СПГ ГОСТ Р 57431-2017
                    sep = sep_3(eff_diameter)
                elif subst == 'LPG':
                    sep_4 = interp1d([1, 10, 20, 30, 40, 50], [
                        80, 80, 63, 50, 43, 40], 'linear')  # СУГ
                    sep = sep_4(eff_diameter)
                elif subst == 'liq_hydrogen':
                    sep_5 = interp1d([1, 10, 20, 30, 40, 50], [
                        150, 150, 120, 100, 90, 80], 'linear')  # Сжиженный водород
                    sep = sep_5(eff_diameter)
            elif eff_diameter >= 50:
                if subst == 'gasoline':
                    sep = 25
                elif subst == 'diesel':
                    sep = 18
                elif subst == 'LNG':
                    sep = 120
                elif subst == 'LPG':
                    sep = 40
                elif subst == 'liq_hydrogen':
                    sep = 80
            else:
                # для нефти и нефтепродуктов по ГОСТ 1510-2022
                sep = 140 * m.exp(-0.12 * eff_diameter) + 20 * \
                    (1 - m.exp(-0.12 * eff_diameter))
        else:
            sep = (0.4 * mass_burning_rate * heat_of_comb) / \
                (1 + 4 * (lenght_flame / eff_diameter))
        return sep

    def compute_mass_burning_rate(self, subst: str = None, heat_of_comb: int | float = None, Lg: int | float = None, Cp: int | float = None, Tb: int | float = None, Ta: int | float = None):
        if heat_of_comb == None:
            if subst == 'gasoline':
                m = 0.06
            elif subst == 'diesel':
                m = 0.04
            elif subst == 'LNG':
                m = 0.08
            elif subst == 'LPG':
                m = 0.10
            elif subst == 'liq_hydrogen':
                m = 0.17
        else:
            m = (0.001 * heat_of_comb) / (Lg + Cp * (Tb - Ta))
        return m

    def compute_heat_flux(self, eff_diameter: int | float, lenght_flame: int | float, sep: int | float = 200, angle: int | float = 0):
        # Определение интенсивности теплового излучения, кВт/м2
        # расстояние от центра лужи для расчета
        if sep != 200:
            x_lim = int(eff_diameter + lenght_flame * 5)
        else:
            x_lim = int(eff_diameter + lenght_flame * 1.5)

        x_values = []
        qf = []
        for r in range(0, x_lim, 1):
            x_values.append(r)
            if r < 1 + eff_diameter * 0.5:
                qf_f = sep
            else:
                a = 2 * lenght_flame / eff_diameter
                b = 2 * r / eff_diameter

                A = m.sqrt(a ** 2 + (b + 1) ** 2 - 2 *
                           a * (b + 1) * m.sin(angle))
                B = m.sqrt(a ** 2 + (b - 1) ** 2 - 2 *
                           a * (b - 1) * m.sin(angle))
                C = m.sqrt(1 + ((b ** 2) - 1) * m.cos(angle) ** 2)
                D = m.sqrt((b - 1) / (b + 1))
                E = (a * m.cos(angle)) / (b - a * m.sin(angle))
                F = m.sqrt(b ** 2 - 1)
                Fv = (1 / 3.14) * \
                     (-E * m.atan(D) + E * ((a ** 2 + (b + 1) ** 2 - 2 * b * (1 + a * m.sin(angle))) / (A * B)) * m.atan(
                         (A * D) / B) + (m.cos(angle) / C) * (m.atan((a * b - F ** 2 * m.sin(angle)) / (F * C)) +
                                                              m.atan((F ** 2 * m.sin(angle)) / (F * C))))
                Fh = (1 / 3.14) * \
                     ((m.atan(1 / D)) +
                      (m.sin(angle) / C) *
                      (m.atan((a * b - F ** 2 * m.sin(angle)) / (F * C)) +
                       m.atan((F ** 2 * m.sin(angle)) / (F * C))) -
                      ((a ** 2 + (b + 1) ** 2 - 2 * (b + 1 + a * b * m.sin(angle))) / (A * B)) *
                      m.atan((A * D) / B))

                Fq = m.sqrt(Fv ** 2 + Fh ** 2)  # коэффициент облученности
                # коэффициент пропускания атмосферы
                t = m.exp(-0.0007 * (r - 0.5 * eff_diameter))
                qf_f = float(sep * Fq * t)  # интенсивность теплового излучения

            qf.append(qf_f)

        return x_values, qf

    def compute_fire_ball_diameter(self, mass: int | float):
        return 6.48 * (mass ** 0.325)

    def compute_fire_ball_existence_time(self, mass: int | float):
        return 0.852 * (mass ** 0.260)

    def compute_fire_ball_view_factor(self, eff_diameter: int | float,
                                      height: int | float,
                                      distance: int | float):
        return (eff_diameter ** 2) / (4 * (height ** 2 + distance ** 2))

    def compute_fire_ball_atmospheric_transmittance(self, eff_diameter: int | float,
                                                    height: int | float,
                                                    distance: int | float):
        return m.exp((-7.0 * 0.0001) * (m.sqrt(height ** 2 + distance ** 2) - (eff_diameter / 2)))

    def compute_heat_flux_fire_ball(self, diameter_ball: int | float, height: int | float, sep: int | float):
        # Определение интенсивности теплового излучения, кВт/м2
        # расстояние от центра огненного шара

        x_lim = int(height * 6)
        x_values = []
        qf = []
        for r in range(0, x_lim, 1):
            x_values.append(r)
            # коэффициент облученности
            Fq = diameter_ball ** 2 / (4 * (height ** 2 + r ** 2))
            # коэффициент пропускания атмосферы
            t = m.exp((-7.0 * 0.0001) *
                      (m.sqrt(height ** 2 + r ** 2) - (diameter_ball / 2)))
            qf_f = float(sep * Fq * t)  # интенсивность теплового излучения

            qf.append(qf_f)

        return x_values, qf

    def compute_heat_jet_fire(self, lenght_flame: int | float, diameter: int | float = 0):
        # Определение интенсивности теплового излучения, кВт/м2
        # расстояние от источника истечения вещества
        x_lim = int(lenght_flame * 2.5)
        x_values = []
        qf = []
        for r in range(0, x_lim, 1):
            x_values.append(r)
            if r < lenght_flame * 1.5:
                if r > lenght_flame and r <= lenght_flame * 1.5:
                    qf_f = 10.0
                else:
                    qf_f = 200  # интенсивность теплового излучения
            else:
                qf_f = 0
            qf.append(qf_f)
        return x_values, qf

    def get_mode_explosion(self, class_fuel: int = 1, class_space: int = 1):
        data_mode = np.array([[1, 1, 2, 3],
                              [1, 2, 3, 4],
                              [2, 3, 4, 5],
                              [3, 4, 5, 6]])
        mode_explosion = data_mode[class_fuel - 1, class_space - 1]
        return mode_explosion

    def compute_eff_energy_reserve(self, phi_fuel: int | float, phi_stc: int | float, mass_gas_phase: int | float, subst: str = 'gas', explosion_superficial: bool = False):
        """Эффективный энергозапас горючей смеси Е"""
        sigma = 7.0 if subst == 'gas' else 4.0
        if subst == 'gas':
            energy_reserve = mass_gas_phase * self.heat_burn_specific if phi_fuel <= phi_stc else mass_gas_phase * \
                self.heat_burn_specific * (phi_stc / phi_fuel)
        else:
            energy_reserve = ((sigma - 1) / sigma) * mass_gas_phase * self.heat_burn_specific if phi_fuel <= phi_stc else (
                (sigma - 1) / sigma) * mass_gas_phase * self.heat_burn_specific * (phi_stc / phi_fuel)

        return energy_reserve * 2 if explosion_superficial else energy_reserve

    def compute_nondimensional_distance(self, distance: int | float, energy_reserve: int | float):
        return distance / ((energy_reserve/self.pressure_ambient) ** (1/3))

    def compute_velocity_flame(self, mass_gas_phase: int | float, cloud_combustion_mode: int = 1):
        # скорость фронта пламени
        k1 = 43.0
        k2 = 26.0
        u_front = k1 * mass_gas_phase ** 0.1666
        if cloud_combustion_mode == 6:
            u_front = k2 * mass_gas_phase ** 0.1666
        elif cloud_combustion_mode == 5:
            u_front = k1 * mass_gas_phase ** 0.1666
        elif cloud_combustion_mode == 4:
            if u_front > 200:
                u_front = k1 * mass_gas_phase ** 0.1666
            else:
                u_front = 200
        elif cloud_combustion_mode == 3:
            if u_front > 300:
                u_front = k1 * mass_gas_phase ** 0.1666
            else:
                u_front = 300
        elif cloud_combustion_mode == 2:
            if u_front > 500:
                u_front = k1 * mass_gas_phase ** 0.1666
            else:
                u_front = 500
        else:
            u_front = 0
        # log.info(f"u: {u_front:.1f}")
        return u_front

    def get_distance_at_sep(self, x_values, y_values, sep):
        func_sep = interp1d(y_values, x_values, kind='linear',
                            bounds_error=False, fill_value=0)
        return func_sep(sep)

    def get_sep_at_distance(self, x_values, y_values, distance):
        func_distance = interp1d(x_values, y_values, kind='linear',
                                 bounds_error=False, fill_value=0)
        return func_distance(distance)

    def get_coefficient_eta(self, velocity_air_flow: int | float = 0, temperature_air: int | float = None):

        x_temp = [10.0, 15.0, 20.0, 30.0, 35.0]
        y_vel = [0.0, 0.1, 0.2, 0.5, 1.0]
        eta = np.array([(1.0, 1.0, 1.0, 1.0, 1.0),
                        (3.0, 2.6, 2.4, 1.8, 1.6),
                        (4.6, 3.8, 3.5, 2.4, 2.3),
                        (6.6, 5.7, 5.4, 3.6, 3.2),
                        (10.0, 8.7, 7.7, 5.6, 4.6)])
        f_eta = RectBivariateSpline(x_temp, y_vel, eta.T, kx=4, ky=4, s=1)
        eta = f_eta(temperature_air, velocity_air_flow)
        log.info(
            f"При температуре: {temperature_air} и скорости: {velocity_air_flow}, eta: {eta[-1][-1]:.2f}")
        return eta[-1][-1]

    def calc_evaporation_intencity_liquid(self, eta: int | float, molar_mass: int | float, vapor_pressure: int | float):
        """Возвращает интенсивность испарения паров жидкости"""
        return 10 ** -6 * eta * m.sqrt(molar_mass) * vapor_pressure

    # def calc_saturated_vapor_pressure(self, temperature: int | float = None, a: int | float, b: int | float, ca: int | float):
    #     """Возвращает давление насыщенных паров в кПа при заданной температуре в С"""
    #     return 10 ** (a - (b / (temperature + ca)))

    def calc_concentration_saturated_vapors_at_temperature(self, vapor_pressure: int | float):
        return 100 * vapor_pressure / self.pressure_ambient * 0.001  # kPa
