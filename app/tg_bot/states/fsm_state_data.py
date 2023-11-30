from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage


class FSMAdminForm(StatesGroup):
    # Состояние отправки картинки для отображения на первой странице ввода данных
    admin_set_pic_steel = State()


class FSMSteelForm(StatesGroup):

    fr_steel_edit_state = State()  # Состояние редактирвания исходных данных
    mode_edit_state = State()  # Состояние редактирвания Температурный режим
    ptm_edit_state = State()  # Состояние редактирвания Приведенная толщина металла
    # Состояние редактирвания Критическая температура стали
    t_critic_edit_state = State()
    T_0_edit_state = State()  # Состояние редактирвания Начальная температура
    # Состояние редактирвания Конвективный коэффициент теплоотдачи
    a_convection_edit_state = State()
    s_1_edit_state = State()  # Состояние редактирвания Степень черноты стали
    # Состояние редактирвания Коэффициент изм. теплоемкости стали
    heat_capacity_change_edit_state = State()
    heat_capacity_edit_state = State()  # Состояние редактирвания Теплоемкость стали
    density_steel_edit_state = State()  # Состояние редактирвания Плотность стали
    s_0_edit_state = State()  # Состояние редактирвания Степень черноты среды, S\u2080


class FSMWoodForm(StatesGroup):

    fr_wood_edit_state = State()  # Состояние редактирвания исходных данных


class FSMConcreteForm(StatesGroup):

    fr_concrete_edit_state = State()  # Состояние редактирвания исходных данных
