from aiogram.fsm.state import State, StatesGroup


class FSMOwnerForm(StatesGroup):
    promocode_state = State()


class FSMAdminForm(StatesGroup):
    # Состояние отправки картинки для отображения на первой странице ввода данных
    admin_set_pic_steel = State()


class FSMEditForm(StatesGroup):
    keypad_state = State()


class FSMFDSForm(StatesGroup):
    accept_document_state = State()


class FSMCatBuildForm(StatesGroup):
    edit_area_A_state = State()
    edit_area_B_state = State()
    edit_area_V1_state = State()
    edit_area_V2_state = State()
    edit_area_V3_state = State()
    edit_area_V4_state = State()
    edit_area_G_state = State()
    edit_area_D_state = State()
    edit_area_A_EFS_state = State()
    edit_area_B_EFS_state = State()
    edit_area_V1_EFS_state = State()
    edit_area_V2_EFS_state = State()
    edit_area_V3_EFS_state = State()


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
    len_elem_edit_state = State()  # Состояние редактирвания длины элемеента конструкции
    # Состояние редактирвания нагрузки на элемеент конструкции
    n_load_edit_state = State()
    num_profile_inline_search_state = State()
    add_steel_element_state = State()


class FSMWoodForm(StatesGroup):
    fr_wood_edit_state = State()  # Состояние редактирвания исходных данных


class FSMConcreteForm(StatesGroup):
    fr_concrete_edit_state = State()  # Состояние редактирвания исходных данных


class FSMSubstanceForm(StatesGroup):
    database_edit_state = State()  # Состояние выбора вещества из базы данных
    database_search_state = State()  # Состояние поиска веществ в базе данных
    database_inline_state = State()  # Состояние поиска веществ в инлайн-режиме


class FSMPromoCodeForm(StatesGroup):
    promo_code_state = State()  # Состояние ввода промокода


class FSMClimateForm(StatesGroup):
    select_region_state = State()
    select_city_state = State()


class FSMFireRiskForm(StatesGroup):
    edit_fire_freq_pub = State()
    edit_time_presence_pub = State()
    edit_probity_evac_pub = State()
    select_type_obj_pub = State()

    edit_time_crowding_pub = State()
    edit_time_evacuation_pub = State()
    edit_time_blocking_paths_pub = State()
    edit_time_start_evacuation_pub = State()

    edit_fire_freq_ind = State()
    edit_time_presence_ind = State()
    edit_probity_evac_ind = State()
    edit_area_ind = State()
    edit_work_days_ind = State()

    edit_time_evacuation_ind = State()
    edit_time_blocking_paths_ind = State()
    edit_time_start_evacuation_ind = State()


class FSMFireAccidentForm(StatesGroup):
    edit_fire_accident_state = State()

    edit_fire_pool_area_state = State()
    edit_fire_pool_distance_state = State()
    edit_fire_pool_wind_state = State()

    edit_horizontal_jet_mass_flow_state = State()
    edit_horizontal_jet_distance_state = State()

    edit_vertical_jet_mass_flow_state = State()
    edit_vertical_jet_distance_state = State()

    edit_fire_flash_mass_state = State()
    edit_fire_flash_lcl_state = State()

    edit_fire_ball_mass_state = State()
    edit_fire_ball_distance_state = State()

    edit_bleve_mass_state = State()
    edit_bleve_distance_state = State()

    edit_cloud_explosion_correction_parameter_state = State()
    edit_cloud_explosion_stc_coef_oxygen_state = State()
    edit_cloud_explosion_coef_z_state = State()
    edit_cloud_explosion_mass_state = State()
    edit_cloud_explosion_distance_state = State()


class FSMToolLiquidForm(StatesGroup):
    edit_state_liquid_density = State()
    edit_state_liquid_volume_vessel = State()
    edit_state_liquid_height_vessel = State()
    edit_state_liquid_vessel_diameter = State()
    edit_state_liquid_temperature = State()
    edit_state_liquid_fill_factor = State()
    edit_state_liquid_hole_diameter = State()
    edit_state_liquid_hole_distance = State()
    edit_state_liquid_mu = State()


class FSMToolCompGasForm(StatesGroup):
    edit_state_comp_gas_pres_init = State()
    edit_state_comp_gas_density = State()
    edit_state_comp_gas_volume_vessel = State()
    edit_state_comp_gas_height_vessel = State()
    edit_state_comp_gas_vessel_diameter = State()
    edit_state_comp_gas_temperature = State()
    edit_state_comp_gas_coef_poisson = State()
    edit_state_comp_gas_hole_diameter = State()
    edit_state_comp_gas_specific_heat_const_vol = State()
    edit_state_comp_gas_mu = State()
    edit_state_comp_gas_molar_mass = State()


class FSMFrequencyForm(StatesGroup):
    edit_area_to_frequency = State()
    edit_type_to_table_1_3 = State()
    edit_type_to_table_2_3 = State()
    edit_type_to_table_2_4 = State()


class FSMFireModelForm(StatesGroup):
    edit_standard_flammable_load = State()

    edit_analytics_model_lenght_room = State()
    edit_analytics_model_width_room = State()
    edit_analytics_model_height_room = State()
    edit_analytics_model_air_temperature = State()
