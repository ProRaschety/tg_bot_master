import matplotlib.pyplot as plt


def plotting_fire_resistance(chat_id, mode, time, temp, time_fsr=15, t_critic=500):
    # График изменения температуры во времени
    # размеры рисунка в дюймах, 1 дюйм = 2,54 см
    print(f'Tm={temp}, chat_id={chat_id}')
    # inch = 2.54
    # w = 20
    # h = 20
    # fig = plt.figure(figsize=(w/inch, h/inch))
    # fsize = 16
    # plt.style.use('classic')
    # ax = fig.add_subplot(1, 1, 1)

    # x = time
    # mode = mode
    # time_fsr = time_fsr
    # Tm = temp
    # Tcr = t_critic

    # tt = range(x)

    # if mode == 'Углеводородный':
    #     rl = "Углеводородный режим"
    # elif mode == 'Наружный':
    #     rl = "Наружный режим"
    # elif mode == 'Тлеющий':
    #     rl = "Тлеющий режим"
    # else:
    #     rl = "Стандартный режим"
    # label_plot_Tst = f'Температура элемента'

    # ax.plot(tt, Tm, '-', linewidth=4, label=f'{rl}', color=(0.9, 0.1, 0, 0.9))
    # # ax.plot(tt, temperature_element, '-', linewidth=4,
    # #         label=label_plot_Tst, color=(0, 0, 0, 0.35))
    # # ax.hlines(y=Tcr, xmin=0, xmax=time_fsr*0.96, linestyle='--',
    # #           linewidth=2, color=(0.1, 0.1, 0, 0.9))
    # # ax.vlines(x=time_fsr, ymin=0, ymax=Tcr*0.98, linestyle='--',
    # #           linewidth=2, color=(0.1, 0.1, 0, 0.9))

    # # if time_fsr > 0:
    # #     ax.scatter(time_fsr, Tcr, s=90, marker='o', color=(0.9, 0.1, 0, 1))
    # #     ax.annotate(f'Предел огнестойкости: {round((time_fsr / 60), 1)} мин\n'
    # #                 f'Критическая температура: {round((Tcr), 1)} \u00B0С\n'
    # #                 f'Приведенная толщина элемента: {round((ptm*1000), 3)} мм',
    # #                 xy=(time_fsr, Tcr), xycoords='data', xytext=(time_fsr+600, Tcr-40), textcoords='data', arrowprops=dict(arrowstyle='-'))
    # # else:
    # #     # ax.scatter(2000, 600, color='w', s=80, marker='o', alpha=1)
    # #     ax.annotate(f'Предел огнестойкости: {round((time_fsr / 60), 1)} мин\n'
    # #                 f'Критическая температура: {round((Tcr), 1)} \u00B0С\n'
    # #                 f'Приведенная толщина элемента: {round((ptm * 1000), 3)} мм',
    # #                 xy=(time_fsr, Tcr), xycoords='data', xytext=(2000, 200), textcoords='data')

    # ax.set_xlim(0.0, x+100)
    # ax.set_ylim(20.0, max(Tm)+100)
    # ax.set_xlabel(r"Время, с")
    # # set_y_label = str(f'Температура, \u00B0С')
    # # ax.set_ylabel(f"{set_y_label}")
    # plt.title(f'График прогрева элемента\n', fontsize=18)
    # # plt.legend(fontsize=18, framealpha=0.95, facecolor="w", loc=4)
    # # ax.grid(visible=True, which='major', axis='both',
    # #         color='k', linestyle='--', linewidth=0.10)

    # # fig.savefig(f"temp_file/fig_calc0_{chat.id}.png", dpi=150)

    # # directory = os.getcwd()
    # directory = 'tg_bot/tmp'
    # filename = f'plot_fire_resistance_{chat_id}.png'
    # filepath = os.path.join(directory, filename)
    # fig.savefig(filepath, bbox_inches='tight')
    # plt.show(fig)

    return mode
