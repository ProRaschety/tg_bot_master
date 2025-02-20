import logging
import numpy as np

from scipy.stats import norm
from scipy.constants import physical_constants

from app.calculation.utilities import misc_utils


log = logging.getLogger(__name__)


def compute_fatal_probability(probit_value: int | float = 0, normal_distribution_mean=5) -> float:
    """
    Вычисляет вероятность летального исхода по значению пробита

    Параметры
    ----------
    probit_value : float
        Значение из модели probit
    normal_distribution_mean: int
        Значение по умолчанию, равное 5, позволяет избежать отрицательных значений в соответствии с опубликованными моделями

    Returns
    -------
    prob: float
        Вероятность летального исхода
    """
    return norm.cdf(probit_value, loc=normal_distribution_mean)


def get_probity_ignition(type_sub: str, temperature_flash_C: int | float = 28, mass_flow_rate: int | float = None) -> \
        tuple[float, float, float]:
    """Условная вероятность мгновенного воспламенения и воспламенения с задержкой"""
    if type_sub == 'ГГ':
        """Для горючего газа"""
        if mass_flow_rate != None:
            if mass_flow_rate < 1:
                prob_instant_ignition = 0.005
                prob_instant_ignition_delay = 0.005
                prob_comb_overpres_ignition = 0.080
            elif mass_flow_rate >= 1 and mass_flow_rate < 50:
                prob_instant_ignition = 0.035
                prob_instant_ignition_delay = 0.036
                prob_comb_overpres_ignition = 0.240
            elif mass_flow_rate >= 50:
                prob_instant_ignition = 0.150
                prob_instant_ignition_delay = 0.176
                prob_comb_overpres_ignition = 0.600
        else:
            prob_instant_ignition = 0.200
            prob_instant_ignition_delay = 0.240
            prob_comb_overpres_ignition = 0.600
    elif type_sub != 'ГГ' and temperature_flash_C > 28:
        """Для горючей и легковоспламеняющейся жидкости с Твсп > 28 C"""
        if mass_flow_rate != None:
            if mass_flow_rate < 1:
                prob_instant_ignition = 0.005
                prob_instant_ignition_delay = 0.005
                prob_comb_overpres_ignition = 0.050
            elif mass_flow_rate >= 1 and mass_flow_rate < 50:
                prob_instant_ignition = 0.015
                prob_instant_ignition_delay = 0.015
                prob_comb_overpres_ignition = 0.050
            elif mass_flow_rate >= 50:
                prob_instant_ignition = 0.040
                prob_instant_ignition_delay = 0.042
                prob_comb_overpres_ignition = 0.050
        else:
            prob_instant_ignition = 0.050
            prob_instant_ignition_delay = 0.061
            prob_comb_overpres_ignition = 0.100
    elif type_sub != 'ГГ' and temperature_flash_C <= 28:
        """Для двухфазной смеси или горючей и легковоспламеняющейся жидкости с Твсп <=28 C"""
        if mass_flow_rate != None:
            if mass_flow_rate < 1:
                prob_instant_ignition = 0.005
                prob_instant_ignition_delay = 0.005
                prob_comb_overpres_ignition = 0.080
            elif mass_flow_rate >= 1 and mass_flow_rate < 50:
                prob_instant_ignition = 0.035
                prob_instant_ignition_delay = 0.036
                prob_comb_overpres_ignition = 0.240
            elif mass_flow_rate >= 50:
                prob_instant_ignition = 0.150
                prob_instant_ignition_delay = 0.176
                prob_comb_overpres_ignition = 0.600
        else:
            prob_instant_ignition = 0.200
            prob_instant_ignition_delay = 0.240
            prob_comb_overpres_ignition = 0.600
    else:
        prob_instant_ignition = 0.200
        prob_instant_ignition_delay = 0.240
        prob_comb_overpres_ignition = 0.600

    return prob_instant_ignition, prob_instant_ignition_delay, prob_comb_overpres_ignition


"""
THERMAL Fatality Probit Models
"""


def compute_thermal_fatality_prob(heat_flux: int | float, exposure_time: int | float, model_ref: str = 'pbtp', mean=5):
    """
    Рассчитывает вероятность летального исхода от теплового источника, используя заданную пользователем модель.

    Parameters
    ----------
    model_ref : str
        ссылка на применимую функцию внутренней тепловой модели пробита (см. ниже)
    heat_flux : float
        heat flux intensity (W/m^2)
    exposure_time : float
        duration of exposure (s)
    mean : int
        Значение по умолчанию 5 позволяет избежать отрицательных значений в соответствии с опубликованными моделями.

    Returns
    -------
    prob : float
        Вероятность смертельного исхода
    """
    cleaned_id = parse_thermal_model(model_ref)
    probit_model = PROBIT_THERMAL_CHOICES[cleaned_id]

    thermal_dose = calculate_thermal_dose(heat_flux, exposure_time)

    if thermal_dose == 0:
        probit_value = -np.inf
    else:
        probit_value = probit_model(thermal_dose)
    return compute_fatal_probability(probit_value, mean)


def compute_thermal_fatality_prob_for_plot(type_accident: str, x_val: list[int], heat_flux: list[float], eff_diameter: int | float = None, mass_ball: int | float = None):
    lim_dist = misc_utils.get_distance_at_value(
        x_values=x_val, y_values=heat_flux, value=4.0)
    r0 = round(float(lim_dist), 1)
    prob_fatal = []
    if type_accident == 'fire_pool':
        radius_pool = eff_diameter / 2
        for i in x_val:
            if i <= radius_pool:
                exposure_time = 0
            elif i > r0:
                exposure_time = 0
            else:
                exposure_time = compute_effective_exposure_time(
                    type_accident=type_accident, distance=r0 - i)

            # prob = compute_thermal_fatality_prob(
            #     heat_flux=heat_flux[i], exposure_time=exposure_time)

            if i <= radius_pool:
                Qi = 1
            elif i > r0:
                Qi = 0
            else:
                Qi = compute_thermal_fatality_prob(
                    heat_flux=heat_flux[i], exposure_time=exposure_time)

            prob_fatal.append(Qi)

    else:
        for i in x_val:
            exposure_time = compute_effective_exposure_time(
                type_accident=type_accident, mass=mass_ball)

            if i > r0:
                Qi = 0
            else:
                Qi = compute_thermal_fatality_prob(
                    heat_flux=heat_flux[i], exposure_time=exposure_time)

            prob_fatal.append(Qi)

    return x_val, prob_fatal


def compute_effective_exposure_time(type_accident: str, distance: int | float = None, mass: int | float = None):
    t0 = 5  # время обнаружения пожара, с
    u = 5  # скорость движения человека, м/с
    if type_accident == 'fire_pool':
        return t0 + distance / u
    else:
        return 0.92 * (mass ** 0.303)


def calculate_thermal_dose(heat_flux: int | float, exposure_time: int | float):
    """
    Вычислить тепловую дозу за заданное время

    Parameters
    -------------
    heat_flux : float
        heat flux intensity (W/m^2)
    exposure_time : float
        duration of exposure (s)

    Returns
    ---------
    thermal_dose : float
        Thermal dose in (W/m^2)^4/3 s
    """
    return exposure_time * heat_flux ** (4/3)


def thermal_eisenberg(thermal_dose: int | float):
    """
    Eisenberg - thermal exposure

    Parameters
    -------------
    thermal_dose : float
        Thermal dose in (W/m^2)^4/3 s

    Returns
    ---------
    probit_value : float
    """
    return -38.48 + 2.56 * np.log(thermal_dose)


def thermal_tsao_perry(thermal_dose: int | float):
    """
    Tsao & Perry - thermal exposure

    Parameters
    -------------
    thermal_dose : float
        Thermal dose in (W/m^2)^4/3 s

    Returns
    ---------
    probit_value : float
    """
    return -36.38 + 2.56 * np.log(thermal_dose)


def thermal_tno(thermal_dose: int | float):
    """
    TNO - thermal exposure

    Parameters
    -------------
    thermal_dose : float
        Thermal dose in (W/m^2)^4/3 s

    Returns
    ---------
    probit_value : float
    """
    return -37.23 + 2.56 * np.log(thermal_dose)


def thermal_lees(thermal_dose: int | float):
    """
    Lees - thermal exposure

    Parameters
    -------------
    thermal_dose : float
        Thermal dose in (W/m^2)^4/3 s

    Returns
    ---------
    probit_value : float
    """
    return -29.02 + 1.99 * np.log(0.5 * thermal_dose)


def thermal_pbtp(thermal_dose: int | float):
    return -12.8 + 2.56 * np.log(thermal_dose)


"""
OVERPRESSURE Fatality Probit Models

TNO Легочное кровотечение требует массы человека, поэтому мы ее не рассчитываем.

    Модель удара всего тела TNO дает меньшие вероятности, чем модель удара головой,
    что означает, что количество смертельных исходов при ударе головой
    будет преобладать над числом погибших при ударе всего тела.
    Поэтому мы не учитываем смертельные случаи всего тела TNO.
"""


def compute_overpressure_fatality_prob(model_ref, overp, impulse=None, mean=5):
    """
    Calculate probability of fatality from overpressure using user-specified model

    Parameters
    ----------
    model_ref : str
        reference to internal probit model function to use (from available functions)
    overp : float
        Peak overpressure (Pa)
    impulse : float
        Impulse of shock wave (Pa*s)
        Not used in Eisenberg - Lung hemorrhage or HSE - Lung Hemorrhage models
    mean : int
        Default value of 5 avoids negative values, consistent with published models

    Returns
    -------
    prob : float
        Probability of fatality
    """
    cleaned_id = parse_overp_model(model_ref)
    probit_model = PROBIT_OVERP_CHOICES[cleaned_id]

    if overp == 0 or impulse == 0:
        probit_value = -np.inf
    else:
        if cleaned_id in ['leis', 'lhse']:
            probit_value = probit_model(overp=overp)
        else:
            probit_value = probit_model(overp=overp, impulse=impulse)

    return calc_fatality_probability(probit_value, mean)


def overp_eisenberg(overp):
    """
    Eisenberg - Lung hemorrhage

    Parameters
    ----------
    overp : float
        Peak overpressure (Pa)

    Returns
    -------
    probit_value : float
    """
    return -77.1 + 6.91 * np.log(overp)


def overp_hse(overp):
    """
    HSE - Lung hemorrhage

    Parameters
    ----------
    overp : float
        Peak overpressure (Pa)

    Returns
    -------
    probit_value : float
    """
    return 5.13 + 1.37 * np.log(overp * 1e-5)


def overp_tno_head(overp, impulse):
    """
    TNO - Head impact

    Parameters
    ----------
    overp : float
        Peak overpressure (Pa)
    impulse : float
        Impulse of shock wave (Pa*s)

    Returns
    -------
    probit_value : float
    """
    return 5 - 8.49 * np.log((2430 / overp) + 4.e8 / (overp * impulse))


def overp_tno_struct_collapse(overp, impulse):
    """
    TNO - Structural collapse

    Parameters
    ----------
    overp : float
        Peak overpressure (Pa)
    impulse: impulse of shock wave (Pa*s)

    Returns
    -------
    probit_value : float
    """
    return 5 - 0.22 * np.log((40000 / overp) ** 7.4 + (460 / impulse) ** 11.3)


def overp_building_collapse(overp, impulse):
    """
    TNO - Structural (Building) collapse - Обрушение здания

    Parameters
    ----------
    overp : float
        Peak overpressure (Pa)
    impulse: impulse of shock wave (Pa*s)

    Returns
    -------
    probit_value : float
    """
    S = (40000 / overp) ** 7.4 + (460 / impulse) ** 11.3
    return 5 - 0.22 * np.log(S)


def overp_major_structural_damage(overp, impulse):
    """
    Major Structural Damage - Серьезные структурные повреждения

    Parameters
    ----------
    overp : float
        Peak overpressure (Pa)
    impulse: impulse of shock wave (Pa*s)

    Returns
    -------
    probit_value : float
    """
    S = (40000 / overp) ** 7.4 + (460 / impulse) ** 11.3
    V = (17500 / overp) ** 8.4 + (290 / impulse) ** 9.3
    return 5 - 0.26 * np.log(V*S)


def overp_minor_damages(overp, impulse):
    """
    Minor Damages - Незначительные повреждения здания

    Parameters
    ----------
    overp : float
        Peak overpressure (Pa)
    impulse: impulse of shock wave (Pa*s)

    Returns
    -------
    probit_value : float
    """
    S = (40000 / overp) ** 7.4 + (460 / impulse) ** 11.3
    V = (4600 / overp) ** 3.9 + (110 / impulse) ** 5.0
    return 5 - 0.26 * np.log(V*S)


def overp_breakage_win_panes(overp):
    """
    Breakage of Window Panes - Разрушение оконных стекол

    Parameters
    ----------
    overp : float
        Peak overpressure (Pa)

    Returns
    -------
    probit_value : float
    """
    return -16.58 + 2.53 * np.log(overp * 1e-5)


# Reference to fatality models
#   key: internal reference string
#   val: function reference
PROBIT_THERMAL_CHOICES = {
    'eise': thermal_eisenberg,
    'tsao': thermal_tsao_perry,
    'tno': thermal_tno,
    'lees': thermal_lees,
    'pbtp': thermal_pbtp
}

# Reference to overpressure models
#   key: internal reference string
#   val: function reference
# Note: keys are unique with above dict to ensure no accidental overlap
PROBIT_OVERP_CHOICES = {
    'leis': overp_eisenberg,
    'lhse': overp_hse,
    'head': overp_tno_head,
    'coll': overp_tno_struct_collapse,
}


def parse_thermal_model(name):
    """ Determine model ID from string name """
    # parsed = re.sub(r'\W+', '', name.lower())
    cleaned = misc_utils.clean_name(name)  # alphanumeric lower-case

    if cleaned in ['eise', 'eisenberg', 'eis', 'eisen']:
        model_id = 'eise'
    elif cleaned in ['tsao', 'tsa']:
        model_id = 'tsao'
    elif cleaned in ['tno', 'tn']:
        model_id = 'tno'
    elif cleaned in ['lees', 'lee', 'le']:
        model_id = 'lees'
    elif cleaned in ['pbtp', 'pbt', 'pb']:
        model_id = 'pbtp'
    else:
        raise ValueError(
            "Thermal model name {} not recognized".format(cleaned))

    return model_id


def parse_overp_model(name):
    """ Determine model ID from string name """
    cleaned = misc_utils.clean_name(name)  # alphanumeric lower-case

    if cleaned in ['leis', 'lung_eisenberg', 'lungeisenberg', 'lunge', 'lung_eis', 'elh']:
        model_id = 'leis'
    elif cleaned in ['lhse', 'lung_hse', 'lunghse', 'lungh', 'lhs']:
        model_id = 'lhse'
    elif cleaned in ['head_impact', 'head', 'headimpact', 'hea']:
        model_id = 'head'
    elif cleaned in ['col', 'collapse', 'coll']:
        model_id = 'coll'
    else:
        raise ValueError(
            "Probit overpressure model name {} not recognized".format(cleaned))

    return model_id


def get_probit_overpressure_mix():
    pass
