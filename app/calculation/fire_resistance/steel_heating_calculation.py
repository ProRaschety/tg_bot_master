import math as m
from scipy.interpolate import interp1d

def steel_heating(self, ptm: float, temp: float, mode: str, s_0: float, s_1: float, T_0: float, t_critic: float):

    '''
    Теплотехнический расчет
    Прогрев элемента конструкции по уравнению Яковлева А.И. при тепловом воздействии по ГОСТ 30247.0 и ГОСТ Р ЕН 1363-2

    Параметры
    ----------
    ptm: float, приведенная толщина металла (m)
    temp: float, критическая температура элемента (с)
    mode: str, режим теплового воздействия (стандартный, углеводородный, наружный, тлеющий)
    s_0: float, степень черноты нагревающей среды (-)
    s_1: float, степень черноты обогреваемого элемента (-)
    T_0: float, начальная темепарутура (по умолчанию, 293.0)), (К)

    '''

    ptm = float(ptm) * 0.001
    temp = float(temp)
    t_critic = float(temp)  # 500 C = 773 K

    T_0 = 293.0
    spr = 1 / ((1 / s_0) + (1 / s_1) - 1)  # приведенная степень черноты
    x = 90 * 60  # общее время для расчета в сек
    if temp > 750.0 or mode == 'Тлеющий':
        x = 150 * 60

    # РАСЧЕТ
    Tm = []
    for i in range(x):
        if mode == 'Углеводородный':
            Tm.append((round(1080 * (1 - 0.325 * m.exp(-0.167 * (i / 60)) - 0.675 * m.exp(-2.5 * (i / 60))) + 20)))  # Углеводородный
        elif mode == 'Наружный':
            Tm.append((round(660 * (1 - 0.687 * m.exp(-0.32 * (i / 60)) - 0.313 * m.exp(-3.8 * (i / 60))) + 20)))  # Наружный
        elif mode == 'Тлеющий':
            if i <= 21 * 60:
                Tm.append((round(154 * ((i / 60) ** 0.25)) + 20))  # Тлеющий
            elif i > 21 * 60:
                Tm.append((round(345 * m.log10(8 * ((i / 60) - 20) + 1) + 20)))
        else:
            Tm.append((round(345 * m.log10(8 / 60 * i + 1) + 20)))  # Стандартный

    Tst = [T0]
    time = [0]
    temperature_element = [20]
    for i in range(1, x, 1):
        time.append(i)
        if mode == 'Углеводородный':
            Tn = 1080 * (1 - 0.325 * m.exp(-0.167 * (i / 60)) - 0.675 * m.exp(-2.5 * (i / 60))) + T0  # Углеводородный
        elif mode == 'Наружный':
            Tn = 660 * (1 - 0.687 * m.exp(-0.32 * (i / 60)) - 0.313 * m.exp(-3.8 * (i / 60))) + T0  # Наружный
        elif mode == 'Тлеющий':
            if i <= 21 * 60:
                Tn = (154 * ((i / 60) ** 0.25)) + T0  # Тлеющий
            elif i > 21 * 60:
                Tn = 345 * m.log10(8 * ((i / 60) - 20) + 1) + T0
        else:
            Tn = 345 * m.log10(8 / 60 * i + 1) + T0  # Стандартный

        an = a_convection + 5.77 * spr * (((Tn / 100) ** 4 - (Tst[i - 1] / 100) ** 4) / (Tn - Tst[i - 1]))

        Tsti = Tst[i - 1] + an * ((Tn - Tst[i - 1]) * (1 / (density_steel * ptm * (Cst + Dst * Tst[i - 1]))))
        Tst.append((Tsti))
        temperature_element.append(Tsti - 273)

    temp_fsr = interp1d(Tst, time, kind='slinear', bounds_error=False, fill_value=0)
    time_fsr = float(temp_fsr(t_critic + 273))  # Определение времени прогрева от температуры

    return Tst
