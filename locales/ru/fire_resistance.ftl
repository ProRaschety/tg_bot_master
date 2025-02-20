
# РАСЧЕТ СТАЛЬНЫХ КОНСТРУКЦИЙ

type_calculation_steel_kb_owner =
    strength_calculation
    thermal_calculation
type_calculation_steel_kb_admin =
    strength_calculation
    thermal_calculation
type_calculation_steel_kb_comrade =
    strength_calculation
    thermal_calculation
type_calculation_steel_kb_subscriber =
    thermal_calculation
type_calculation_steel_kb_guest =
    thermal_calculation

# Пакетный расчет

fire_protection = Пакетный расчет
fire_protection-text = Пакетный расчет огнестойкости стальных эелементов
                        🚧 <i>Находится в разработке</i>

fire_protection_calculation = Расчет параметров огнезащиты
add_element_steel = Добавить элемент
add_element_steel-text = Добавьте элементы для расчета
add_quantity_element = Укажите количество элементов

edit_init_data_protection = Редактировать элементы
run_protection_steel = Выполнить расчет
back_protection_element = ↩ Назад
clear_table_protection_steel = 🚮 Очистить таблицу
clear_table_protection_steel-text = Таблица готова для заполнения


# ПРОЧНОСТНОЙ расчет стальной конструкции
initial_data_steel-text =
    <b></b>
back_type_calc =
    ⤴ Выход
back_type_material =
    ↩ Назад
back_steel_element =
    ↩ Назад

stop_edit_strength =
    ❌ Отменить ввод
next_page_steel =
    ➡ Следующая страница

fire_resistance-text =
    Виберите материал конструкции
steel_element =
    Стальная

type_of_calculation_steel-text =
    <i></i>

strength_calculation = ⚒ Прочностной расчет
run_strength_steel = ▶ Рассчитать
edit_init_data_strength = 📝 Редактировать
back_strength_element = ↩ Назад
ptm_strength_edit = Приведенная толщина металла
ptm_strength_edit-text = Приведенная толщина металла <blockquote>{ $ptm_strength } мм</blockquote>

                Для завершения ввода нажмите 💾
type_steel_element_edit = Марка стали
type_steel_element_edit-text = Выберите марку стали
C235 = C235
C245 = C245
C255 = C255
C345 = C345
C355 = C355
C375 = C375
C390 = C390
C440 = C440
C550 = C550
C590 = C590
C355P = C355П
C390P = C390П


type_of_load_edit = Тип нагружения
type_of_load_edit-text = Выберите тип нагружения элемента конструкции
distributed_load_steel = Распределенная
    нагрузка
concentrated_load_steel = Сосредоточенная
    нагрузка

len_elem_edit = Длина
len_elem_edit-text = Установите длину элемента <blockquote>{ $len_elem } мм</blockquote>

                        Для завершения ввода нажмите 💾

fixation_steel-text = Выберите способ закрепления элемента конструкции
fixation_steel = Способ закрепления
hinge-hinge = Шарнир - шарнир
sealing-sealing = Заделка - заделка
seal-hinge = Заделка - шарнир
console = Консоль
one-sided-seal = Односторонняя заделка

beam_steel = Балка
column_steel = Колонна

fire_resistance_element-text = Виберите тип элемента конструкции
ibeam_element = Двутавр
channel_element = Швеллер

type_ibeam = Двутавр
reg_document_1 = "ГОСТ Р 57837"

num_profile = Профиль
num_profile_inline_search-text = Нажмите на кнопку <b>Выбрать профиль</b> чтобы начать поиск 🔎
select_steel_profile = Выбрать профиль 🔎

type_channel = Швеллер
type_corner = Уголок
type_profile = Профиль
type_profile_square = Квадратный
type_profile_rectangle = Прямоугольный

type_loading_element-text = Виберите тип усилия элемента конструкции
type_loading_element = Усилие
stretching_element = Растяжение
compression_element = Сжатие
bend_element = Изгиб

num_sides_heated-text = Укажите количество сторон обогрева элемента
sides_heated = Обогрев сторон
num_sides_heated_two = 2
num_sides_heated_three = 3
num_sides_heated_four = 4

loads_steel_edit = Нагрузка
loads_steel_edit-text =
    Установите значение нагрузки <blockquote>{$n_load} кг</blockquote>

    Для завершения ввода нажмите 💾

strength_calculation-text = Критическая температура
    стального элемента конструкции
    <blockquote>{ $t_critic } ℃</blockquote>

compression_element_result-text =
    Коэффициент снижения предела текучести стали <blockquote>γе = { $gamma_t }</blockquote>
    Коэффициент снижения модуля упругости стали <blockquote>γt = { $gamma_elasticity }</blockquote>
    Критическая температура стального элемента конструкции
    <blockquote>{ $t_critic } ℃</blockquote>
stretch_or_bend_element_result-text =
    Коэффициент снижения предела текучести стали <blockquote>γt = { $gamma }</blockquote>
    Критическая температура стального элемента конструкции
    <blockquote>{ $t_critic } ℃</blockquote>
export_data_strength = 🔄 Экспорт
export_data_strength-text = Экспорт данных расчета
                            🚧 <i>Находится в разработке</i>

protocol_strength = 📄 Протокол расчета
protocol_strength-text = Протокол расчета критической температуры стального элемента конструкции.
                        🚧 <i>Находится в разработке</i>


# ТЕПЛОТЕХНИЧЕСКИЙ расчет стальной конструкции
thermal_calculation =
    🔥 Теплотехнический расчет

thermal_calculation_kb_owner =
    edit_init_data_thermal
    run_thermal_steel
thermal_calculation_kb_admin =
    edit_init_data_thermal
    run_thermal_steel
thermal_calculation_kb_comrade =
    edit_init_data_thermal
    run_thermal_steel
thermal_calculation_kb_subscriber =
    edit_init_data_thermal
    run_thermal_steel
thermal_calculation_kb_guest =
    edit_init_data_thermal_guest
    run_thermal_steel

back_thermal_calculation =
    ↩ Назад
back_thermal_calc =
    ↩ Назад

edit_init_data_thermal =
    📝 Редактировать
edit_thermal_calculation_kb =
    mode_edit
    ptm_edit
    t_critic_edit

edit_init_data_thermal_guest =
    🔒 Редактировать
run_thermal_steel =
    ▶ Рассчитать
stop_edit_thermal_calc =
    ❌ Отменить ввод
thermal_calculation-text =
    Предел огнестойкости незащищенного стального элемента конструкции <blockquote>{ $time_fsr } мин</blockquote>
plot_thermal =
    📈 График прогрева
plot_thermal-text =
    График прогрева стального элемента

edit_init_data_thermal-text = Выберите параметр для редактирования
mode_edit = Температурный режим
ptm_edit = Приведенная толщина металла
t_critic_edit = Критическая температура стали
T_0_edit = Начальная температура
a_convection_edit = Конвективный коэффициент теплоотдачи
s_1_edit = Степень черноты стали
heat_capacity_change_edit = Коэффициент изм. теплоемкости стали
heat_capacity_edit = Теплоемкость стали
density_steel_edit = Плотность стали
s_0_edit = Степень черноты среды, S\u2080

mode_edit-text = Выберите Температурный режим
mode_standard = Стандартный
mode_hydrocarbon = Углеводородный
mode_external = Наружный
mode_smoldering = Тлеющий

ptm_edit-text =
    Приведенная толщина металла <blockquote>{ $ptm } мм</blockquote>

    Для завершения ввода нажмите 💾
t_critic_edit-text =
    Критическая температура стали <blockquote>{ $t_critic } ℃</blockquote>

    Для завершения ввода нажмите 💾
T_0_edit-text =
    Начальная температура
a_convection_edit-text =
    Конвективный коэффициент теплоотдачи
s_1_edit-text = Степень черноты стали
heat_capacity_change_edit-text =
    Коэффициент изм. теплоемкости стали
heat_capacity_edit-text =
    Теплоемкость стали
density_steel_edit-text =
    Плотность стали
s_0_edit-text =
    Степень черноты среды

protocol_thermal =
    📄 Протокол расчета
protocol_thermal-text =
    Протокол расчета собственного предела огнестойкости
    незащищенной стальной конструкции.
    🚧 <i>Находится в разработке</i>
export_data_steel =
    🔄 Экспорт
export_data_steel-text =
    Экспорт данных теплотехнического расчета



# РАСЧЕТ ДЕРЕВЯННЫХ КОНСТРУКЦИЙ
wood_element = 🚧 Деревянная
type_of_calculation_wood-text = Расчет огнестойкости деревянных конструкций
                                🚧 <i>Находится в разработке</i>


# РАСЧЕТ ЖЕЛЕЗОБЕТОННЫХ КОНСТРУКЦИЙ
concrete_element = 🚧 Железебетонная
type_of_calculation_concrete-text = Расчет огнестойкости железобетонных конструкций
                                    🚧 <i>Находится в разработке</i>
