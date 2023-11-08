import math as m
from scipy.interpolate import interp1d
from app.calculation.fire_resistance.fire_mode import run_fire_mode


def steel_heating(
        ptm=5.0,
        mode='Стандартный',
        s_0=0.85,
        s_1=0.625,
        T_0=293.0,
        t_critic=500.0,
        xlim=90,
        a_convection=29.0,
        density_steel=7800.0,
        heat_capacity=310.0,
        heat_capacity_change=0.469):
    '''
    Теплотехнический расчет
    Прогрев элемента конструкции по уравнению Яковлева А.И. при тепловом воздействии по ГОСТ 30247.0 и ГОСТ Р ЕН 1363-2

    Параметры
    ----------
    ptm: float, приведенная толщина металла (m)
    mode: str, режим теплового воздействия (стандартный, углеводородный, наружный, тлеющий)
    s_0: float, степень черноты нагревающей среды (-)
    s_1: float, степень черноты обогреваемого элемента (-)
    T_0: float, начальная темепарутура (по умолчанию, 293.0)), (К)
    t_critic: float, критическая температура элемента (C)

    '''

    ptm = ptm * 0.001
    t_critic = t_critic  # 500 C = 773 K
    a_convection = a_convection
    density_steel = density_steel
    Cst = heat_capacity
    Dst = heat_capacity_change

    T0 = T_0
    spr = 1 / ((1 / s_0) + (1 / s_1) - 1)  # приведенная степень черноты
    x = xlim * 60  # общее время для расчета в сек
    if t_critic > 750.0 or mode == 'Тлеющий':
        x = 150 * 60

    # РАСЧЕТ
    Tst = [T0]
    time = [0]
    temperature_element = [20]
    # Tm = run_fire_mode(mode=mode, time=x)

    for i in range(1, x, 1):
        time.append(i)

        if mode == 'Углеводородный':
            Tn = 1080 * (1 - 0.325 * m.exp(-0.167 * (i / 60)) -
                         0.675 * m.exp(-2.5 * (i / 60))) + T0  # Углеводородный
        elif mode == 'Наружный':
            Tn = 660 * (1 - 0.687 * m.exp(-0.32 * (i / 60)) -
                        0.313 * m.exp(-3.8 * (i / 60))) + T0  # Наружный
        elif mode == 'Тлеющий':
            if i <= 21 * 60:
                Tn = (154 * ((i / 60) ** 0.25)) + T0  # Тлеющий
            elif i > 21 * 60:
                Tn = 345 * m.log10(8 * ((i / 60) - 20) + 1) + T0
        else:
            Tn = 345 * m.log10(8 / 60 * i + 1) + T0  # Стандартный

        an = a_convection + 5.77 * spr * \
            (((Tn / 100) ** 4 - (Tst[i - 1] / 100) ** 4) / (Tn - Tst[i - 1]))

        Tsti = Tst[i - 1] + an * ((Tn - Tst[i - 1]) * (1 /
                                  (density_steel * ptm * (Cst + Dst * Tst[i - 1]))))
        Tst.append((Tsti))
        temperature_element.append(Tsti - 273)

    temp_fsr = interp1d(Tst, time, kind='slinear',
                        bounds_error=False, fill_value=0)
    # Определение времени прогрева от температуры
    time_fsr = round(float(temp_fsr(t_critic + 273))/60, 1)

    # print()
    return time_fsr
