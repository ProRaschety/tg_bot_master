
typical_accidents =
    Аварийные события
typical_accidents-text =
    <b></b>
back_typical_accidents =
    ↩ Назад

substance =
    Вещество
edit_substance =
    Вещество
velocity_wind =
    w

jet_flame =
    Струйное пламя (не используется)

run_calculation =
    ▶ Выполнить расчет (не используется)


# кнопки для Типовые аварии
accidents_kb_owner =
    dissipation_without_ignition
    fire_flash
    fire_pool
    jet_and_flare_combustion
    fire_ball
    cloud_explosion
    accident_bleve
    bleve_boiling_luquid
    scattering_of_fragments
    explosion_of_pressurized_equipment
    column_fire
    gas_jet_burning
accidents_kb_admin =
    fire_flash
    fire_pool
    horizontal_jet
    vertical_jet
    fire_ball
    cloud_explosion
    accident_bleve
accidents_kb_comrade =
    fire_flash
    fire_pool
    horizontal_jet
    vertical_jet
    fire_ball
    cloud_explosion
    accident_bleve
accidents_kb_subscriber =
    fire_flash
    fire_pool
accidents_kb_guest =
    fire_flash
    fire_pool
disabled_buttons = (не используется)
    horizontal_jet
    vertical_jet
    fire_ball
    cloud_explosion
    accident_bleve

plot_pressure_label =
    Давление взрыва
plot_impuls_label =
    Импульс волны давления
plot_pressure_legend =
    Давление взрыва, Па
plot_impuls_legend =
    Импульс волны давления, Па×с
distance_label =
    Расстояние, м
surface_density_thermal_radiation_flame =
    Среднеповерхностная плотность
    теплового излучения пламени
distance_to_safe_zone_from_the_heat_flux =
    Расстояние до безопасной зоны
    (зона, где тепловой поток < 4 кВт/м²)

dissipation_without_ignition =
    Рассеивание без воспламенения
bleve_boiling_luquid =
    Взрывное расширение паров кипящих жидкостей (BLEVE)
scattering_of_fragments =
    Разлет осколков
explosion_of_pressurized_equipment =
    Физический взрыв оборудования под давлением
column_fire =
    Пожар колонного типа (для газопроводов)
gas_jet_burning =
    Струевое горение газа (для газопроводов)



# пожар-вспышка
fire_flash =
    Пожар-вспышка
fire_flash-text =
    Расчет параметров пожара-вспышки.

fire_flash_kb =
    edit_fire_flash
    run_fire_flash
fire_flash_kb_guest =
    edit_fire_flash_guest
    run_fire_flash

run_fire_flash =
    ▶ Рассчитать

edit_fire_flash =
    📝 Редактировать
edit_fire_flash_guest =
    🔒 Редактировать

edit_fire_flash_kb =
    edit_substance
    mass_vapor_fuel
    lower_flammability_limit

mass_vapor_fuel =
    mг
lower_flammability_limit =
    Снкпр
name_mass_vapor_fuel =
    Введите массу вещества:
name_lower_flammability_limit =
    Введите значение Cнкпр вещества:
edit_fire_flash-text = {$fire_flash_param}
    <blockquote>{$edit_fire_flash}</blockquote>

back_fire_flash =
    ↩ Назад
mass_of_flammable_gases_entering_the_surrounding_space =
    Масса горючих газов (паров)
    в окружающем пространстве
radius_of_the_strait_above_which_an_explosive_zone_is_formed =
    Радиус пролива над которым
    образуется взрывоопасная зона
height_LFL =
    Zнкпр
height_zone_LFL =
    Высота зоны концентраций выше НКПР,
    при неподвижной воздушной среде
radius_LFL =
    Rнкпр
radius_zone_LFL =
    Радиус зоны концентраций выше НКПР,
    при неподвижной воздушной среде
radius_Rf =
    Rf
radius_zone_Rf =
    Радиус воздействия
    высокотемпературных продуктов
    сгорания паровоздушного облака
density_flammable_gases_at_ambient_temperature =
    Плотность горючих газов (паров)
    при температуре окружающей среды


# пожар-пролива
fire_pool =
    Пожар-пролива
fire_pool-text =
    Расчет параметров пожара-пролива.
fire_pool_kb =
    edit_fire_pool
    run_fire_pool
fire_pool_kb_guest =
    edit_fire_pool_guest
    run_fire_pool

run_fire_pool =
    ▶ Рассчитать
run_fire_pool_text =
    Пожар-пролива. Результаты расчета
result_fire_pool_kb_owner =
    plot_fire_pool
    probit_fire_pool
result_fire_pool_kb_admin =
    plot_fire_pool
    probit_fire_pool
result_fire_pool_kb_comrade =
    plot_fire_pool
    probit_fire_pool
result_fire_pool_kb_subscriber =
    plot_fire_pool

result_fire_pool_kb_guest =
    plot_fire_pool

edit_fire_pool =
    📝 Редактировать

edit_fire_pool_kb =
    edit_substance
    pool_area
    velocity_wind
    pool_distance

edit_fire_pool_guest =
    🔒 Редактировать
back_fire_pool =
    ↩ Назад
plot_fire_pool =
    📉 Тепловой поток
plot_pool_label =
    График теплового потока
y_pool_label =
    Интенсивность теплового потока, кВт/м²

probit_fire_pool =
    📈 Вероятность поражения


pool_area =
    F
pool_distance =
    r
velocity_wind =
    w

description_pool_area =
    Площадь пролива
description_pool_diameter =
    Эффективный диаметр пролива
description_pool_wind =
    Скорость ветра
description_pool_flame_angle =
    Угол наклона пламени
description_pool_flame_lenght =
    Длина пламени
description_saturated_fuel_vapor_density_at_boiling_point =
    Плотность паров горючего
    при температуре кипения
description_pool_distance =
    Расстояние от края пролива

name_pool_area =
    Введите площадь пролива:
name_pool_distance =
    Введите расстояние от края пролива:
name_velocity_wind =
    Введите скорость ветра:

edit_fire_pool-text = {$fire_pool_param}
    <blockquote>{$edit_fire_pool}</blockquote>


# взрыв ТВС
cloud_explosion =
    Взрыв ТВС
cloud_explosion-text =
    Расчет параметров взрыва облака
cloud_explosion_result-text =
    Параметры взрыва облака на расстоянии <b>{$distance}</b> м.
cloud_explosion_kb =
    edit_cloud_explosion
    run_cloud_explosion
cloud_explosion_kb_guest =
    edit_cloud_explosion_guest
    run_cloud_explosion
edit_cloud_explosion_kb =
    explosion_state_fuel
    class_fuel
    correction_parameter
    cloud_explosion_condition
    class_space
    explosion_stc_coef_oxygen
    explosion_mass_fuel
    explosion_distance
    methodology

run_cloud_explosion =
    ▶ Рассчитать
edit_cloud_explosion =
    📝 Редактировать
run_cloud_explosion_guest =
    ▶ Рассчитать
edit_cloud_explosion_guest =
    🔒 Редактировать
plot_accident_cloud_explosion_pressure =
    📉 Давление взрыва ΔP
plot_accident_cloud_explosion_impuls =
    📉 Импульс I⁺
back_cloud_explosion =
    ↩ Назад
back_edit_cloud_explosion =
    ↩ Назад
plot_cloud_explosion_pressure-text =
    <blockquote></blockquote>

cloud_explosion_condition =
    Расположение взрывоопасного облака
cloud_explosion_condition-text =
    При расчете параметров сгорания облака, расположенного <b>на поверхности земли</b>, величина эффективного энергозапаса удваивается.
above_surface =
    Над
    поверхностью
on_surface =
    На
    поверхности

methodology =
    Методика расчета
methodology-text =
    <b></b>
description_methodology =
    Методика расчета
methodology_404 =
    Мет.404
methodology_2024 =
    Мет.2024
explosion_state_fuel =
    Агрегатное состояние
    горючего вещества
cloud_explosion_state_gas =
    Газ/Пар
cloud_explosion_state_dust =
    Пыль
gas =
    Газ/Пар
dust =
    Пыль

description_explosion_state_fuel =
    Агрегатное состояние
    горючего вещества
description_coefficient_participation_in_explosion =
    Коэффициент участия горючего
    во взрыве
description_explosion_correction_parameter =
    Корректировочный параметр
description_class_space =
    Класс загроможденности
    окружающего пространства
description_condition_on_ground =
    Расположение облака паров горючего
    относительно поверхности земли
description_explosion_mass_fuel =
    Масса вышедшего газа (пара)
    в окружающее пространство
description_explosion_mode_explosion =
    Ожидаемый режим
    сгорания облака
description_explosion_distance =
    Расстояние от центра
    облака паров горючего
description_explosion_mass_explosion =
    Масса горючих газов (паров)
    участвующих во взрыве
description_explosion_spec_heat_combustion =
    Удельная теплота сгорания
    при расчете энерговыделения
description_explosion_stoichiometric_fuel =
    Стехиометрическая концентрация
    паров горючего
description_explosion_efficient_energy_reserve =
    Эффективный энергозапас
    горючей смеси
description_explosion_nondimensional_distance =
    Безразмерное расстояние
    от центра облака
description_explosion_nondimensional_pressure =
    Безразмерное давление
description_explosion_nondimensional_impuls =
    Безразмерный импульс
    фазы сжатия

correction_parameter =
    β
explosion_stc_coef_oxygen =
    k

class_fuel =
    Класс горючего вещества
edit_cloud_explosion_class_fuel-text =
    <b>Класс 1</b>: Особо чувствительные вещества. Размер детоционной ячейки менее 2 см.
    <b>Класс 2</b>: Чувствительные вещества. Размер детоционной ячейки от 2 до 10 см.
    <b>Класс 3</b>: Среднечувствительные вещества. Размер детоционной ячейки от 10 до 40 см.
    <b>Класс 4</b>: Слабочувствительные вещества. Размер детоционной ячейки больше 40 см.
class_fuel_first =
    1
class_fuel_second =
    2
class_fuel_third =
    3
class_fuel_fourth =
    4

class_space =
    Класс загроможденности пространства
edit_cloud_explosion_class_space-text =
    <b>Класс I</b>: Наличие длинных труб, полостей, каверн, заполненных горючей смесью, при сгорании которой возможно ожидать формирование турбулентных струй продуктов сгорания, имеющих размеры не менее трех размеров детонационной ячейки данной смеси.
    <b>Класс II</b>: Сильно загроможденное пространство: наличие полузамкнутых объемов высокая плотность размещения технологического оборудования, лес, большое количество повторяющихся препятствий.
    <b>Класс III</b>: Средне загроможденное пространство: отдельно стоящие технологические установки, резервуарный парк.
    <b>Класс IV</b>: Слабо загроможденное и свободное пространство.
class_space_first =
    I
class_space_second =
    II
class_space_third =
    III
class_space_fourth =
    IV

edit_cloud_explosion_coef_z =
    Z
explosion_mass_fuel =
    m
explosion_distance =
    r

edit_cloud_explosion-text = {$cloud_explosion_param}
    <blockquote>{$edit_cloud_explosion}</blockquote>

name_correction_parameter =
    Введите корретировочный параметр:
name_cloud_explosion_stc_coef_oxygen =
    Введите значение стехиометрического коэффициента
    при кислороде:
name_cloud_explosion_coef_z =
    Введите значение коэффициента Z
    участия горючего во взрыве:
name_explosion_mass_fuel =
    Введите массу вещества:
name_explosion_distance =
    Введите расстояние от центра взрыва:


# огненный шар
fire_ball =
    Огненный шар
fire_ball-text =
    Расчет параметров огненного шара.
fire_ball_kb =
    edit_fire_ball
    run_fire_ball
fire_ball_kb_guest =
    edit_fire_ball_guest
    run_fire_ball
back_fire_ball =
    ↩ Назад
run_fire_ball =
    ▶ Рассчитать

edit_fire_ball =
    📝 Редактировать
edit_fire_ball_kb =
    edit_substance
    fire_ball_mass_fuel
    fire_ball_distance

edit_fire_ball_guest =
    🔒 Редактировать
plot_fire_ball =
    📉 Тепловой поток
probit_fire_ball =
    📈 Вероятность поражения
plot_ball_label =
    График теплового потока
y_ball_label =
    Интенсивность теплового потока, кВт/м²

fire_ball_mass_fuel =
    m
fire_ball_distance =
    r
name_fire_ball_mass_fuel =
    Введите массу горючего вещества:
name_fire_ball_distance =
    Введите расстояние от ОШ:
edit_fire_ball-text = {$fire_ball_param}
    <blockquote>{$edit_fire_ball}</blockquote>
description_ball_height_center =
    Высота центра
    огненного шара
description_ball_mass_fuel =
    Масса горючего вещества
    поступившего
    в окружающее пространство
description_ball_distance =
    Расстояние от облучаемого объекта
    до точки на поверхности земли
    под центром огненного шара
description_ball_existence_time =
    Время существования
    огненного шара
description_ball_diameter =
    Эффективный диаметр
    огненного шара
description_ball_view_factor =
    Угловой коэффициент облученности
description_ball_atmospheric_transmittance =
    Коэффициент пропускания атмосферы
description_ball_heat_flux =
    Тепловой поток
    на расстоянии r


# взрыв сосуда в очаге пожара
accident_bleve =
    Взрыв резервуара
accident_bleve-text =
    Расчет параметров взрыва.
    Форм.(В.14) и (В.22) СП12 и форм.(П3.47) М404
accident_bleve_kb =
    edit_accident_bleve
    run_accident_bleve
accident_bleve_kb_guest =
    edit_accident_bleve_guest
    run_accident_bleve
back_accident_bleve =
    ↩ Назад
run_accident_bleve =
    ▶ Рассчитать
edit_accident_bleve =
    📝 Редактировать
edit_accident_bleve_kb =
    edit_substance
    bleve_mass_fuel
    bleve_distance

edit_accident_bleve_guest =
    🔒 Редактировать
plot_accident_bleve_pressure =
    📉 Давление взрыва ΔP
plot_accident_bleve_impuls =
    📉 Импульс I⁺

bleve_mass_fuel =
    m
name_bleve_mass_fuel =
    Введите массу вещества:

bleve_distance =
    r
name_bleve_distance =
    Введите расстояние от центра взрыва:

edit_bleve-text = {$bleve_param}
    <blockquote>{$edit_bleve}</blockquote>

description_bleve_distance =
    Расстояние
    от центра взрыва
description_effective_explosion_energy =
    Эффективная энергия взрыва
description_pressure_wave_energy_fraction =
    Доля энергии волны давления
description_reduced_mass_liquid_phase =
    Приведенная масса жидкой фазы
description_mass_liquid_phase =
    Масса жидкой фазы
    в резервуаре
description_temperature_liquid_phase =
    Температура жидкой фазы
description_device_response_pressure =
    Давление срабатывания
    предохранительного устройства


# Факельное горение веществ
jet_and_flare_combustion =
    Факельное горение
back_jet_and_flare_combustion =
    ↩ Назад

jet_and_flare_combustion_kb =
    horizontal_jet
    vertical_jet
    flare_combustion

flare_combustion =
    🚧 Сжигание газа на факеле
back_flare_combustion =
    ↩ Назад
flare_combustion-text =
    Расчет параметров горизонтального факела.
    🚧 <i>Находится в разработке</i>
flare_combustion_kb =
    edit_flare_combustion
    plot_flare_combustion
flare_combustion_kb_guest =
    edit_flare_combustion_guest
    plot_flare_combustion
run_flare_combustion =
    ▶ Рассчитать
edit_flare_combustion =
    📝 Редактировать
edit_flare_combustion_kb =
    edit_flare_combustion_mass_rate
    edit_distance
edit_flare_combustion_guest =
    🔒 Редактировать


horizontal_jet =
    Горизонтальный факел
back_horizontal_jet =
    ↩ Назад
horizontal_jet-text =
    Расчет параметров горизонтального факела.
horizontal_jet_kb =
    edit_horizontal_jet
    plot_horizontal_jet
horizontal_jet_kb_guest =
    edit_horizontal_jet_guest
    plot_horizontal_jet
run_horizontal_jet =
    ▶ Рассчитать
edit_horizontal_jet =
    📝 Редактировать
edit_horizontal_jet_kb =
    jet_state_fuel
    jet_mass_rate
    distance
    plot_horizontal_jet

edit_horizontal_jet_guest =
    🔒 Редактировать

plot_horizontal_jet_label =
    График теплового потока
y_horizontal_jet_label =
    Интенсивность теплового потока, кВт/м²


vertical_jet =
    Вертикальный факел
back_vertical_jet =
    ↩ Назад
vertical_jet-text =
    Расчет параметров вертикального факела.
vertical_jet_kb =
    edit_vertical_jet
    plot_vertical_jet
vertical_jet_kb_guest =
    edit_vertical_jet_guest
    plot_vertical_jet

edit_vertical_jet_kb =
    jet_state_fuel
    jet_mass_rate
    distance
    plot_vertical_jet

jet_state_fuel =
    Агрегатное состояние ГВ
jet_mass_rate =
    Расход ГВ
distance =
    Расстояние до облучаемого объекта

run_vertical_jet =
    ▶ Рассчитать
edit_vertical_jet =
    📝 Редактировать
edit_vertical_jet_guest =
    🔒 Редактировать


plot_vertical_jet_label =
    График теплового потока
y_vertical_jet_label =
    Интенсивность теплового потока, кВт/м²

jet_state_liquid_kb =
    Жидкая фаза 💧
jet_state_comp_gas_kb =
    Сжатый газ 💨
jet_state_liq_gas_vap_kb =
    Паровая фаза ☁

plot_horizontal_jet =
    📉 Тепловой поток

plot_vertical_jet =
    📉 Тепловой поток

name_jet_mass_rate =
    Введите расход продукта:
name_distance =
    Введите расстояние до облучаемого объекта:


description_jet_mass_rate =
    Расход продукта
description_jet_distance =
    Расстояние до облучаемого объекта

description_jet_state_fuel =
    Агрегатное состояние горючего вещества
jet_state_liquid =
    Жидкая фаза
jet_state_liq_gas_vap =
    Паровая фаза
jet_state_comp_gas =
    Сжатый газ
description_empirical_coefficient =
    Эмпирический коэффициент
description_jet_mass_rate =
    Расход сжатого газа, паровой
    или жидкой фазы сжиженного газа
description_jet_flame_length =
    Длина факела
description_jet_flame_width =
    Ширина факела
description_jet_human_distance =
    Расстояние до облучаемого объекта