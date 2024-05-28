import logging

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
# , InlineQueryResultArticle, InputTextMessageContent
# from aiogram.types import InlineQuery
from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaPhoto

from fluentogram import TranslatorRunner

# from app.infrastructure.database.database.db import DB
from app.tg_bot.models.role import UserRole
from app.tg_bot.filters.filter_role import IsGuest
from app.tg_bot.states.fsm_state_data import FSMFireAccidentForm
from app.calculation.physics.accident_parameters import AccidentParameters
from app.tg_bot.utilities.misc_utils import get_picture_filling, get_data_table, get_plot_graph
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb
from app.calculation.physics.physics_utils import compute_characteristic_diameter, compute_density_gas_phase, compute_density_vapor_at_boiling, get_property_fuel, compute_stoichiometric_coefficient_with_fuel, compute_stoichiometric_coefficient_with_oxygen

log = logging.getLogger(__name__)

fire_accident_router = Router()
fire_accident_router.message.filter(IsGuest())
fire_accident_router.callback_query.filter(IsGuest())

SFilter_fire_pool = [FSMFireAccidentForm.edit_fire_pool_area_state,
                     FSMFireAccidentForm.edit_fire_pool_distance_state,
                     FSMFireAccidentForm.edit_fire_pool_wind_state]

SFilter_horizontal_jet = [FSMFireAccidentForm.edit_horizontal_jet_mass_flow_state,
                          FSMFireAccidentForm.edit_horizontal_jet_distance_state]

SFilter_vertical_jet = [FSMFireAccidentForm.edit_vertical_jet_mass_flow_state,
                        FSMFireAccidentForm.edit_vertical_jet_distance_state]

SFilter_fire_flash = [FSMFireAccidentForm.edit_fire_flash_mass_state,
                      FSMFireAccidentForm.edit_fire_flash_lcl_state]

SFilter_fire_ball = [FSMFireAccidentForm.edit_fire_ball_mass_state,
                     FSMFireAccidentForm.edit_fire_ball_distance_state]

SFilter_bleve = [FSMFireAccidentForm.edit_bleve_mass_state,
                 FSMFireAccidentForm.edit_bleve_distance_state]

SFilter_cloud_explosion = [FSMFireAccidentForm.edit_cloud_explosion_correction_parameter_state,
                           FSMFireAccidentForm.edit_cloud_explosion_stc_coef_oxygen_state,
                           FSMFireAccidentForm.edit_cloud_explosion_coef_z_state,
                           FSMFireAccidentForm.edit_cloud_explosion_mass_state,
                           FSMFireAccidentForm.edit_cloud_explosion_distance_state]

kb_accidents = [1,
                'fire_pool',
                'fire_flash',
                'cloud_explosion',
                'horizontal_jet',
                'vertical_jet',
                'fire_ball',
                'accident_bleve',]

kb_edit_pool = [4,
                'edit_pool_substance',
                'edit_pool_area',
                'edit_pool_wind',
                'edit_pool_distance']

kb_edit_hjet = [1,
                'edit_hjet_state',
                'edit_hjet_mass_rate',
                'edit_hjet_distance']

kb_edit_vjet = [1,
                'edit_vjet_state',
                'edit_vjet_mass_rate',
                'edit_vjet_distance']

kb_edit_ball = [4,
                'edit_ball_mass',
                'edit_ball_distance']

kb_edit_flash = [4,
                 'edit_flash_mass',
                 'edit_flash_lcl']

kb_edit_bleve = [4,
                 'edit_bleve_mass',
                 'edit_bleve_distance']

kb_edit_cloud_explosion = [2,
                           'edit_cloud_explosion_state',
                           'edit_cloud_explosion_correction_parameter',
                           'edit_cloud_explosion_stc_coef_oxygen',
                           'edit_cloud_explosion_class_fuel',
                           'edit_cloud_explosion_class_space',
                           'edit_cloud_explosion_expl_cond',
                           'edit_cloud_explosion_coef_z',
                           'edit_cloud_explosion_mass_fuel',
                           'edit_cloud_explosion_distance',
                           'cloud_explosion_methodology']


@fire_accident_router.callback_query(F.data == 'back_typical_accidents')
async def back_typical_accidents_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.typical_accidents.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_accident_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*kb_accidents, i18n=i18n, param_back=True, back_data='back_fire_risks'))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'typical_accidents')
async def typical_accidents_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    data.setdefault("edit_typical_accidents", "0")
    text = i18n.typical_accidents.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_accident_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*kb_accidents, i18n=i18n, param_back=True, back_data='back_fire_risks'))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['fire_pool', 'back_fire_pool']))
async def fire_pool_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    data.setdefault("edit_accident_fire_pool_param", "1")
    data.setdefault("accident_fire_pool_sub", "gasoline")
    data.setdefault("accident_fire_pool_molar_mass_fuel", "100")
    data.setdefault("accident_fire_pool_boiling_point_fuel", "180")
    data.setdefault("accident_fire_pool_mass_burning_rate", "0.06")
    data.setdefault("accident_fire_pool_heat_of_combustion", "36000")
    data.setdefault("accident_fire_pool_temperature", "20")
    data.setdefault("accident_fire_pool_wind", "0")
    data.setdefault("accident_fire_pool_pool_area", "314")
    data.setdefault("accident_fire_pool_distance", "30")
    await state.update_data(data)
    data = await state.get_data()
    text = i18n.fire_pool.text()

    subst = data.get('accident_fire_pool_sub')
    air_density = compute_density_gas_phase(
        molar_mass=28.97, temperature=float(data.get('accident_fire_pool_temperature')))

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('fire_pool')
    data_out = [
        {'id': i18n.get('pool_distance'), 'var': 'r',  'unit_1': data.get(
            'accident_fire_pool_distance'), 'unit_2': i18n.get('meter')},
        {'id': i18n.get('pool_area'), 'var': 'F',  'unit_1': data.get(
            'accident_fire_pool_pool_area'), 'unit_2': i18n.get('meter_square')},
        {'id': i18n.get('wind_velocity'), 'var': 'wₒ',
            'unit_1': data.get('accident_fire_pool_wind'), 'unit_2': i18n.get('m_per_sec')},
        {'id': i18n.get('ambient_air_density'), 'var': 'ρₒ',
            'unit_1': f"{air_density:.2f}", 'unit_2': i18n.get('kg_per_m_cub')},
        {'id': i18n.get('ambient_temperature'), 'var': 'tₒ', 'unit_1': data.get(
            'accident_fire_pool_temperature'), 'unit_2': i18n.get('celsius')},
        {'id': i18n.get('specific_mass_fuel_burning_rate'),
            'var': 'm', 'unit_1': data.get('accident_fire_pool_mass_burning_rate'), 'unit_2': i18n.get('kg_per_m_square_in_sec')},
        # {'id': i18n.get('specific_heat_of_combustion'), 'var': 'Hсг',
        #     'unit_1': data.get(
        #     'accident_fire_pool_heat_of_combustion'), 'unit_2': i18n.get('kJ_per_kg')},
        {'id': i18n.get('substance'), 'var': '-', 'unit_1': i18n.get(subst), 'unit_2': '-'}]

    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_fire_pool', 'run_fire_pool', i18n=i18n, param_back=True, back_data='back_typical_accidents', check_role=True, role=role))
    await state.update_data(data)


@fire_accident_router.callback_query(F.data.in_(['edit_fire_pool']))
async def edit_fire_pool_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(*kb_edit_pool, i18n=i18n, param_back=True, back_data='back_fire_pool', check_role=True, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_pool_substance']))
async def pool_subst_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, 'gasoline', 'diesel', 'LNG', 'LPG', 'liq_hydrogen', i18n=i18n))


@fire_accident_router.callback_query(F.data.in_(['gasoline', 'diesel', 'LNG', 'LPG', 'liq_hydrogen']))
async def fire_pool_subst_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    call_data = callback.data
    # data = await state.get_data()
    molar_mass, boling_point, m = get_property_fuel(subst=call_data)
    await state.update_data(accident_fire_pool_sub=call_data)
    await state.update_data(accident_fire_pool_molar_mass_fuel=molar_mass)
    await state.update_data(accident_fire_pool_boiling_point_fuel=boling_point)
    await state.update_data(accident_fire_pool_mass_burning_rate=m)

    data = await state.get_data()
    await state.update_data(data)
    data = await state.get_data()
    text = i18n.fire_pool.text()
    subst = data.get('accident_fire_pool_sub')
    air_density = compute_density_gas_phase(
        molar_mass=28.97, temperature=float(data.get('accident_fire_pool_temperature')))
    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('fire_pool')
    data_out = [
        {'id': i18n.get('pool_area'), 'var': 'F',  'unit_1': data.get(
            'accident_fire_pool_pool_area'), 'unit_2': i18n.get('meter_square')},
        {'id': i18n.get('wind_velocity'), 'var': 'wₒ',
            'unit_1': data.get('accident_fire_pool_vel_wind'), 'unit_2': i18n.get('m_per_sec')},
        {'id': i18n.get('ambient_air_density'), 'var': 'ρₒ',
            'unit_1': f"{air_density:.2f}", 'unit_2': i18n.get('kg_per_m_cub')},
        {'id': i18n.get('ambient_temperature'), 'var': 'tₒ', 'unit_1': data.get(
            'accident_fire_pool_temperature'), 'unit_2': i18n.get('celsius')},
        {'id': i18n.get('specific_mass_fuel_burning_rate'),
            'var': 'm', 'unit_1': data.get('accident_fire_pool_mass_burning_rate'), 'unit_2': i18n.get('kg_per_m_square_in_sec')},
        # {'id': i18n.get('specific_heat_of_combustion'), 'var': 'Hсг',
        #     'unit_1': data.get(
        #     'accident_fire_pool_heat_of_combustion'), 'unit_2': i18n.get('kJ_per_kg')},
        {'id': i18n.get('substance'), 'var': '-', 'unit_1': i18n.get(subst), 'unit_2': '-'}]
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_fire_pool', 'run_fire_pool', i18n=i18n, param_back=True, back_data='back_typical_accidents', check_role=True, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_pool_area', 'edit_pool_distance', 'edit_pool_wind']))
async def edit_pool_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    if callback.data == 'edit_pool_area':
        await state.set_state(FSMFireAccidentForm.edit_fire_pool_area_state)
    elif callback.data == 'edit_pool_distance':
        await state.set_state(FSMFireAccidentForm.edit_fire_pool_distance_state)
    elif callback.data == 'edit_pool_wind':
        await state.set_state(FSMFireAccidentForm.edit_fire_pool_wind_state)
    data = await state.get_data()
    state_data = await state.get_state()
    if state_data == FSMFireAccidentForm.edit_fire_pool_area_state:
        text = i18n.edit_fire_pool.text(fire_pool_param=i18n.get(
            "name_fire_pool_area"), edit_fire_pool=data.get("accident_fire_pool_pool_area", 0))
    elif state_data == FSMFireAccidentForm.edit_fire_pool_distance_state:
        text = i18n.edit_fire_pool.text(fire_pool_param=i18n.get(
            "name_fire_pool_distance"), edit_fire_pool=data.get("accident_fire_pool_distance", 0))
    elif state_data == FSMFireAccidentForm.edit_fire_pool_wind_state:
        text = i18n.edit_fire_pool.text(fire_pool_param=i18n.get(
            "name_fire_pool_wind"), edit_fire_pool=data.get("accident_fire_pool_wind", 0))
    kb = ['one', 'two', 'three', 'four', 'five', 'six', 'seven',
          'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready']

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, *kb, i18n=i18n))
    await callback.answer('')


@fire_accident_router.callback_query(StateFilter(*SFilter_fire_pool), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'dooble_zero', 'point', 'clear']))
async def edit_fire_pool_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    if state_data == FSMFireAccidentForm.edit_fire_pool_area_state:
        fire_pool_param = i18n.get("name_fire_pool_area")
    elif state_data == FSMFireAccidentForm.edit_fire_pool_distance_state:
        fire_pool_param = i18n.get("name_fire_pool_distance")
    elif state_data == FSMFireAccidentForm.edit_fire_pool_wind_state:
        fire_pool_param = i18n.get("name_fire_pool_wind")

    edit_data = await state.get_data()
    if callback.data == 'clear':
        await state.update_data(edit_accident_fire_pool_param="")
        edit_d = await state.get_data()
        edit_data = edit_d.get('edit_accident_fire_pool_param', 1)
        text = i18n.edit_fire_pool.text(
            fire_pool_param=fire_pool_param, edit_fire_pool=edit_data)

    else:
        edit_param_1 = edit_data.get('edit_accident_fire_pool_param')
        edit_sum = edit_param_1 + i18n.get(callback.data)
        await state.update_data(edit_accident_fire_pool_param=edit_sum)
        edit_data = await state.get_data()
        edit_param = edit_data.get('edit_accident_fire_pool_param', 0)
        text = i18n.edit_fire_pool.text(
            fire_pool_param=fire_pool_param, edit_fire_pool=edit_param)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready', i18n=i18n))


@fire_accident_router.callback_query(StateFilter(*SFilter_fire_pool), F.data.in_(['ready']))
async def edit_fire_pool_param_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    state_data = await state.get_state()
    data = await state.get_data()
    value = data.get("edit_accident_fire_pool_param")
    if state_data == FSMFireAccidentForm.edit_fire_pool_area_state:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(accident_fire_pool_pool_area=value)
        else:
            await state.update_data(accident_fire_pool_pool_area=10)
    elif state_data == FSMFireAccidentForm.edit_fire_pool_distance_state:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(accident_fire_pool_distance=value)
        else:
            await state.update_data(accident_fire_pool_distance=10)
    elif state_data == FSMFireAccidentForm.edit_fire_pool_wind_state:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(accident_fire_pool_wind=value)
        else:
            await state.update_data(accident_fire_pool_wind=0)

    data = await state.get_data()
    text = i18n.fire_pool.text()
    subst = data.get('accident_fire_pool_sub')
    air_density = compute_density_gas_phase(
        molar_mass=28.97, temperature=float(data.get('accident_fire_pool_temperature')))
    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('fire_pool')
    data_out = [
        {'id': i18n.get('pool_distance'), 'var': 'r',  'unit_1': data.get(
            'accident_fire_pool_distance'), 'unit_2': i18n.get('meter')},
        {'id': i18n.get('pool_area'), 'var': 'F',  'unit_1': data.get(
            'accident_fire_pool_pool_area'), 'unit_2': i18n.get('meter_square')},
        {'id': i18n.get('wind_velocity'), 'var': 'wₒ',
            'unit_1': data.get('accident_fire_pool_wind'), 'unit_2': i18n.get('m_per_sec')},
        {'id': i18n.get('ambient_air_density'), 'var': 'ρₒ',
            'unit_1': f"{air_density:.2f}", 'unit_2': i18n.get('kg_per_m_cub')},
        {'id': i18n.get('ambient_temperature'), 'var': 'tₒ', 'unit_1': data.get(
            'accident_fire_pool_temperature'), 'unit_2': i18n.get('celsius')},
        {'id': i18n.get('specific_mass_fuel_burning_rate'),
            'var': 'm', 'unit_1': data.get('accident_fire_pool_mass_burning_rate'), 'unit_2': i18n.get('kg_per_m_square_in_sec')},
        # {'id': i18n.get('specific_heat_of_combustion'), 'var': 'Hсг',
        #     'unit_1': data.get(
        #     'accident_fire_pool_heat_of_combustion'), 'unit_2': i18n.get('kJ_per_kg')},
        {'id': i18n.get('substance'), 'var': '-', 'unit_1': i18n.get(subst), 'unit_2': '-'}]

    media = get_data_table(data=data_out, headers=headers, label=label)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*kb_edit_pool, i18n=i18n, param_back=True, back_data='back_fire_pool', check_role=True, role=role))
    await state.update_data(edit_accident_fire_pool_param='')
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['run_fire_pool', 'run_fire_pool_guest']))
async def run_fire_pool_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    text = i18n.calculation_progress.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_fire_pool', check_role=True, role=role))

    text = i18n.fire_pool.text()
    subst = data.get('accident_fire_pool_sub')
    distance = float(data.get('accident_fire_pool_distance'))
    diameter = compute_characteristic_diameter(
        area=float(data.get("accident_fire_pool_pool_area")))
    air_density = compute_density_gas_phase(
        molar_mass=28.97, temperature=float(data.get('accident_fire_pool_temperature')))
    fuel_density = compute_density_vapor_at_boiling(molar_mass=float(data.get('accident_fire_pool_molar_mass_fuel')),
                                                    boiling_point=float(data.get('accident_fire_pool_boiling_point_fuel')))
    mass_burn_rate = float(data.get('accident_fire_pool_mass_burning_rate'))
    f_pool = AccidentParameters(type_accident='fire_pool')
    nonvelocity = f_pool.compute_nonvelocity(wind=float(data.get(
        'accident_fire_pool_wind')), density_fuel=fuel_density, mass_burn_rate=mass_burn_rate, eff_diameter=diameter)
    flame_angle = f_pool.get_flame_deflection_angle(nonvelocity=nonvelocity)
    flame_lenght = f_pool.compute_lenght_flame_pool(
        nonvelocity=nonvelocity, density_air=air_density, mass_burn_rate=mass_burn_rate, eff_diameter=diameter)
    sep = f_pool.compute_surface_emissive_power(
        eff_diameter=diameter, subst=subst)
    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('fire_pool')
    data_out = [
        {'id': i18n.get('surface_density_thermal_radiation_flame'), 'var': 'Ef',
            'unit_1': f"{sep:.2f}", 'unit_2': i18n.get('kwatt_per_meter_square')},
        {'id': i18n.get('pool_flame_lenght'), 'var': 'L',
            'unit_1': f"{flame_lenght:.2f}", 'unit_2': i18n.get('meter')},
        {'id': i18n.get('pool_flame_angle'), 'var': 'θ',
            'unit_1': f"{flame_angle:.2f}", 'unit_2': i18n.get('degree')},
        {'id': i18n.get('pool_diameter'), 'var': 'deff',
            'unit_1': f"{diameter:.2f}", 'unit_2': i18n.get('meter')},
        {'id': i18n.get('saturated_fuel_vapor_density_at_boiling_point'), 'var': 'ρп',
            'unit_1': f"{fuel_density:.3f}", 'unit_2': i18n.get('kg_per_m_cub')},
        {'id': i18n.get('pool_distance'), 'var': 'r',
         'unit_1': distance, 'unit_2': i18n.get('meter')},
        {'id': i18n.get('pool_area'), 'var': 'F',  'unit_1': data.get(
            'accident_fire_pool_pool_area'), 'unit_2': i18n.get('meter_square')},
        {'id': i18n.get('wind_velocity'), 'var': 'wₒ',
            'unit_1': data.get('accident_fire_pool_wind'), 'unit_2': i18n.get('m_per_sec')},
        {'id': i18n.get('ambient_air_density'), 'var': 'ρₒ',
            'unit_1': f"{air_density:.2f}", 'unit_2': i18n.get('kg_per_m_cub')},
        {'id': i18n.get('ambient_temperature'), 'var': 'tₒ', 'unit_1': data.get(
            'accident_fire_pool_temperature'), 'unit_2': i18n.get('celsius')},
        # {'id': i18n.get('specific_heat_of_combustion'), 'var': 'Hсг',
        #     'unit_1': data.get(
        #     'accident_fire_pool_heat_of_combustion'), 'unit_2': i18n.get('kJ_per_kg')},
        {'id': i18n.get('specific_mass_fuel_burning_rate'),
            'var': 'm', 'unit_1': mass_burn_rate, 'unit_2': i18n.get('kg_per_m_square_in_sec')},
        {'id': i18n.get('substance'), 'var': '-', 'unit_1': i18n.get(subst), 'unit_2': '-'}]

    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=7)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'plot_fire_pool', i18n=i18n, param_back=True, back_data='back_fire_pool', check_role=False, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'plot_fire_pool')
async def plot_fire_pool_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_fire_pool', check_role=True, role=role))

    data = await state.get_data()
    text = i18n.fire_pool.text()
    subst = data.get('accident_fire_pool_sub')
    distance = float(data.get('accident_fire_pool_distance'))
    diameter = compute_characteristic_diameter(
        area=float(data.get("accident_fire_pool_pool_area")))
    f_pool = AccidentParameters(type_accident='fire_pool')
    fuel_density = compute_density_gas_phase(molar_mass=float(data.get('accident_fire_pool_molar_mass_fuel')),
                                             temperature=float(data.get('accident_fire_pool_boiling_point_fuel')))
    mass_burn_rate = float(data.get('accident_fire_pool_mass_burning_rate'))
    f_pool = AccidentParameters(type_accident='fire_pool')
    nonvelocity = f_pool.compute_nonvelocity(wind=float(data.get(
        'accident_fire_pool_wind')), density_fuel=fuel_density, mass_burn_rate=mass_burn_rate, eff_diameter=diameter)
    flame_angle = f_pool.get_flame_deflection_angle(nonvelocity=nonvelocity)
    air_density = compute_density_gas_phase(
        molar_mass=28.97, temperature=float(data.get('accident_fire_pool_temperature')))
    flame_lenght = f_pool.compute_lenght_flame_pool(
        nonvelocity=nonvelocity, density_air=air_density, mass_burn_rate=mass_burn_rate, eff_diameter=diameter)
    sep = f_pool.compute_surface_emissive_power(
        eff_diameter=diameter, subst=subst)
    x, y = f_pool.compute_heat_flux(
        eff_diameter=diameter, sep=sep, lenght_flame=flame_lenght, angle=flame_angle)

    # dist_num = f_pool.get_distance_at_sep(x_values=x, y_values=y, sep=4)
    sep_num = f_pool.get_sep_at_distance(
        x_values=x, y_values=y, distance=distance + diameter / 2)

    unit_sep = i18n.get('kwatt_per_meter_square')
    text_annotate = f" q= {sep_num:.1f} {unit_sep}"
    media = get_plot_graph(x_values=x, y_values=y, ylim=max(y) + max(y) * 0.05,
                           add_annotate=True, text_annotate=text_annotate, x_ann=distance + diameter / 2, y_ann=sep_num,
                           label=i18n.get('plot_pool_label'), x_label=i18n.get('distance_label'), y_label=i18n.get('y_pool_label'),
                           add_legend=True, loc_legend=1)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_fire_pool', check_role=True, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['fire_flash', 'back_fire_flash']))
async def fire_flash_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    data.setdefault("edit_accident_fire_flash_param", "1")
    data.setdefault("accident_fire_flash_sub", "gasoline")
    data.setdefault("accident_fire_flash_temperature", "20")
    data.setdefault("accident_fire_flash_lcl", "1.4")
    data.setdefault("accident_fire_flash_mass_fuel", "5")
    data.setdefault("accident_fire_flash_molar_mass_fuel", "100")
    data.setdefault("accident_fire_flash_radius_pool", "1")

    text = i18n.fire_flash.text()
    subst = data.get('accident_fire_flash_sub')
    # f_flash = AccidentParameters(type_accident='fire_flash')
    air_density = compute_density_gas_phase(
        molar_mass=28.97, temperature=float(data.get('accident_fire_flash_temperature')))
    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('fire_flash')
    data_out = [
        {'id': i18n.get('radius_of_the_strait_above_which_an_explosive_zone_is_formed'), 'var': 'r',
            'unit_1': data.get('accident_fire_flash_radius_pool'), 'unit_2': i18n.get('meter')},
        {'id': i18n.get('mass_of_flammable_gases_entering_the_surrounding_space'), 'var': 'mг',  'unit_1': data.get(
            'accident_fire_flash_mass_fuel'), 'unit_2': i18n.get('kilogram')},
        {'id': i18n.get('lower_concentration_limit_of_flame_propagation'),
            'var': 'Cнкпр', 'unit_1': data.get('accident_fire_flash_lcl'), 'unit_2': i18n.get('percent_volume')},
        {'id': i18n.get('ambient_air_density'), 'var': 'ρₒ',
            'unit_1': f"{air_density:.2f}", 'unit_2': i18n.get('kg_per_m_cub')},
        {'id': i18n.get('ambient_temperature'), 'var': 'tₒ', 'unit_1': data.get(
            'accident_fire_flash_temperature'), 'unit_2': i18n.get('celsius')},
        # {'id': i18n.get('substance'), 'var': '-', 'unit_1': i18n.get(subst), 'unit_2': '-'}
    ]

    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_fire_flash', 'run_fire_flash', i18n=i18n, param_back=True, back_data='back_typical_accidents', check_role=True, role=role))
    await state.update_data(data)
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_fire_flash']))
async def edit_fire_flash_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(*kb_edit_flash, i18n=i18n, param_back=True, back_data='back_fire_flash', check_role=True, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_flash_mass', 'edit_flash_lcl']))
async def edit_flash_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    if callback.data == 'edit_flash_mass':
        await state.set_state(FSMFireAccidentForm.edit_fire_flash_mass_state)
    elif callback.data == 'edit_flash_lcl':
        await state.set_state(FSMFireAccidentForm.edit_fire_flash_lcl_state)
    data = await state.get_data()
    state_data = await state.get_state()
    if state_data == FSMFireAccidentForm.edit_fire_flash_mass_state:
        text = i18n.edit_fire_flash.text(fire_flash_param=i18n.get(
            "name_fire_flash_mass"), edit_fire_flash=data.get("accident_fire_flash_mass_fuel", 0))
    elif state_data == FSMFireAccidentForm.edit_fire_flash_lcl_state:
        text = i18n.edit_fire_flash.text(fire_flash_param=i18n.get(
            "name_fire_flash_lcl"), edit_fire_flash=data.get("accident_fire_flash_lcl", 0))
    kb = ['one', 'two', 'three', 'four', 'five', 'six', 'seven',
          'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready']

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, *kb, i18n=i18n))


@fire_accident_router.callback_query(StateFilter(*SFilter_fire_flash), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'dooble_zero', 'point', 'clear']))
async def edit_fire_flash_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    if state_data == FSMFireAccidentForm.edit_fire_flash_mass_state:
        fire_flash_param = i18n.get("name_fire_flash_mass")
    elif state_data == FSMFireAccidentForm.edit_fire_flash_lcl_state:
        fire_flash_param = i18n.get("name_fire_flash_lcl")

    edit_data = await state.get_data()
    if callback.data == 'clear':
        await state.update_data(edit_accident_fire_flash_param="")
        edit_d = await state.get_data()
        edit_data = edit_d.get('edit_accident_fire_flash_param', 1)
        text = i18n.edit_fire_flash.text(
            fire_flash_param=fire_flash_param, edit_fire_flash=edit_data)

    else:
        edit_param_1 = edit_data.get('edit_accident_fire_flash_param')
        edit_sum = edit_param_1 + i18n.get(callback.data)
        await state.update_data(edit_accident_fire_flash_param=edit_sum)
        edit_data = await state.get_data()
        edit_param = edit_data.get('edit_accident_fire_flash_param', 0)
        text = i18n.edit_fire_flash.text(
            fire_flash_param=fire_flash_param, edit_fire_flash=edit_param)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready', i18n=i18n))


@fire_accident_router.callback_query(StateFilter(*SFilter_fire_flash), F.data.in_(['ready']))
async def edit_fire_flash_param_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    state_data = await state.get_state()
    data = await state.get_data()
    value = data.get("edit_accident_fire_flash_param")
    if state_data == FSMFireAccidentForm.edit_fire_flash_mass_state:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(accident_fire_flash_mass_fuel=value)
        else:
            await state.update_data(accident_fire_flash_mass_fuel=10)
    elif state_data == FSMFireAccidentForm.edit_fire_flash_lcl_state:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(accident_fire_flash_lcl=value)
        else:
            await state.update_data(accident_fire_flash_lcl=1.4)

    data = await state.get_data()
    text = i18n.fire_flash.text()
    subst = data.get('accident_fire_flash_sub')
    # f_flash = AccidentParameters(type_accident='fire_flash')
    lcl = float(data.get('accident_fire_flash_lcl'))
    air_density = compute_density_gas_phase(
        molar_mass=28.97, temperature=float(data.get('accident_fire_flash_temperature')))
    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('fire_flash')
    data_out = [
        {'id': i18n.get('radius_of_the_strait_above_which_an_explosive_zone_is_formed'), 'var': 'r',
            'unit_1': data.get('accident_fire_flash_radius_pool'), 'unit_2': i18n.get('meter')},
        {'id': i18n.get('mass_of_flammable_gases_entering_the_surrounding_space'), 'var': 'mг',  'unit_1': data.get(
            'accident_fire_flash_mass_fuel'), 'unit_2': i18n.get('kilogram')},
        {'id': i18n.get('saturated_fuel_vapor_density_at_boiling_point'),
            'var': 'Cнкпр', 'unit_1': f"{lcl:.2f}", 'unit_2': i18n.get('percent_volume')},
        {'id': i18n.get('ambient_air_density'), 'var': 'ρₒ',
            'unit_1': f"{air_density:.2f}", 'unit_2': i18n.get('kg_per_m_cub')},
        {'id': i18n.get('ambient_temperature'), 'var': 'tₒ', 'unit_1': data.get(
            'accident_fire_flash_temperature'), 'unit_2': i18n.get('celsius')},
        # {'id': i18n.get('substance'), 'var': '-', 'unit_1': i18n.get(subst), 'unit_2': '-'}
    ]

    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_fire_flash', 'run_fire_flash', i18n=i18n, param_back=True, back_data='back_typical_accidents', check_role=True, role=role))
    await state.update_data(edit_accident_fire_flash_param='')


@fire_accident_router.callback_query(F.data == 'run_fire_flash')
async def run_fire_flash_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    text = i18n.calculation_progress.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_fire_flash', check_role=True, role=role))

    text = i18n.fire_flash.text()
    subst = data.get('accident_fire_flash_sub')
    rad_pool = float(data.get('accident_fire_flash_radius_pool'))
    mass = float(data.get('accident_fire_flash_mass_fuel'))
    lcl = float(data.get('accident_fire_flash_lcl'))
    temperature = float(data.get('accident_fire_flash_temperature'))
    molar_mass = float(data.get(
        'accident_fire_flash_molar_mass_fuel'))

    density_fuel = compute_density_gas_phase(
        molar_mass=molar_mass, temperature=temperature)
    # air_density = compute_density_gas_phase(
    #     molar_mass=28.97, temperature=float(data.get('accident_fire_flash_temperature')))
    f_flash = AccidentParameters(type_accident='fire_flash')
    radius_LFL = f_flash.compute_radius_LFL(
        density=density_fuel, mass=mass, clfl=lcl)
    height_LFL = f_flash.compute_height_LFL(
        density=density_fuel, mass=mass, clfl=lcl)

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('fire_flash')
    data_out = [
        {'id': i18n.get('radius_zone_Rf'), 'var': i18n.get('radius_Rf'),
            'unit_1': f"{(radius_LFL if radius_LFL>rad_pool else rad_pool) * 1.2:.2f}", 'unit_2': i18n.get('meter')},
        {'id': i18n.get('height_zone_LFL'), 'var': i18n.get('height_LFL'),
            'unit_1': f"{height_LFL:.2f}", 'unit_2': i18n.get('meter')},
        {'id': i18n.get('radius_zone_LFL'), 'var': i18n.get('radius_LFL'),
            'unit_1': f"{(radius_LFL if radius_LFL>rad_pool else rad_pool):.2f}", 'unit_2': i18n.get('meter')},
        {'id': i18n.get('density_flammable_gases_at_ambient_temperature'),
            'var': 'ρг', 'unit_1': f"{density_fuel:.3f}", 'unit_2': i18n.get('kg_per_m_cub')},
        # {'id': i18n.get('radius_of_the_strait_above_which_an_explosive_zone_is_formed'), 'var': 'r',
        #     'unit_1': f"{rad_pool:.2f}", 'unit_2': i18n.get('meter')},
        {'id': i18n.get('mass_of_flammable_gases_entering_the_surrounding_space'),
         'var': 'mг',  'unit_1': mass, 'unit_2': i18n.get('kilogram')},
        {'id': i18n.get('lower_concentration_limit_of_flame_propagation'),
            'var': i18n.get('lower_concentration_limit'), 'unit_1': f"{lcl:.2f}", 'unit_2': i18n.get('percent_volume')},
        # {'id': i18n.get('ambient_air_density'), 'var': 'ρₒ',
        #     'unit_1': f"{air_density:.2f}", 'unit_2': i18n.get('kg_per_m_cub')},
        {'id': i18n.get('ambient_temperature'), 'var': 'tₒ',
         'unit_1': temperature, 'unit_2': i18n.get('celsius')},
        # {'id': i18n.get('substance'), 'var': '-', 'unit_1': i18n.get(subst), 'unit_2': '-'}
    ]

    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=4)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_fire_flash', check_role=True, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['cloud_explosion', 'back_cloud_explosion']))
async def cloud_explosion_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    data.setdefault("edit_accident_cloud_explosion_param", "1")
    data.setdefault("accident_cloud_explosion_sub", "Бензин")
    data.setdefault("accident_cloud_explosion_class_fuel", "3")
    data.setdefault("accident_cloud_explosion_correction_parameter", "1.0")
    data.setdefault("accident_cloud_explosion_class_space", "3")
    data.setdefault("accident_cloud_explosion_mass_fuel", "1890")
    data.setdefault("accident_cloud_explosion_coef_z", "0.1")
    data.setdefault("accident_cloud_explosion_heat_combustion", "44000")
    data.setdefault("accident_cloud_explosion_expl_cond", "above_surface")
    data.setdefault("accident_cloud_explosion_distance", "70")
    data.setdefault("accident_cloud_explosion_state_fuel", "gas")
    data.setdefault("accident_cloud_explosion_stc_coef_oxygen", "9.953")
    data.setdefault("accident_cloud_explosion_methodology", "methodology_404")
    await state.update_data(data)
    data = await state.get_data()
    text = i18n.cloud_explosion.text()
    subst = data.get('accident_cloud_explosion_state_fuel')
    methodology = data.get('accident_cloud_explosion_methodology')
    mass = float(data.get('accident_cloud_explosion_mass_fuel'))
    stc_coef_oxygen = float(
        data.get('accident_cloud_explosion_stc_coef_oxygen'))
    class_fuel = int(data.get('accident_cloud_explosion_class_fuel'))
    class_space = int(data.get('accident_cloud_explosion_class_space'))
    distance = float(data.get('accident_cloud_explosion_distance'))
    cloud_exp = AccidentParameters(type_accident='cloud_explosion')
    mode_expl = cloud_exp.get_mode_explosion(
        class_fuel=class_fuel, class_space=class_space)

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('cloud_explosion')
    data_out = [
        {'id': i18n.get('cloud_explosion_methodology'),
            'var': '-',
            'unit_1': i18n.get(methodology),
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_distance'),
            'var': 'R',
            'unit_1': f"{distance:.1f}",
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('cloud_explosion_mass_fuel'),
            'var': 'm',
            'unit_1': f"{mass:.1f}",
            'unit_2': i18n.get('kilogram')},
        {'id': i18n.get('cloud_explosion_coefficient_z'),
            'var': 'Z',
            'unit_1': data.get('accident_cloud_explosion_coef_z'),
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_cond_ground'),
            'var': '-',
            'unit_1': i18n.get(data.get(
                'accident_cloud_explosion_expl_cond')),
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_mode_expl'),
            'var': '-',
            'unit_1': f"{mode_expl:.0f}",
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_class_space'),
            'var': '-',
            'unit_1': data.get('accident_cloud_explosion_class_space'),
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_class_fuel'),
            'var': '-',
            'unit_1': data.get('accident_cloud_explosion_class_fuel'),
            'unit_2': '-'},
        {'id': i18n.get('stoichiometric_coefficient_for_oxygen'),
            'var': 'k',
            'unit_1': f"{stc_coef_oxygen:.3f}",
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_correction_parameter'),
            'var': 'β',
            'unit_1': data.get('accident_cloud_explosion_correction_parameter'),
            'unit_2': '-'},
        # {'id': i18n.get('cloud_explosion_heat_combustion'),
        #     'var': 'Eуд0',
        #     'unit_1': data.get('accident_cloud_explosion_heat_combustion'),
        #     'unit_2': i18n.get('kJ_per_kg')},
        {'id': i18n.get('cloud_explosion_state_fuel'),
            'var': '-',
            'unit_1': i18n.get(subst),
            'unit_2': '-'},]

    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_cloud_explosion', 'run_cloud_explosion', i18n=i18n, param_back=True, back_data='back_typical_accidents', check_role=True, role=role))


@fire_accident_router.callback_query(F.data.in_(['edit_cloud_explosion', 'back_edit_cloud_explosion']))
async def edit_cloud_explosion_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(*kb_edit_cloud_explosion, i18n=i18n, param_back=True, back_data='back_cloud_explosion', check_role=True, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_cloud_explosion_state']))
async def cloud_explosion_state_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, 'cloud_explosion_state_gas', 'cloud_explosion_state_dust', i18n=i18n, param_back=True, back_data='back_edit_cloud_explosion',))


@fire_accident_router.callback_query(F.data.in_(['edit_cloud_explosion_class_fuel']))
async def cloud_explosion_class_fuel_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(4, 'class_fuel_first', 'class_fuel_second', 'class_fuel_third', 'class_fuel_fourth', i18n=i18n, param_back=True, back_data='back_edit_cloud_explosion',))


@fire_accident_router.callback_query(F.data.in_(['edit_cloud_explosion_class_space']))
async def cloud_explosion_class_space_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(4, 'class_space_first', 'class_space_second', 'class_space_third', 'class_space_fourth', i18n=i18n, param_back=True, back_data='back_edit_cloud_explosion',))


@fire_accident_router.callback_query(F.data.in_(['edit_cloud_explosion_expl_cond']))
async def cloud_explosion_cond_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, 'above_surface', 'on_surface', i18n=i18n, param_back=True, back_data='back_edit_cloud_explosion',))


@fire_accident_router.callback_query(F.data.in_(['cloud_explosion_methodology']))
async def cloud_explosion_methodology_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, 'methodology_404', 'methodology_2024', i18n=i18n, param_back=True, back_data='back_edit_cloud_explosion',))


@fire_accident_router.callback_query(F.data.in_(['cloud_explosion_state_gas', 'cloud_explosion_state_dust', 'class_fuel_first', 'class_fuel_second', 'class_fuel_third', 'class_fuel_fourth', 'class_space_first', 'class_space_second', 'class_space_third', 'class_space_fourth', 'above_surface', 'on_surface', 'methodology_404', 'methodology_2024']))
async def cloud_explosion_state_close(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.update_data.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_edit_cloud_explosion', check_role=True, role=role))

    call_data = callback.data
    if call_data == 'cloud_explosion_state_gas':
        await state.update_data(accident_cloud_explosion_state_fuel='gas')
    elif call_data == 'cloud_explosion_state_dust':
        await state.update_data(accident_cloud_explosion_state_fuel='dust')
    elif call_data == 'class_fuel_first':
        await state.update_data(accident_cloud_explosion_class_fuel='1')
    elif call_data == 'class_fuel_second':
        await state.update_data(accident_cloud_explosion_class_fuel='2')
    elif call_data == 'class_fuel_third':
        await state.update_data(accident_cloud_explosion_class_fuel='3')
    elif call_data == 'class_fuel_fourth':
        await state.update_data(accident_cloud_explosion_class_fuel='4')
    elif call_data == 'class_space_first':
        await state.update_data(accident_cloud_explosion_class_space='1')
    elif call_data == 'class_space_second':
        await state.update_data(accident_cloud_explosion_class_space='2')
    elif call_data == 'class_space_third':
        await state.update_data(accident_cloud_explosion_class_space='3')
    elif call_data == 'class_space_fourth':
        await state.update_data(accident_cloud_explosion_class_space='4')
    elif call_data == 'above_surface':
        await state.update_data(accident_cloud_explosion_expl_cond='above_surface')
    elif call_data == 'on_surface':
        await state.update_data(accident_cloud_explosion_expl_cond='on_surface')
    elif call_data == 'methodology_404':
        await state.update_data(accident_cloud_explosion_methodology='methodology_404')
    elif call_data == 'methodology_2024':
        await state.update_data(accident_cloud_explosion_methodology='methodology_2024')
    # data = await state.get_data()
    # data.setdefault("edit_accident_cloud_explosion_param", "1")
    # data.setdefault("accident_cloud_explosion_sub", "Бензин")
    # data.setdefault("accident_cloud_explosion_class_fuel", "3")
    # data.setdefault("accident_cloud_explosion_correction_parameter", "1.0")
    # data.setdefault("accident_cloud_explosion_class_space", "3")
    # data.setdefault("accident_cloud_explosion_mass_fuel", "1890")
    # data.setdefault("accident_cloud_explosion_coef_z", "0.1")
    # data.setdefault("accident_cloud_explosion_heat_combustion", "44000")
    # data.setdefault("accident_cloud_explosion_expl_cond", "above_surface")
    # data.setdefault("accident_cloud_explosion_distance", "70")
    # data.setdefault("accident_cloud_explosion_state_fuel", "gas")
    # data.setdefault("accident_cloud_explosion_stc_coef_oxygen", "2.0")
    # await state.update_data(data)
    data = await state.get_data()
    text = i18n.cloud_explosion.text()
    subst = data.get('accident_cloud_explosion_state_fuel')
    methodology = data.get('accident_cloud_explosion_methodology')
    mass = float(data.get('accident_cloud_explosion_mass_fuel'))
    stc_coef_oxygen = float(
        data.get('accident_cloud_explosion_stc_coef_oxygen'))
    class_fuel = int(data.get('accident_cloud_explosion_class_fuel'))
    class_space = int(data.get('accident_cloud_explosion_class_space'))
    distance = float(data.get('accident_cloud_explosion_distance'))
    cloud_exp = AccidentParameters(type_accident='cloud_explosion')
    mode_expl = cloud_exp.get_mode_explosion(
        class_fuel=class_fuel, class_space=class_space)

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('cloud_explosion')
    data_out = [
        {'id': i18n.get('cloud_explosion_methodology'),
            'var': '-',
            'unit_1': i18n.get(methodology),
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_distance'),
            'var': 'R',
            'unit_1': f"{distance:.1f}",
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('cloud_explosion_mass_fuel'),
            'var': 'm',
            'unit_1': f"{mass:.2f}",
            'unit_2': i18n.get('kilogram')},
        {'id': i18n.get('cloud_explosion_coefficient_z'),
            'var': 'Z',
            'unit_1': data.get('accident_cloud_explosion_coef_z'),
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_cond_ground'),
            'var': '-',
            'unit_1': i18n.get(data.get(
                'accident_cloud_explosion_expl_cond')),
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_mode_expl'),
            'var': '-',
            'unit_1': f"{mode_expl:.0f}",
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_class_space'),
            'var': '-',
            'unit_1': data.get('accident_cloud_explosion_class_space'),
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_class_fuel'),
            'var': '-',
            'unit_1': data.get('accident_cloud_explosion_class_fuel'),
            'unit_2': '-'},
        {'id': i18n.get('stoichiometric_coefficient_for_oxygen'),
            'var': 'k',
            'unit_1': f"{stc_coef_oxygen:.2f}",
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_correction_parameter'),
            'var': 'β',
            'unit_1': data.get('accident_cloud_explosion_correction_parameter'),
            'unit_2': '-'},
        # {'id': i18n.get('cloud_explosion_heat_combustion'),
        #     'var': 'Eуд0',
        #     'unit_1': data.get('accident_cloud_explosion_heat_combustion'),
        #     'unit_2': i18n.get('kJ_per_kg')},
        {'id': i18n.get('cloud_explosion_state_fuel'),
            'var': '-',
            'unit_1': i18n.get(subst),
            'unit_2': '-'}]

    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*kb_edit_cloud_explosion, i18n=i18n, param_back=True, back_data='back_cloud_explosion', check_role=True, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_cloud_explosion_correction_parameter',
                                                 'edit_cloud_explosion_stc_coef_oxygen',
                                                 'edit_cloud_explosion_coef_z',
                                                 'edit_cloud_explosion_mass_fuel',
                                                 'edit_cloud_explosion_distance']))
async def edit_cloud_explosion_num_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    if callback.data == 'edit_cloud_explosion_correction_parameter':
        await state.set_state(FSMFireAccidentForm.edit_cloud_explosion_correction_parameter_state)
    elif callback.data == 'edit_cloud_explosion_stc_coef_oxygen':
        await state.set_state(FSMFireAccidentForm.edit_cloud_explosion_stc_coef_oxygen_state)
    elif callback.data == 'edit_cloud_explosion_coef_z':
        await state.set_state(FSMFireAccidentForm.edit_cloud_explosion_coef_z_state)
    elif callback.data == 'edit_cloud_explosion_mass_fuel':
        await state.set_state(FSMFireAccidentForm.edit_cloud_explosion_mass_state)
    elif callback.data == 'edit_cloud_explosion_distance':
        await state.set_state(FSMFireAccidentForm.edit_cloud_explosion_distance_state)

    data = await state.get_data()
    state_data = await state.get_state()

    if state_data == FSMFireAccidentForm.edit_cloud_explosion_correction_parameter_state:
        text = i18n.edit_cloud_explosion.text(cloud_explosion_param=i18n.get(
            "name_cloud_explosion_correction_parameter"), edit_cloud_explosion=data.get("accident_cloud_explosion_correction_parameter", 0))
    elif state_data == FSMFireAccidentForm.edit_cloud_explosion_stc_coef_oxygen_state:
        text = i18n.edit_cloud_explosion.text(cloud_explosion_param=i18n.get(
            "name_cloud_explosion_stc_coef_oxygen"), edit_cloud_explosion=data.get("accident_cloud_explosion_stc_coef_oxygen", 0))

    elif state_data == FSMFireAccidentForm.edit_cloud_explosion_coef_z_state:
        text = i18n.edit_cloud_explosion.text(cloud_explosion_param=i18n.get(
            "name_cloud_explosion_coef_z"), edit_cloud_explosion=data.get("accident_cloud_explosion_coef_z", 0))

    elif state_data == FSMFireAccidentForm.edit_cloud_explosion_mass_state:
        text = i18n.edit_cloud_explosion.text(cloud_explosion_param=i18n.get(
            "name_cloud_explosion_mass_fuel"), edit_cloud_explosion=data.get("accident_cloud_explosion_mass_fuel", 0))

    elif state_data == FSMFireAccidentForm.edit_cloud_explosion_distance_state:
        text = i18n.edit_cloud_explosion.text(cloud_explosion_param=i18n.get(
            "name_cloud_explosion_distance"), edit_cloud_explosion=data.get("accident_cloud_explosion_distance", 0))

    kb = ['one', 'two', 'three', 'four', 'five', 'six', 'seven',
          'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready']

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, *kb, i18n=i18n))


@fire_accident_router.callback_query(StateFilter(*SFilter_cloud_explosion), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'dooble_zero', 'point', 'clear']))
async def edit_cloud_explosion_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    if state_data == FSMFireAccidentForm.edit_cloud_explosion_correction_parameter_state:
        cloud_explosion_param = i18n.get(
            "name_cloud_explosion_correction_parameter")
    elif state_data == FSMFireAccidentForm.edit_cloud_explosion_stc_coef_oxygen_state:
        cloud_explosion_param = i18n.get(
            "name_cloud_explosion_stc_coef_oxygen")

    elif state_data == FSMFireAccidentForm.edit_cloud_explosion_coef_z_state:
        cloud_explosion_param = i18n.get("edit_cloud_explosion_coef_z_state")

    elif state_data == FSMFireAccidentForm.edit_cloud_explosion_mass_state:
        cloud_explosion_param = i18n.get("name_cloud_explosion_mass_fuel")

    elif state_data == FSMFireAccidentForm.edit_cloud_explosion_distance_state:
        cloud_explosion_param = i18n.get("name_cloud_explosion_distance")

    edit_data = await state.get_data()
    if callback.data == 'clear':
        await state.update_data(edit_accident_cloud_explosion_param="")
        edit_d = await state.get_data()
        edit_data = edit_d.get('edit_accident_cloud_explosion_param', 1)
        text = i18n.edit_cloud_explosion.text(
            cloud_explosion_param=cloud_explosion_param, edit_cloud_explosion=edit_data)

    else:
        edit_param_1 = edit_data.get('edit_accident_cloud_explosion_param')
        edit_sum = edit_param_1 + i18n.get(callback.data)
        await state.update_data(edit_accident_cloud_explosion_param=edit_sum)
        edit_data = await state.get_data()
        edit_param = edit_data.get('edit_accident_cloud_explosion_param', 0)
        text = i18n.edit_cloud_explosion.text(
            cloud_explosion_param=cloud_explosion_param, edit_cloud_explosion=edit_param)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready', i18n=i18n))


@fire_accident_router.callback_query(StateFilter(*SFilter_cloud_explosion), F.data.in_(['ready']))
async def edit_cloud_explosion_param_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    state_data = await state.get_state()
    data = await state.get_data()
    value = data.get("edit_accident_cloud_explosion_param")

    if state_data == FSMFireAccidentForm.edit_cloud_explosion_correction_parameter_state:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(accident_cloud_explosion_correction_parameter=value)
        else:
            await state.update_data(accident_cloud_explosion_correction_parameter=1.0)
    elif state_data == FSMFireAccidentForm.edit_cloud_explosion_stc_coef_oxygen_state:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(accident_cloud_explosion_stc_coef_oxygen=value)
        else:
            await state.update_data(accident_cloud_explosion_stc_coef_oxygen=2.0)

    elif state_data == FSMFireAccidentForm.edit_cloud_explosion_coef_z_state:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(accident_cloud_explosion_coef_z=value)
        else:
            await state.update_data(accident_cloud_explosion_coef_z=0.1)

    elif state_data == FSMFireAccidentForm.edit_cloud_explosion_mass_state:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(accident_cloud_explosion_mass_fuel=value)
        else:
            await state.update_data(accident_cloud_explosion_mass_fuel=100.0)

    elif state_data == FSMFireAccidentForm.edit_cloud_explosion_distance_state:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(accident_cloud_explosion_distance=value)
        else:
            await state.update_data(accident_cloud_explosion_distance=30.0)

    data = await state.get_data()
    text = i18n.cloud_explosion.text()
    subst = data.get('accident_cloud_explosion_state_fuel')
    methodology = data.get('accident_cloud_explosion_methodology')
    mass = float(data.get('accident_cloud_explosion_mass_fuel'))
    stc_coef_oxygen = float(
        data.get('accident_cloud_explosion_stc_coef_oxygen'))
    class_fuel = int(data.get('accident_cloud_explosion_class_fuel'))
    class_space = int(data.get('accident_cloud_explosion_class_space'))
    distance = float(data.get('accident_cloud_explosion_distance'))
    cloud_exp = AccidentParameters(type_accident='cloud_explosion')
    mode_expl = cloud_exp.get_mode_explosion(
        class_fuel=class_fuel, class_space=class_space)

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('cloud_explosion')
    data_out = [
        {'id': i18n.get('cloud_explosion_methodology'),
            'var': '-',
            'unit_1': i18n.get(methodology),
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_distance'),
            'var': 'R',
            'unit_1': f"{distance:.1f}",
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('cloud_explosion_mass_fuel'),
            'var': 'm',
            'unit_1': f"{mass:.1f}",
            'unit_2': i18n.get('kilogram')},
        {'id': i18n.get('cloud_explosion_coefficient_z'),
            'var': 'Z',
            'unit_1': data.get('accident_cloud_explosion_coef_z'),
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_cond_ground'),
            'var': '-',
            'unit_1': i18n.get(data.get(
                'accident_cloud_explosion_expl_cond')),
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_mode_expl'),
            'var': '-',
            'unit_1': f"{mode_expl:.0f}",
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_class_space'),
            'var': '-',
            'unit_1': data.get('accident_cloud_explosion_class_space'),
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_class_fuel'),
            'var': '-',
            'unit_1': data.get('accident_cloud_explosion_class_fuel'),
            'unit_2': '-'},
        {'id': i18n.get('stoichiometric_coefficient_for_oxygen'),
            'var': 'k',
            'unit_1': f"{stc_coef_oxygen:.3f}",
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_correction_parameter'),
            'var': 'β',
            'unit_1': data.get('accident_cloud_explosion_correction_parameter'),
            'unit_2': '-'},
        # {'id': i18n.get('cloud_explosion_heat_combustion'),
        #     'var': 'Eуд0',
        #     'unit_1': data.get('accident_cloud_explosion_heat_combustion'),
        #     'unit_2': i18n.get('kJ_per_kg')},
        {'id': i18n.get('cloud_explosion_state_fuel'),
            'var': '-',
            'unit_1': i18n.get(subst),
            'unit_2': '-'}]

    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*kb_edit_cloud_explosion, i18n=i18n, param_back=True, back_data='back_cloud_explosion', check_role=True, role=role))
    await state.update_data(edit_accident_cloud_explosion_param='')


@fire_accident_router.callback_query(F.data.in_(['run_cloud_explosion', 'run_cloud_explosion_guest']))
async def run_cloud_explosion_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    text = i18n.calculation_progress.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_cloud_explosion', check_role=True, role=role))

    methodology = True if data.get(
        'accident_cloud_explosion_methodology') == 'methodology_2024' else False
    mass = float(data.get('accident_cloud_explosion_mass_fuel'))
    coef_z = float(data.get('accident_cloud_explosion_coef_z'))
    class_fuel = int(data.get('accident_cloud_explosion_class_fuel'))
    class_space = int(data.get('accident_cloud_explosion_class_space'))
    heat = float(data.get('accident_cloud_explosion_heat_combustion'))
    beta = float(data.get('accident_cloud_explosion_correction_parameter'))
    distance = float(data.get('accident_cloud_explosion_distance'))
    expl_sf = True if data.get(
        'accident_cloud_explosion_expl_cond') == 'on_surface' else False
    stc_coef_oxygen = float(
        data.get('accident_cloud_explosion_stc_coef_oxygen'))
    # stc_coef_oxygen = compute_stoichiometric_coefficient_with_oxygen(
    #     n_C=6.911, n_H=12.168)
    stc_coef_fuel = compute_stoichiometric_coefficient_with_fuel(
        beta=stc_coef_oxygen)

    cloud_exp = AccidentParameters()
    eff_energy = cloud_exp.compute_eff_energy_reserve(
        phi_fuel=stc_coef_fuel, phi_stc=stc_coef_fuel, mass_gas_phase=mass * coef_z, explosion_superficial=expl_sf)
    mode_expl = cloud_exp.get_mode_explosion(
        class_fuel=class_fuel, class_space=class_space)
    ufront = cloud_exp.compute_velocity_flame(
        cloud_combustion_mode=mode_expl, mass_gas_phase=mass * coef_z)

    nondimensional_distance, nondimensional_pressure, overpres, nondimensional_impuls, impuls = cloud_exp.compute_overpres_inclosed(
        energy_reserve=eff_energy, distance_run=False, distance=distance, ufront=ufront, mode_explosion=mode_expl, new_methodology=methodology)

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('cloud_explosion')
    data_out = [
        {'id': i18n.get('impuls_overpressure'),
            'var': 'I+',
            'unit_1': f"{impuls:.2e}",
            'unit_2': i18n.get('pascal_in_sec')},
        {'id': i18n.get('overpressure'),
            'var': 'ΔP',
            'unit_1': f"{overpres:.2e}",
            'unit_2': i18n.get('pascal')},
        {'id': i18n.get('cloud_explosion_nondimensional_impuls'),
            'var': 'Ix',
            'unit_1': f"{nondimensional_impuls:.3f}",
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_nondimensional_pressure'),
            'var': 'px',
            'unit_1': f"{nondimensional_pressure:.3f}",
            'unit_2': '-'},
        {'id': i18n.get('cloud_explosion_nondimensional_distance'),
            'var': 'Rx',
            'unit_1': f"{nondimensional_distance:.3f}",
            'unit_2': '-'},
        {'id': i18n.get('max_speed_of_flame_front'),
            'var': 'u',
            'unit_1': f"{ufront:.2f}",
            'unit_2': i18n.get('m_per_sec')},
        # {'id': i18n.get('apparent_speed_of_flame_front'),
        #     'var': 'uр',
        #     'unit_1': f"{103.2:.2f}",
        #     'unit_2': i18n.get('m_per_sec')},
        {'id': i18n.get('cloud_explosion_efficient_energy_reserve'),
            'var': 'E',
            'unit_1': f"{2 * (mass * coef_z) * (heat * beta) * 1000:.2e}",
            'unit_2': i18n.get('Joule')},
        {'id': i18n.get('cloud_explosion_stoichiometric_fuel'),
            'var': 'Cст',
            'unit_1': f"{stc_coef_fuel:.3f}",
            'unit_2': i18n.get('percent_volume')},
        # {'id': i18n.get('stoichiometric_coefficient_for_oxygen'),
        #     'var': 'β',
        #     'unit_1': f"{stc_coef_oxygen:.3f}",
        #     'unit_2': '-'},
        # {'id': i18n.get('cloud_explosion_spec_heat_combustion'),
        #     'var': 'Eуд',
        #     'unit_1': f"{(heat * beta):.1f}",
        #     'unit_2': i18n.get('kJ_per_kg')},
        {'id': i18n.get('cloud_explosion_mass_expl'),
            'var': 'Mт',
            'unit_1': f"{(mass * coef_z):.2f}",
            'unit_2': i18n.get('kilogram')}]

    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=7)
    text = i18n.cloud_explosion_result.text(distance=distance)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'plot_accident_cloud_explosion_pressure', 'plot_accident_cloud_explosion_impuls', i18n=i18n, param_back=True, back_data='back_cloud_explosion', check_role=False, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['plot_accident_cloud_explosion_pressure']))
async def plot_cloud_explosion_pres_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_cloud_explosion', check_role=True, role=role))
    data = await state.get_data()
    text = i18n.cloud_explosion.text()

    methodology = True if data.get(
        'accident_cloud_explosion_methodology') == 'methodology_2024' else False
    mass = float(data.get('accident_cloud_explosion_mass_fuel'))
    coef_z = float(data.get('accident_cloud_explosion_coef_z'))
    class_fuel = int(data.get('accident_cloud_explosion_class_fuel'))
    class_space = int(data.get('accident_cloud_explosion_class_space'))
    heat = float(data.get('accident_cloud_explosion_heat_combustion'))
    beta = float(data.get('accident_cloud_explosion_correction_parameter'))
    distance = float(data.get('accident_cloud_explosion_distance'))
    expl_sf = True if data.get(
        'accident_cloud_explosion_expl_cond') == 'on_surface' else False
    stc_coef_oxygen = compute_stoichiometric_coefficient_with_oxygen(
        n_C=6.911, n_H=12.168)
    stc_coef_fuel = compute_stoichiometric_coefficient_with_fuel(
        beta=stc_coef_oxygen)

    cloud_exp = AccidentParameters()
    eff_energy = cloud_exp.compute_eff_energy_reserve(
        phi_fuel=stc_coef_fuel, phi_stc=stc_coef_fuel, mass_gas_phase=mass * coef_z, explosion_superficial=expl_sf)
    mode_expl = cloud_exp.get_mode_explosion(
        class_fuel=class_fuel, class_space=class_space)
    ufront = cloud_exp.compute_velocity_flame(
        cloud_combustion_mode=mode_expl, mass_gas_phase=mass * coef_z)

    dist, overpres, impuls = cloud_exp.compute_overpres_inclosed(
        energy_reserve=eff_energy, distance_run=True, distance=distance, ufront=ufront, mode_explosion=mode_expl, new_methodology=methodology)

    value = cloud_exp.get_sep_at_distance(
        x_values=dist, y_values=overpres, distance=distance)

    unit_p = i18n.get('pascal')
    unit_p1 = i18n.get('kg_per_santimeter_square')
    text_annotate = f" ΔP\n = {value:.2e} {unit_p}\n = {(value*0.000010197):.2e} {unit_p1}"

    media = get_plot_graph(x_values=dist, y_values=overpres, ylim=max(overpres) + max(overpres) * 0.05,
                           add_annotate=True, text_annotate=text_annotate, x_ann=distance, y_ann=value,
                           label=i18n.get(
                               'plot_pressure_label'),
                           x_label=i18n.get('distance_label'),
                           y_label=i18n.get(
                               'plot_pressure_legend'),
                           add_legend=True, loc_legend=1)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'plot_accident_cloud_explosion_impuls', i18n=i18n, param_back=True, back_data='back_cloud_explosion', check_role=True, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['plot_accident_cloud_explosion_impuls']))
async def plot_cloud_explosion_impuls_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_cloud_explosion', check_role=True, role=role))
    data = await state.get_data()
    text = i18n.cloud_explosion.text()

    methodology = True if data.get(
        'accident_cloud_explosion_methodology') == 'methodology_2024' else False
    mass = float(data.get('accident_cloud_explosion_mass_fuel'))
    coef_z = float(data.get('accident_cloud_explosion_coef_z'))
    class_fuel = int(data.get('accident_cloud_explosion_class_fuel'))
    class_space = int(data.get('accident_cloud_explosion_class_space'))
    heat = float(data.get('accident_cloud_explosion_heat_combustion'))
    beta = float(data.get('accident_cloud_explosion_correction_parameter'))
    distance = float(data.get('accident_cloud_explosion_distance'))
    expl_sf = True if data.get(
        'accident_cloud_explosion_expl_cond') == 'on_surface' else False
    stc_coef_oxygen = compute_stoichiometric_coefficient_with_oxygen(
        n_C=6.911, n_H=12.168)
    stc_coef_fuel = compute_stoichiometric_coefficient_with_fuel(
        beta=stc_coef_oxygen)

    cloud_exp = AccidentParameters()
    eff_energy = cloud_exp.compute_eff_energy_reserve(
        phi_fuel=stc_coef_fuel, phi_stc=stc_coef_fuel, mass_gas_phase=mass * coef_z, explosion_superficial=expl_sf)
    mode_expl = cloud_exp.get_mode_explosion(
        class_fuel=class_fuel, class_space=class_space)
    ufront = cloud_exp.compute_velocity_flame(
        cloud_combustion_mode=mode_expl, mass_gas_phase=mass * coef_z)

    dist, overpres, impuls = cloud_exp.compute_overpres_inclosed(
        energy_reserve=eff_energy, distance_run=True, distance=distance, ufront=ufront, mode_explosion=mode_expl, new_methodology=methodology)

    value = cloud_exp.get_sep_at_distance(
        x_values=dist, y_values=impuls, distance=distance)

    unit = i18n.get('pascal_in_sec')
    text_annotate = f" I+ = {value:.1f} {unit}"
    media = get_plot_graph(x_values=dist, y_values=impuls, ylim=max(impuls) + max(impuls) * 0.05,
                           add_annotate=True, text_annotate=text_annotate, x_ann=distance, y_ann=value,
                           label=i18n.get(
                               'plot_impuls_label'),
                           x_label=i18n.get('distance_label'),
                           y_label=i18n.get(
                               'plot_impuls_legend'),
                           add_legend=True, loc_legend=1)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'plot_accident_cloud_explosion_pressure', i18n=i18n, param_back=True, back_data='back_cloud_explosion', check_role=True, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['horizontal_jet', 'back_horizontal_jet']))
async def horizontal_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    data.setdefault("accident_horizontal_jet_sub", "Метан")
    data.setdefault("accident_horizontal_jet_mass_rate", "5")
    data.setdefault("accident_horizontal_jet_state", "jet_state_liquid")
    data.setdefault("accident_horizontal_jet_human_distance", "30")
    await state.update_data(data)

    text = i18n.horizontal_jet.text()
    data = await state.get_data()

    jet_state_phase = data.get('accident_horizontal_jet_state')
    k_coef = 15.0 if jet_state_phase == 'jet_state_liquid' else 13.5 if jet_state_phase == 'jet_state_liq_gas_vap' else 12.5
    mass_rate = float(data.get('accident_horizontal_jet_mass_rate'))
    lenght_flame = k_coef * mass_rate ** 0.4
    diameter_flame = 0.15 * lenght_flame

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('horizontal_jet')
    data_out = [
        {'id': i18n.get('jet_human_distance'),
            'var': 'r',
            'unit_1': data.get('accident_horizontal_jet_human_distance'),
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('hjet_flame_width'),
            'var': 'Df',
            'unit_1': f'{diameter_flame:.2f}',
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('hjet_flame_length'),
            'var': 'Lf',
            'unit_1': f'{lenght_flame:.2f}',
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('jet_mass_rate'),
            'var': 'G',
            'unit_1': f'{mass_rate:.2f}',
            'unit_2': i18n.get('kg_per_sec')},
        {'id': i18n.get('empirical_coefficient'),
            'var': 'K',
            'unit_1': k_coef,
            'unit_2': '-'},
        {'id': i18n.get('jet_state_fuel'),
            'var': '-',
            'unit_1': i18n.get(jet_state_phase),
            'unit_2': '-'}]

    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'edit_horizontal_jet',
                                      'plot_horizontal_jet',
                                      i18n=i18n, param_back=True, back_data='back_typical_accidents', check_role=True, role=role))


@fire_accident_router.callback_query(F.data.in_(['plot_horizontal_jet']))
async def horizontal_jet_plot_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      #   'edit_vertical_jet',
                                      #   'plot_vertical_jet',
                                      i18n=i18n, param_back=True, back_data='back_horizontal_jet', check_role=True, role=role))
    data = await state.get_data()

    text = i18n.horizontal_jet.text()

    distance = float(data.get('accident_horizontal_jet_human_distance'))

    jet_state_phase = data.get('accident_horizontal_jet_state')
    k_coef = 15.0 if jet_state_phase == 'jet_state_liquid' else 13.5 if jet_state_phase == 'jet_state_liq_gas_vap' else 12.5
    mass_rate = float(data.get('accident_horizontal_jet_mass_rate'))
    lenght_flame = k_coef * mass_rate ** 0.4
    # diameter_flame = 0.15 * lenght_flame

    h_jet = AccidentParameters()
    x, y = h_jet.compute_heat_jet_fire(lenght_flame=lenght_flame)

    # dist_num = f_ball.get_distance_at_sep(x_values=x, y_values=y, sep=4)
    sep_num = h_jet.get_sep_at_distance(
        x_values=x, y_values=y, distance=distance)

    unit_sep = i18n.get('kwatt_per_meter_square')

    text_annotate = f" q= {sep_num:.1f} {unit_sep} "

    media = get_plot_graph(x_values=x, y_values=y, ylim=max(y) + max(y) * 0.05,
                           add_annotate=True, text_annotate=text_annotate, x_ann=distance, y_ann=sep_num,
                           label=i18n.get('plot_horizontal_jet_label'), x_label=i18n.get('distance_label'), y_label=i18n.get('y_horizontal_jet_label'),
                           add_legend=True, loc_legend=1)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      #   'edit_horizontal_jet',
                                      #   'plot_horizontal_jet',
                                      i18n=i18n, param_back=True, back_data='back_horizontal_jet', check_role=True, role=role))


@fire_accident_router.callback_query(F.data.in_(['edit_horizontal_jet']))
async def edit_horizontal_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(*kb_edit_hjet, i18n=i18n, param_back=True, back_data='back_horizontal_jet', check_role=True, role=role))


@fire_accident_router.callback_query(F.data.in_(['edit_hjet_state']))
async def hjet_state_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, 'horizontal_jet_state_liquid_kb', 'horizontal_jet_state_comp_gas_kb', 'horizontal_jet_state_liq_gas_vap_kb', i18n=i18n))


@fire_accident_router.callback_query(F.data.in_(['horizontal_jet_state_liquid_kb', 'horizontal_jet_state_comp_gas_kb', 'horizontal_jet_state_liq_gas_vap_kb']))
async def horizontal_jet_state_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    # state_data = await state.get_state()
    call_data = callback.data
    if call_data == 'horizontal_jet_state_liquid_kb':
        await state.update_data(accident_horizontal_jet_state='jet_state_liquid')
    elif call_data == 'horizontal_jet_state_comp_gas_kb':
        await state.update_data(accident_horizontal_jet_state='jet_state_comp_gas')
    elif call_data == 'horizontal_jet_state_liq_gas_vap_kb':
        await state.update_data(accident_horizontal_jet_state='jet_state_liq_gas_vap')

    data = await state.get_data()

    text = i18n.horizontal_jet.text()

    jet_state_phase = data.get('accident_horizontal_jet_state')
    k_coef = 15.0 if jet_state_phase == 'jet_state_liquid' else 13.5 if jet_state_phase == 'jet_state_liq_gas_vap' else 12.5
    mass_rate = float(data.get('accident_horizontal_jet_mass_rate'))
    lenght_flame = k_coef * mass_rate ** 0.4
    diameter_flame = 0.15 * lenght_flame

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('horizontal_jet')
    data_out = [
        {'id': i18n.get('jet_human_distance'),
            'var': 'r',
            'unit_1': data.get('accident_horizontal_jet_human_distance'),
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('hjet_flame_width'),
            'var': 'Df',
            'unit_1': f'{diameter_flame:.2f}',
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('hjet_flame_length'),
            'var': 'Lf',
            'unit_1': f'{lenght_flame:.2f}',
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('jet_mass_rate'),
            'var': 'G',
            'unit_1': f'{mass_rate:.2f}',
            'unit_2': i18n.get('kg_per_sec')},
        {'id': i18n.get('empirical_coefficient'),
            'var': 'K',
            'unit_1': k_coef,
            'unit_2': '-'},
        {'id': i18n.get('jet_state_fuel'),
            'var': '-',
            'unit_1': i18n.get(jet_state_phase),
            'unit_2': '-'}]

    media = get_data_table(data=data_out, headers=headers, label=label)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*kb_edit_hjet, i18n=i18n, param_back=True, back_data='back_horizontal_jet'))


# @fire_accident_router.callback_query(F.data.in_(['edit_hjet_mass_rate', 'edit_hjet_distance']))
# async def edit_horizontal_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
#     if callback.data == 'edit_hjet_mass_rate':
#         await state.set_state(FSMFireAccidentForm.edit_horizontal_jet_mass_flow_state)
#     elif callback.data == 'edit_hjet_distance':
#         await state.set_state(FSMFireAccidentForm.edit_horizontal_jet_distance_state)
#     data = await state.get_data()
#     state_data = await state.get_state()
#     if state_data == FSMFireAccidentForm.edit_fire_flash_mass_state:
#         text = i18n.edit_fire_flash.text(fire_flash_param=i18n.get(
#             "name_fire_flash_mass"), edit_fire_flash=data.get("accident_fire_flash_mass_fuel", 0))
#     elif state_data == FSMFireAccidentForm.edit_fire_flash_lcl_state:
#         text = i18n.edit_fire_flash.text(fire_flash_param=i18n.get(
#             "name_fire_flash_lcl"), edit_fire_flash=data.get("accident_fire_flash_lcl", 0))
#     kb = ['one', 'two', 'three', 'four', 'five', 'six', 'seven',
#           'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready']

#     await bot.edit_message_caption(
#         chat_id=callback.message.chat.id,
#         message_id=callback.message.message_id,
#         caption=text,
#         reply_markup=get_inline_cd_kb(3, *kb, i18n=i18n))

@fire_accident_router.callback_query(F.data.in_(['vertical_jet', 'back_vertical_jet']))
async def vertical_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    data.setdefault("accident_vertical_jet_sub", "Метан")
    data.setdefault("accident_vertical_jet_mass_rate", "5")
    data.setdefault("accident_vertical_jet_state", "jet_state_liq_gas_vap")
    data.setdefault("accident_vertical_jet_human_distance", "30")
    await state.update_data(data)

    text = i18n.vertical_jet.text()

    data = await state.get_data()

    jet_state_phase = data.get('accident_vertical_jet_state')
    k_coef = 15.0 if jet_state_phase == 'jet_state_liquid' else 13.5 if jet_state_phase == 'jet_state_liq_gas_vap' else 12.5
    mass_rate = float(data.get('accident_vertical_jet_mass_rate'))
    lenght_flame = k_coef * mass_rate ** 0.4
    diameter_flame = 0.15 * lenght_flame

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('vertical_jet')
    data_out = [
        {'id': i18n.get('jet_human_distance'),
            'var': 'r',
            'unit_1': data.get('accident_horizontal_jet_human_distance'),
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('hjet_flame_width'),
            'var': 'Df',
            'unit_1': f'{diameter_flame:.2f}',
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('hjet_flame_length'),
            'var': 'Lf',
            'unit_1': f'{lenght_flame:.2f}',
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('jet_mass_rate'),
            'var': 'G',
            'unit_1': f'{mass_rate:.2f}',
            'unit_2': i18n.get('kg_per_sec')},
        {'id': i18n.get('empirical_coefficient'),
            'var': 'K',
            'unit_1': k_coef,
            'unit_2': '-'},
        {'id': i18n.get('jet_state_fuel'),
            'var': '-',
            'unit_1': i18n.get(jet_state_phase),
            'unit_2': '-'}]
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'edit_vertical_jet',
                                      'plot_vertical_jet',
                                      i18n=i18n, param_back=True, back_data='back_typical_accidents', check_role=True, role=role))


@fire_accident_router.callback_query(F.data.in_(['edit_vertical_jet']))
async def edit_vertical_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(*kb_edit_vjet, i18n=i18n, param_back=True, back_data='back_vertical_jet', check_role=True, role=role))


@fire_accident_router.callback_query(F.data.in_(['edit_vjet_state']))
async def vjet_state_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, 'vertical_jet_state_liquid_kb', 'vertical_jet_state_comp_gas_kb', 'vertical_jet_state_liq_gas_vap_kb', i18n=i18n))


@fire_accident_router.callback_query(F.data.in_(['vertical_jet_state_liquid_kb', 'vertical_jet_state_comp_gas_kb', 'vertical_jet_state_liq_gas_vap_kb']))
async def vertical_jet_state_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    # state_data = await state.get_state()
    call_data = callback.data
    if call_data == 'vertical_jet_state_liquid_kb':
        await state.update_data(accident_vertical_jet_state='jet_state_liquid')
    elif call_data == 'vertical_jet_state_comp_gas_kb':
        await state.update_data(accident_vertical_jet_state='jet_state_comp_gas')
    elif call_data == 'vertical_jet_state_liq_gas_vap_kb':
        await state.update_data(accident_vertical_jet_state='jet_state_liq_gas_vap')
    data = await state.get_data()
    jet_state_phase = data.get('accident_vertical_jet_state')
    k_coef = 15.0 if jet_state_phase == 'jet_state_liquid' else 13.5 if jet_state_phase == 'jet_state_liq_gas_vap' else 12.5
    mass_rate = float(data.get('accident_vertical_jet_mass_rate'))
    lenght_flame = k_coef * mass_rate ** 0.4
    diameter_flame = 0.15 * lenght_flame

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('vertical_jet')
    data_out = [
        {'id': i18n.get('jet_human_distance'),
            'var': 'r',
            'unit_1': data.get('accident_horizontal_jet_human_distance'),
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('hjet_flame_width'),
            'var': 'Df',
            'unit_1': f'{diameter_flame:.2f}',
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('hjet_flame_length'),
            'var': 'Lf',
            'unit_1': f'{lenght_flame:.2f}',
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('jet_mass_rate'),
            'var': 'G',
            'unit_1': f'{mass_rate:.2f}',
            'unit_2': i18n.get('kg_per_sec')},
        {'id': i18n.get('empirical_coefficient'),
            'var': 'K',
            'unit_1': k_coef,
            'unit_2': '-'},
        {'id': i18n.get('jet_state_fuel'),
            'var': '-',
            'unit_1': i18n.get(jet_state_phase),
            'unit_2': '-'}]
    media = get_data_table(data=data_out, headers=headers, label=label)
    text = i18n.vertical_jet.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'edit_vertical_jet',
                                      'plot_vertical_jet',
                                      i18n=i18n, param_back=True, back_data='back_typical_accidents', check_role=True, role=role))


@fire_accident_router.callback_query(F.data.in_(['plot_vertical_jet']))
async def vertical_jet_plot_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      #   'edit_vertical_jet',
                                      #   'plot_vertical_jet',
                                      i18n=i18n, param_back=True, back_data='back_vertical_jet', check_role=True, role=role))
    data = await state.get_data()

    text = i18n.vertical_jet.text()

    distance = float(data.get('accident_horizontal_jet_human_distance'))
    jet_state_phase = data.get('accident_vertical_jet_state')
    k_coef = 15.0 if jet_state_phase == 'jet_state_liquid' else 13.5 if jet_state_phase == 'jet_state_liq_gas_vap' else 12.5
    mass_rate = float(data.get('accident_vertical_jet_mass_rate'))
    lenght_flame = k_coef * mass_rate ** 0.4
    diameter_flame = 0.15 * lenght_flame

    v_jet = AccidentParameters()
    x, y = v_jet.compute_heat_flux(
        eff_diameter=diameter_flame, lenght_flame=lenght_flame)

    # dist_num = f_ball.get_distance_at_sep(x_values=x, y_values=y, sep=4)
    sep_num = v_jet.get_sep_at_distance(
        x_values=x, y_values=y, distance=distance)

    unit_sep = i18n.get('kwatt_per_meter_square')

    text_annotate = f" q= {sep_num:.1f} {unit_sep} "

    media = get_plot_graph(x_values=x, y_values=y, ylim=max(y) + max(y) * 0.05,
                           add_annotate=True, text_annotate=text_annotate, x_ann=distance, y_ann=sep_num,
                           label=i18n.get('plot_vertical_jet_label'), x_label=i18n.get('distance_label'), y_label=i18n.get('y_vertical_jet_label'),
                           add_legend=True, loc_legend=1)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      #   'edit_vertical_jet',
                                      #   'plot_vertical_jet',
                                      i18n=i18n, param_back=True, back_data='back_vertical_jet', check_role=True, role=role))


@fire_accident_router.callback_query(F.data.in_(['fire_ball', 'back_fire_ball']))
async def fire_ball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    data.setdefault("edit_accident_fire_ball_param", "1")
    data.setdefault("accident_fire_ball_sub", "LNG")
    data.setdefault("accident_fire_ball_sep", "350")
    data.setdefault("accident_fire_ball_height_center", "50")
    data.setdefault("accident_fire_ball_mass_fuel", "500")
    data.setdefault("accident_fire_ball_distance", "100")
    data.setdefault("accident_fire_ball_existence_time", "10")
    data.setdefault("accident_fire_ball_atmospheric_transmittance", "1")
    await state.update_data(data)
    data = await state.get_data()
    text = i18n.fire_ball.text()

    subst = data.get('accident_fire_ball_sub')
    mass = float(data.get('accident_fire_ball_mass_fuel'))

    f_ball = AccidentParameters(type_accident='fire_ball')

    ts = f_ball.compute_fire_ball_existence_time(mass=mass)
    d = f_ball.compute_fire_ball_diameter(mass=mass)

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('fire_ball')
    data_out = [
        {'id': i18n.get('ball_distance'), 'var': 'r',  'unit_1': data.get(
            'accident_fire_ball_distance'), 'unit_2': i18n.get('meter')},
        {'id': i18n.get('ball_height_center'), 'var': 'H',
            'unit_1': f"{d:.2f}", 'unit_2': i18n.get('meter')},
        {'id': i18n.get('ball_diameter'), 'var': 'Ds',
            'unit_1': f"{d:.2f}", 'unit_2': i18n.get('meter')},
        {'id': i18n.get('ball_existence_time'), 'var': 'ts',
            'unit_1': f"{ts:.2f}", 'unit_2': i18n.get('second')},
        {'id': i18n.get('ball_mass_fuel'), 'var': 'm',
         'unit_1': mass, 'unit_2': i18n.get('kilogram')},
        {'id': i18n.get('surface_density_thermal_radiation_flame'),
            'var': 'Ef', 'unit_1': data.get('accident_fire_ball_sep'), 'unit_2': i18n.get('kwatt_per_meter_square')},
        {'id': i18n.get('substance'), 'var': '-', 'unit_1': i18n.get(subst), 'unit_2': '-'}]

    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_fire_ball', 'run_fire_ball', i18n=i18n, param_back=True, back_data='back_typical_accidents', check_role=True, role=role))


@fire_accident_router.callback_query(F.data.in_(['edit_fire_ball']))
async def edit_fire_ball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(*kb_edit_ball, i18n=i18n, param_back=True, back_data='back_fire_ball', check_role=True, role=role))


@fire_accident_router.callback_query(F.data.in_(['edit_ball_mass', 'edit_ball_distance']))
async def edit_ball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    if callback.data == 'edit_ball_mass':
        await state.set_state(FSMFireAccidentForm.edit_fire_ball_mass_state)
    elif callback.data == 'edit_ball_distance':
        await state.set_state(FSMFireAccidentForm.edit_fire_ball_distance_state)
    data = await state.get_data()
    state_data = await state.get_state()
    if state_data == FSMFireAccidentForm.edit_fire_ball_mass_state:
        text = i18n.edit_fire_ball.text(fire_ball_param=i18n.get(
            "name_fire_ball_mass"), edit_fire_ball=data.get("accident_fire_ball_mass_fuel", 0))
    elif state_data == FSMFireAccidentForm.edit_fire_ball_distance_state:
        text = i18n.edit_fire_ball.text(fire_ball_param=i18n.get(
            "name_fire_ball_distance"), edit_fire_ball=data.get("accident_fire_ball_distance", 0))
    kb = ['one', 'two', 'three', 'four', 'five', 'six', 'seven',
          'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready']

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, *kb, i18n=i18n))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['run_fire_ball', 'run_fire_ball_guest']))
async def run_fire_ball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    text = i18n.calculation_progress.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_fire_ball', check_role=True, role=role))
    text = i18n.fire_ball.text()
    subst = data.get('accident_fire_ball_sub')
    mass = float(data.get('accident_fire_ball_mass_fuel'))
    distance = float(data.get('accident_fire_ball_distance'))
    sep = float(data.get('accident_fire_ball_sep'))

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('fire_ball')

    f_ball = AccidentParameters(type_accident='fire_ball')
    ts = f_ball.compute_fire_ball_existence_time(mass=mass)
    d = f_ball.compute_fire_ball_diameter(mass=mass)

    fq = f_ball.compute_fire_ball_view_factor(
        eff_diameter=d, height=d, distance=distance)
    t = f_ball.compute_fire_ball_atmospheric_transmittance(
        eff_diameter=d, height=d, distance=distance)
    q = sep * fq * t

    data_out = [
        {'id': i18n.get('ball_heat_flux'), 'var': 'q',
         'unit_1': f"{q:.2f}", 'unit_2': i18n.get('kwatt_per_meter_square')},
        {'id': i18n.get('ball_atmospheric_transmittance'),
         'var': 'τ',  'unit_1': f"{t:.2f}", 'unit_2': '-'},
        {'id': i18n.get('ball_view_factor'), 'var': 'Fq',
         'unit_1': f"{fq:.3f}", 'unit_2': '-'},
        {'id': i18n.get('ball_distance'), 'var': 'r',  'unit_1': data.get(
            'accident_fire_ball_distance'), 'unit_2': i18n.get('meter')},
        {'id': i18n.get('ball_height_center'), 'var': 'H',
            'unit_1': f"{d:.2f}", 'unit_2': i18n.get('meter')},
        {'id': i18n.get('ball_diameter'), 'var': 'Ds',
            'unit_1': f"{d:.2f}", 'unit_2': i18n.get('meter')},
        {'id': i18n.get('ball_existence_time'), 'var': 'ts',
            'unit_1': f"{ts:.2f}", 'unit_2': i18n.get('second')},
        {'id': i18n.get('ball_mass_fuel'), 'var': 'm',
         'unit_1': mass, 'unit_2': i18n.get('kilogram')},
        {'id': i18n.get('surface_density_thermal_radiation_flame'),
            'var': 'Ef', 'unit_1': data.get('accident_fire_ball_sep'), 'unit_2': i18n.get('kwatt_per_meter_square')},
        {'id': i18n.get('substance'), 'var': '-', 'unit_1': i18n.get(subst), 'unit_2': '-'}]

    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=7)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'plot_fire_ball', i18n=i18n, param_back=True, back_data='back_fire_ball', check_role=False, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(StateFilter(*SFilter_fire_ball), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'dooble_zero', 'point', 'clear']))
async def edit_fire_ball_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    if state_data == FSMFireAccidentForm.edit_fire_ball_mass_state:
        fire_ball_param = i18n.get("name_fire_ball_mass")
    elif state_data == FSMFireAccidentForm.edit_fire_ball_distance_state:
        fire_ball_param = i18n.get("name_fire_ball_distance")

    edit_data = await state.get_data()
    if callback.data == 'clear':
        await state.update_data(edit_accident_fire_ball_param="")
        edit_d = await state.get_data()
        edit_data = edit_d.get('edit_accident_fire_ball_param', 1)
        text = i18n.edit_fire_ball.text(
            fire_ball_param=fire_ball_param, edit_fire_ball=edit_data)

    else:
        edit_param_1 = edit_data.get('edit_accident_fire_ball_param')
        edit_sum = edit_param_1 + i18n.get(callback.data)
        await state.update_data(edit_accident_fire_ball_param=edit_sum)
        edit_data = await state.get_data()
        edit_param = edit_data.get('edit_accident_fire_ball_param', 0)
        text = i18n.edit_fire_ball.text(
            fire_ball_param=fire_ball_param, edit_fire_ball=edit_param)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready', i18n=i18n))


@fire_accident_router.callback_query(StateFilter(*SFilter_fire_ball), F.data.in_(['ready']))
async def edit_fire_ball_param_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    state_data = await state.get_state()
    data = await state.get_data()
    value = data.get("edit_accident_fire_ball_param")
    if state_data == FSMFireAccidentForm.edit_fire_ball_mass_state:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(accident_fire_ball_mass_fuel=value)
        else:
            await state.update_data(accident_fire_ball_mass_fuel=10)
    elif state_data == FSMFireAccidentForm.edit_fire_ball_distance_state:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(accident_fire_ball_distance=value)
        else:
            await state.update_data(accident_fire_ball_distance=10)
    data = await state.get_data()
    text = i18n.fire_ball.text()
    subst = data.get('accident_fire_ball_sub')
    mass = float(data.get('accident_fire_ball_mass_fuel'))

    f_ball = AccidentParameters(type_accident='fire_ball')

    ts = f_ball.compute_fire_ball_existence_time(mass=mass)
    d = f_ball.compute_fire_ball_diameter(mass=mass)

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('fire_ball')
    data_out = [
        {'id': i18n.get('ball_distance'), 'var': 'r',  'unit_1': data.get(
            'accident_fire_ball_distance'), 'unit_2': i18n.get('meter')},
        {'id': i18n.get('ball_height_center'), 'var': 'H',
            'unit_1': f"{d:.2f}", 'unit_2': i18n.get('meter')},
        {'id': i18n.get('ball_diameter'), 'var': 'Ds',
            'unit_1': f"{d:.2f}", 'unit_2': i18n.get('meter')},
        {'id': i18n.get('ball_existence_time'), 'var': 'ts',
            'unit_1': f"{ts:.2f}", 'unit_2': i18n.get('second')},
        {'id': i18n.get('ball_mass_fuel'), 'var': 'm',
         'unit_1': mass, 'unit_2': i18n.get('kilogram')},
        {'id': i18n.get('surface_density_thermal_radiation_flame'),
            'var': 'Ef', 'unit_1': data.get('accident_fire_ball_sep'), 'unit_2': i18n.get('kwatt_per_meter_square')},
        {'id': i18n.get('substance'), 'var': '-', 'unit_1': i18n.get(subst), 'unit_2': '-'}]

    media = get_data_table(data=data_out, headers=headers, label=label)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*kb_edit_ball, i18n=i18n, param_back=True, back_data='back_fire_ball', check_role=True, role=role))
    await state.update_data(edit_accident_fire_ball_param='')
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['plot_fire_ball']))
async def plot_fire_ball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_fire_ball', check_role=True, role=role))

    data = await state.get_data()
    text = i18n.fire_ball.text()

    # subst = data.get('accident_fire_ball_sub')
    mass = float(data.get('accident_fire_ball_mass_fuel'))
    sep = float(data.get('accident_fire_ball_sep'))
    distance = float(data.get('accident_fire_ball_distance'))
    f_ball = AccidentParameters(type_accident='fire_ball')
    diameter_ball = f_ball.compute_fire_ball_diameter(mass=mass)

    x, y = f_ball.compute_heat_flux_fire_ball(
        diameter_ball=diameter_ball, height=diameter_ball, sep=sep)

    # dist_num = f_ball.get_distance_at_sep(x_values=x, y_values=y, sep=4)
    sep_num = f_ball.get_sep_at_distance(
        x_values=x, y_values=y, distance=distance)

    unit_sep = i18n.get('kwatt_per_meter_square')
    text_annotate = f" q= {sep_num:.1f} {unit_sep}"
    media = get_plot_graph(x_values=x, y_values=y, ylim=max(y) + max(y) * 0.05,
                           add_annotate=True, text_annotate=text_annotate, x_ann=distance, y_ann=sep_num,
                           label=i18n.get('plot_ball_label'), x_label=i18n.get('distance_label'), y_label=i18n.get('y_ball_label'),
                           add_legend=True, loc_legend=1)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_fire_ball', check_role=True, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['accident_bleve', 'back_accident_bleve']))
async def bleve_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    data.setdefault("edit_accident_bleve_param", "1")
    data.setdefault("accident_bleve_sub", "LPG")
    data.setdefault("accident_bleve_mass_fuel", "1000")
    data.setdefault("accident_bleve_temperature_liquid_phase", "293")
    data.setdefault("accident_bleve_boiling_point", "-50")
    data.setdefault("accident_bleve_energy_fraction", "0.5")
    data.setdefault("accident_bleve_heat_capacity_liquid_phase", "2000")
    data.setdefault("accident_bleve_overpressure_on_30m", "5.0")
    data.setdefault("accident_bleve_impuls_on_30m", "15.0")
    data.setdefault("accident_bleve_distance", "30")

    subst = data.get('accident_bleve_sub')
    coef_k = float(data.get("accident_bleve_energy_fraction"))
    heat_capacity = float(
        data.get('accident_bleve_heat_capacity_liquid_phase'))
    mass = float(data.get('accident_bleve_mass_fuel'))
    temp_liq = float(data.get('accident_bleve_temperature_liquid_phase'))
    boiling_point = float(data.get('accident_bleve_boiling_point'))
    acc_bleve = AccidentParameters(type_accident='accident_bleve')
    expl_energy = acc_bleve.compute_expl_energy(
        k=coef_k, Cp=heat_capacity, mass=mass, temp_liquid=temp_liq, boiling_point=boiling_point)
    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('accident_bleve')
    data_out = [
        {'id': i18n.get('distance_bleve'), 'var': 'r',  'unit_1': data.get(
            'accident_bleve_distance'), 'unit_2': i18n.get('meter')},
        {'id': i18n.get('effective_explosion_energy'), 'var': 'Eeff',
            'unit_1': f"{expl_energy:.2e}", 'unit_2': '-'},
        {'id': i18n.get('pressure_wave_energy_fraction'), 'var': 'k',
            'unit_1': coef_k, 'unit_2': '-'},
        {'id': i18n.get('mass_liquid_phase'), 'var': 'm',
            'unit_1': mass, 'unit_2': i18n.get('kilogram')},
        {'id': i18n.get('temperature_liquid_phase'), 'var': 'Tₒ',
         'unit_1': temp_liq, 'unit_2': i18n.get('kelvin')},
        {'id': i18n.get('boiling_point'),
            'var': 'Tb', 'unit_1': f"{boiling_point + 273.15:.2f}", 'unit_2': i18n.get('kelvin')},
        {'id': i18n.get('specific_heat_capacity_liquid_phase'), 'var': 'Cp',
         'unit_1': heat_capacity, 'unit_2': i18n.get('J_per_kg_in_kelvin')},
        {'id': i18n.get('substance'), 'var': '-', 'unit_1': i18n.get(subst), 'unit_2': '-'}]
    text = i18n.accident_bleve.text()
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_accident_bleve', 'run_accident_bleve', i18n=i18n, param_back=True, back_data='back_typical_accidents', check_role=True, role=role))
    await state.update_data(data)
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_accident_bleve']))
async def edit_accident_bleve_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(*kb_edit_bleve, i18n=i18n, param_back=True, back_data='back_accident_bleve', check_role=True, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_bleve_mass', 'edit_bleve_distance']))
async def edit_bleve_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    if callback.data == 'edit_bleve_mass':
        await state.set_state(FSMFireAccidentForm.edit_bleve_mass_state)
    elif callback.data == 'edit_bleve_distance':
        await state.set_state(FSMFireAccidentForm.edit_bleve_distance_state)
    data = await state.get_data()
    state_data = await state.get_state()
    if state_data == FSMFireAccidentForm.edit_bleve_mass_state:
        text = i18n.edit_bleve.text(bleve_param=i18n.get(
            "name_bleve_mass"), edit_bleve=data.get("accident_bleve_mass_fuel", 0))
    elif state_data == FSMFireAccidentForm.edit_bleve_distance_state:
        text = i18n.edit_bleve.text(bleve_param=i18n.get(
            "name_bleve_distance"), edit_bleve=data.get("accident_bleve_distance", 0))
    kb = ['one', 'two', 'three', 'four', 'five', 'six', 'seven',
          'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready']

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, *kb, i18n=i18n))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['run_accident_bleve', 'run_accident_bleve_guest']))
async def run_bleve_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    text = i18n.calculation_progress.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_accident_bleve', check_role=True, role=role))

    subst = data.get('accident_bleve_sub')
    coef_k = float(data.get("accident_bleve_energy_fraction"))
    heat_capacity = float(
        data.get('accident_bleve_heat_capacity_liquid_phase'))
    mass = float(data.get('accident_bleve_mass_fuel'))
    temp_liq = float(data.get('accident_bleve_temperature_liquid_phase'))
    boiling_point = float(data.get('accident_bleve_boiling_point'))
    distance = float(data.get('accident_bleve_distance'))
    acc_bleve = AccidentParameters(type_accident='accident_bleve')
    expl_energy = acc_bleve.compute_expl_energy(
        k=coef_k, Cp=heat_capacity, mass=mass, temp_liquid=temp_liq, boiling_point=boiling_point)
    reduced_mass = acc_bleve.compute_redused_mass(expl_energy=expl_energy)
    overpres, impuls = acc_bleve.compute_overpres_inopen(
        reduced_mass=reduced_mass, distance=distance)
    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('accident_bleve')
    data_out = [
        {'id': i18n.get('impuls_overpressure'), 'var': 'I+',
         'unit_1': f"{impuls:.2e}", 'unit_2': i18n.get('pascal_in_sec')},
        {'id': i18n.get('overpressure'), 'var': 'ΔP',
         'unit_1': f"{overpres:.2e}", 'unit_2': i18n.get('pascal')},
        {'id': i18n.get('reduced_mass_liquid_phase'), 'var': 'mпр',
            'unit_1': f"{reduced_mass:.2f}", 'unit_2': '-'},

        {'id': i18n.get('distance_bleve'), 'var': 'r',  'unit_1': data.get(
            'accident_bleve_distance'), 'unit_2': i18n.get('meter')},
        {'id': i18n.get('effective_explosion_energy'), 'var': 'Eeff',
            'unit_1': f"{expl_energy:.2e}", 'unit_2': '-'},
        {'id': i18n.get('pressure_wave_energy_fraction'), 'var': 'k',
            'unit_1': coef_k, 'unit_2': '-'},
        {'id': i18n.get('mass_liquid_phase'), 'var': 'm',
            'unit_1': mass, 'unit_2': i18n.get('kilogram')},
        {'id': i18n.get('temperature_liquid_phase'), 'var': 'Tₒ',
         'unit_1': temp_liq, 'unit_2': i18n.get('kelvin')},
        {'id': i18n.get('boiling_point'),
            'var': 'Tb', 'unit_1': f"{boiling_point + 273.15:.2f}", 'unit_2': i18n.get('kelvin')},
        {'id': i18n.get('specific_heat_capacity_liquid_phase'), 'var': 'Cp',
         'unit_1': heat_capacity, 'unit_2': i18n.get('J_per_kg_in_kelvin')},
        {'id': i18n.get('substance'), 'var': '-', 'unit_1': i18n.get(subst), 'unit_2': '-'}]
    text = i18n.accident_bleve.text()
    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=8)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'plot_accident_bleve_pressure', 'plot_accident_bleve_impuls', i18n=i18n, param_back=True, back_data='back_accident_bleve', check_role=False, role=role))

    await state.update_data(accident_bleve_overpressure_on_30m=overpres)
    await state.update_data(accident_bleve_impuls_on_30m=impuls)
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'plot_accident_bleve_pressure')
async def plot_accident_bleve_pressure_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_accident_bleve', check_role=True, role=role))
    data = await state.get_data()
    text = i18n.accident_bleve.text()

    # subst = data.get('accident_bleve_sub')
    coef_k = float(data.get("accident_bleve_energy_fraction"))
    heat_capacity = float(
        data.get('accident_bleve_heat_capacity_liquid_phase'))
    mass = float(data.get('accident_bleve_mass_fuel'))
    temp_liq = float(data.get('accident_bleve_temperature_liquid_phase'))
    boiling_point = float(data.get('accident_bleve_boiling_point'))
    overpresure_30 = round(
        float(data.get('accident_bleve_overpressure_on_30m')), 2)
    distance = float(data.get('accident_bleve_distance'))
    acc_bleve = AccidentParameters(type_accident='accident_bleve')
    expl_energy = acc_bleve.compute_expl_energy(
        k=coef_k, Cp=heat_capacity, mass=mass, temp_liquid=temp_liq, boiling_point=boiling_point)
    reduced_mass = acc_bleve.compute_redused_mass(expl_energy=expl_energy)
    overpres, impuls, dist = acc_bleve.compute_overpres_inopen(
        reduced_mass=reduced_mass, distance_run=True, distance=distance)

    unit_p = i18n.get('pascal')
    unit_p1 = i18n.get('kg_per_santimeter_square')
    text_annotate = f" ΔP\n = {overpresure_30:.2e} {unit_p}\n = {(overpresure_30*0.000010197):.2e} {unit_p1}"

    media = get_plot_graph(x_values=dist, y_values=overpres, ylim=overpresure_30 * 3.5,
                           add_annotate=True,
                           text_annotate=text_annotate, x_ann=distance, y_ann=overpresure_30,
                           label=i18n.get('plot_pressure_label'),
                           x_label=i18n.get('distance_label'),
                           y_label=i18n.get('plot_pressure_legend'),
                           add_legend=True, loc_legend=1)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      #   'plot_accident_bleve_pressure',
                                      'plot_accident_bleve_impuls', i18n=i18n, param_back=True, back_data='back_accident_bleve', check_role=False, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'plot_accident_bleve_impuls')
async def plot_accident_bleve_impuls_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_accident_bleve', check_role=True, role=role))
    data = await state.get_data()
    text = i18n.accident_bleve.text()

    # subst = data.get('accident_bleve_sub')
    coef_k = float(data.get("accident_bleve_energy_fraction"))
    heat_capacity = float(
        data.get('accident_bleve_heat_capacity_liquid_phase'))
    mass = float(data.get('accident_bleve_mass_fuel'))
    temp_liq = float(data.get('accident_bleve_temperature_liquid_phase'))
    boiling_point = float(data.get('accident_bleve_boiling_point'))
    impuls_30 = round(
        float(data.get('accident_bleve_impuls_on_30m')), 2)
    distance = float(data.get('accident_bleve_distance'))
    acc_bleve = AccidentParameters(type_accident='accident_bleve')
    expl_energy = acc_bleve.compute_expl_energy(
        k=coef_k, Cp=heat_capacity, mass=mass, temp_liquid=temp_liq, boiling_point=boiling_point)
    reduced_mass = acc_bleve.compute_redused_mass(expl_energy=expl_energy)
    overpres, impuls, dist = acc_bleve.compute_overpres_inopen(
        reduced_mass=reduced_mass, distance_run=True, distance=distance)

    unit_i = i18n.get('pascal_in_sec')
    text_annotate = f" I+ = {impuls_30:.2e} {unit_i}"

    media = get_plot_graph(x_values=dist, y_values=impuls, ylim=impuls_30 * 4.0,
                           add_annotate=True,
                           text_annotate=text_annotate, x_ann=distance, y_ann=impuls_30,
                           label=i18n.get('plot_impuls_label'), x_label=i18n.get('distance_label'), y_label=i18n.get('plot_impuls_legend'),
                           add_legend=True, loc_legend=1)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'plot_accident_bleve_pressure',
                                      i18n=i18n, param_back=True, back_data='back_accident_bleve', check_role=False, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(StateFilter(*SFilter_bleve), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'dooble_zero', 'point', 'clear']))
async def edit_bleve_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    if state_data == FSMFireAccidentForm.edit_bleve_mass_state:
        bleve_param = i18n.get("name_bleve_mass")
    elif state_data == FSMFireAccidentForm.edit_bleve_distance_state:
        bleve_param = i18n.get("name_bleve_distance")

    edit_data = await state.get_data()
    if callback.data == 'clear':
        await state.update_data(edit_accident_bleve_param="")
        edit_d = await state.get_data()
        edit_data = edit_d.get('edit_accident_bleve_param', 1)
        text = i18n.edit_bleve.text(
            bleve_param=bleve_param, edit_bleve=edit_data)

    else:
        edit_param_1 = edit_data.get('edit_accident_bleve_param')
        edit_sum = edit_param_1 + i18n.get(callback.data)
        await state.update_data(edit_accident_bleve_param=edit_sum)
        edit_data = await state.get_data()
        edit_param = edit_data.get('edit_accident_bleve_param', 0)
        text = i18n.edit_bleve.text(
            bleve_param=bleve_param, edit_bleve=edit_param)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready', i18n=i18n))


@fire_accident_router.callback_query(StateFilter(*SFilter_bleve), F.data.in_(['ready']))
async def edit_bleve_param_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    state_data = await state.get_state()
    data = await state.get_data()
    value = data.get("edit_accident_bleve_param")
    if state_data == FSMFireAccidentForm.edit_bleve_mass_state:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(accident_bleve_mass_fuel=value)
        else:
            await state.update_data(accident_bleve_mass_fuel=10)
    elif state_data == FSMFireAccidentForm.edit_bleve_distance_state:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(accident_bleve_distance=value)
        else:
            await state.update_data(accident_bleve_distance=30)
    data = await state.get_data()
    subst = data.get('accident_bleve_sub')
    coef_k = float(data.get("accident_bleve_energy_fraction"))
    heat_capacity = float(
        data.get('accident_bleve_heat_capacity_liquid_phase'))
    mass = float(data.get('accident_bleve_mass_fuel'))
    temp_liq = float(data.get('accident_bleve_temperature_liquid_phase'))
    boiling_point = float(data.get('accident_bleve_boiling_point'))
    acc_bleve = AccidentParameters(type_accident='accident_bleve')
    expl_energy = acc_bleve.compute_expl_energy(
        k=coef_k, Cp=heat_capacity, mass=mass, temp_liquid=temp_liq, boiling_point=boiling_point)
    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('accident_bleve')
    data_out = [
        {'id': i18n.get('distance_bleve'), 'var': 'r',  'unit_1': data.get(
            'accident_bleve_distance'), 'unit_2': i18n.get('meter')},
        {'id': i18n.get('effective_explosion_energy'), 'var': 'Eeff',
            'unit_1': f"{expl_energy:.2e}", 'unit_2': '-'},
        {'id': i18n.get('pressure_wave_energy_fraction'), 'var': 'k',
            'unit_1': coef_k, 'unit_2': '-'},
        {'id': i18n.get('mass_liquid_phase'), 'var': 'm',
            'unit_1': mass, 'unit_2': i18n.get('kilogram')},
        {'id': i18n.get('temperature_liquid_phase'), 'var': 'Tₒ',
         'unit_1': temp_liq, 'unit_2': i18n.get('kelvin')},
        {'id': i18n.get('boiling_point'),
            'var': 'Tb', 'unit_1': f"{boiling_point + 273.15:.2f}", 'unit_2': i18n.get('kelvin')},
        {'id': i18n.get('specific_heat_capacity_liquid_phase'), 'var': 'Cp',
         'unit_1': heat_capacity, 'unit_2': i18n.get('J_per_kg_in_kelvin')},
        {'id': i18n.get('substance'), 'var': '-',
         'unit_1': i18n.get(subst), 'unit_2': '-'}
    ]
    text = i18n.accident_bleve.text()
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_accident_bleve', 'run_accident_bleve', i18n=i18n, param_back=True, back_data='back_typical_accidents', check_role=True, role=role))
    await state.update_data(edit_accident_bleve_param='')
