import math
import json

from scipy import constants as const


class OutFlowGas:
    pass


class OutFlowLiquid:
    def __init__(self, chat_id=None):
        self.chat_id: int = chat_id

    # Исходные данные:
    p_atm = 101325
    mu = 0.62  # Коэффициент истечения (Зависит от вида отверстия)

    # t_atm = 298.15  # Та — температура окружающего воздуха, К = 298,15
    # p_s = 17.499  # давление насыщенного пара, кПа

    # площадь отверстия истечения, м2
    hole_area = round((3.1415 * hole_diameter ** 2) / 4, 4)
    a_equip = volume_vessel / height_vessel  # площадь сечения резервуара, м2
    # Масса жидкости в резервуаре, кг
    initial_mass = round(fill_factor * volume_vessel * density_liq, 3)
    V_0 = initial_mass / density_liq  # Начальный объем жидкости в резервуаре, м3
    h_0 = V_0 / a_equip  # Начальный уровень жидкости в резервуаре, м

    # столб жидкости в резервуаре, м
    initial_height_liquid = round(fill_factor * height_vessel, 3)
    # h_hol = 1  # высота расположения отверстия от днища, м
    # hi_hol = h_liq0 - h_hol  # Высота столба жидкости над отверстием, м
    initial_pressure_in_vessel = round(
        density_liq * 9.81 * initial_height_liquid + p_atm, 1)  # Давление в оборудовании, Па
    initial_mass_flow = round(mu * hole_area * (2 * (initial_pressure_in_vessel - p_atm) * density_liq) ** 0.5,
                              3)  # начальный массовый расход, кг/с
    initial_volume_flow = round(initial_mass_flow / density_liq, 3)

    max_range = int(volume_vessel / initial_volume_flow)
    delta_t = max_range / 60

    # print(max_range, delta_t)

    # масса жидкости в резервуаре в момент времни t, кг (M(0)-dMi)
    m_equip = [initial_mass]
    t_i = []  # шаг по времени, с
    fill_f = []  # степень заполнения, -
    h_liq = []  # высота столба жидкости над отверстием, м
    p_stat = []  # гидростатичесое давление в момент времени t, Па
    G_t = []  # массовый расход жидкости в момент времени t, кг/с
    delta_m = [0]  # масса идкости вышедшее из резервуара за время t, кг
    total_m = [0]  # общая масса вышедшее из оборудования, кг (dMi-1+dMi)
    velocity_outflow = []

    for t in range(0, max_range, 1):
        if t == 0:
            fi = m_equip[t] / (volume_vessel * density_liq)
            h_liq_i = fi * height_vessel
            p_equip = density_liq * 9.81 * h_liq_i + p_atm
            G_i = round(mu * hole_area *
                        (2 * (p_equip - p_atm) * density_liq) ** 0.5, 4)
            delta_m_i = G_i * delta_t
            # h_i = h_liq_i * (m_equip[-1] - delta_m_i) / m_equip[-1]
        elif t > 0:
            fi = m_equip[-1] / (volume_vessel * density_liq)
            h_liq_i = fi * height_vessel
            p_equip = density_liq * 9.81 * h_liq_i + p_atm
            if float(p_equip) > p_atm:
                G_i = round(mu * hole_area *
                            (2 * (p_equip - p_atm) * density_liq) ** 0.5, 3)
                delta_m_i = G_i * delta_t
                # скорость истечения (м/с) по формуле Торричелли
                velocity_outflow.append(math.sqrt(2 * 9.81 * h_liq_i))

                # длина струи жидкости, м
                lenght_jet = math.sqrt(
                    (2 * 9.81 * h_liq_i) * 2 * (height_vessel - h_liq_i))
                # h_i = h_liq_i * (m_equip[-1] - delta_m_i) / m_equip[-1]
                # print(velocity_outflow[-1], lenght_jet)
            else:
                break
        else:
            break

        # print(f't(с) = {"%4.3f" % (t * delta_t)}, '
        #       f'M(kg) = {"%4.3f" % (m_equip[-1])}, '
        #       f'fi(-) = {"%4.4f" % (fi)}, '
        #       f'h(м) = {"%4.3f" % (h_liq_i)}, '
        #       f'P(Па) = {"%4.3f" % (p_equip)}, '
        #       f'dM(kg) = {"%4.3f" % (delta_m_i)}, '
        #       f'G(кг/с) = {"%2.3f" % (G_i)}, '
        #       f'G(м3/с)= {"%2.3f" % ((G_i / density_liq))}, '
        #       f'M_leaking(кг) = {"%4.3f" % (delta_m[t] + delta_m_i)}, ')

        m_equip.append(m_equip[t] - delta_m_i)
        t_i.append(t * delta_t)
        fill_f.append(fi)
        p_stat.append(p_equip)
        G_t.append(G_i)
        delta_m.append(delta_m_i)
        total_m.append(delta_m[t] + delta_m_i)

    # размеры рисунка в дюймах, 1 дюйм = 2,54 см
    inch = 2.54
    w = 20
    h = 20
    fig = plt.figure(figsize=(w / inch, h / inch))
    fsize = 16
    plt.style.use('classic')
    plt.rcParams["font.family"] = 'fantasy'
    plt.rcParams["font.fantasy"] = 'Arial'
    plt.rcParams["axes.labelsize"] = fsize
    plt.rcParams["xtick.labelsize"] = 14
    plt.rcParams["ytick.labelsize"] = 14

    ax = fig.add_subplot(1, 1, 1)
    ax.plot(t_i, G_t, '-', linewidth=4, color=(1, 0, 0, 0.8))
    # ax.plot(rr, qf, '-', linewidth=4, color=(1, 0, 0, 0.8))

    ax.set_xlim(0, max(t_i) * 1.05)
    ax.set_ylim(0, max(G_t) * 1.05)
    ax.set_xlabel(r"Время, с")
    set_y_label = str(f'Массовый расход жидкости, кг/с')
    ax.set_ylabel(f"{set_y_label}")

    plt.title(f'График массового расхода жидкости', fontsize=18)
    # plt.legend(fontsize=10, framealpha=0.95, facecolor="w", loc=1)
    ax.grid(visible=True, which='major', axis='both', color=(
        0.9, 0.1, 0, 0.8), linestyle='--', linewidth=0.15)

    fig.savefig(
        f"temp_file/fig_outflow_liquid_{callback_data.message.chat.id}.png", dpi=150)

    # КОНЕЦ РАСЧЕТА
