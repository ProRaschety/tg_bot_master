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
from app.tg_bot.utilities.misc_utils import get_picture_filling, get_data_table, get_plot_graph
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb
from app.tg_bot.states.fsm_state_data import FSMFireAccidentForm
from app.calculation.physics.accident_parameters import AccidentParameters
from app.calculation.physics.physics_utils import compute_characteristic_diameter, compute_density_gas_phase
log = logging.getLogger(__name__)

fire_accident_router = Router()
fire_accident_router.message.filter(IsGuest())
fire_accident_router.callback_query.filter(IsGuest())

SFilter_fire_pool = [FSMFireAccidentForm.edit_fire_pool_area_state]
SFilter_fire_flash = [FSMFireAccidentForm.edit_fire_flash_mass_state]
SFilter_bleve = [FSMFireAccidentForm.edit_bleve_mass_state]

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
                'edit_pool_area']

kb_edit_flash = [4,
                 'edit_flash_mass']

kb_edit_bleve = [4,
                 'edit_bleve_mass']


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
    data.setdefault("accident_fire_pool_vel_wind", "0")
    data.setdefault("accident_fire_pool_pool_area", "314")
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
    await state.update_data(data)
    await callback.answer('')


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
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['gasoline', 'diesel', 'LNG', 'LPG', 'liq_hydrogen']))
async def fire_pool_subst_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    call_data = callback.data
    # data = await state.get_data()
    f_pool = AccidentParameters(type_accident='fire_pool')
    mass_burn_rate = f_pool.compute_mass_burning_rate(subst=call_data)
    await state.update_data(accident_fire_pool_sub=call_data)
    await state.update_data(accident_fire_pool_mass_burning_rate=mass_burn_rate)
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


@fire_accident_router.callback_query(F.data.in_(['edit_pool_area']))
async def edit_pool_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    log.info(callback.data)
    if callback.data == 'edit_pool_area':
        await state.set_state(FSMFireAccidentForm.edit_fire_pool_area_state)
    data = await state.get_data()
    state_data = await state.get_state()
    if state_data == FSMFireAccidentForm.edit_fire_pool_area_state:
        text = i18n.edit_fire_pool.text(fire_pool_param=i18n.get(
            "name_fire_pool_area"), edit_fire_pool=data.get("accident_fire_pool_pool_area", 0))

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
        reply_markup=get_inline_cd_kb(*kb_edit_pool, i18n=i18n, param_back=True, back_data='back_fire_pool', check_role=True, role=role))
    await state.update_data(edit_accident_fire_pool_param='')
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'run_fire_pool')
async def run_fire_pool_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    text = i18n.fire_pool.text()
    subst = data.get('accident_fire_pool_sub')
    diameter = compute_characteristic_diameter(
        area=float(data.get("accident_fire_pool_pool_area")))
    air_density = compute_density_gas_phase(
        molar_mass=28.97, temperature=float(data.get('accident_fire_pool_temperature')))
    fuel_density = compute_density_gas_phase(molar_mass=float(data.get('accident_fire_pool_molar_mass_fuel')),
                                             temperature=float(data.get('accident_fire_pool_boiling_point_fuel')))
    mass_burn_rate = float(data.get('accident_fire_pool_mass_burning_rate'))
    f_pool = AccidentParameters(type_accident='fire_pool')
    nonvelocity = f_pool.compute_nonvelocity(wind=float(data.get(
        'accident_fire_pool_vel_wind')), density_fuel=fuel_density, mass_burn_rate=mass_burn_rate, eff_diameter=diameter)
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

        {'id': i18n.get('pool_area'), 'var': 'F',  'unit_1': data.get(
            'accident_fire_pool_pool_area'), 'unit_2': i18n.get('meter_square')},
        {'id': i18n.get('wind_velocity'), 'var': 'wₒ',
            'unit_1': data.get('accident_fire_pool_vel_wind'), 'unit_2': i18n.get('m_per_sec')},
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
        reply_markup=get_inline_cd_kb(1, 'plot_fire_pool', i18n=i18n, param_back=True, back_data='back_fire_pool', check_role=True, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'plot_fire_pool')
async def plot_fire_pool_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    text = i18n.fire_pool.text()
    subst = data.get('accident_fire_pool_sub')
    diameter = compute_characteristic_diameter(
        area=float(data.get("accident_fire_pool_pool_area")))
    f_pool = AccidentParameters(type_accident='fire_pool')
    fuel_density = compute_density_gas_phase(molar_mass=float(data.get('accident_fire_pool_molar_mass_fuel')),
                                             temperature=float(data.get('accident_fire_pool_boiling_point_fuel')))
    mass_burn_rate = float(data.get('accident_fire_pool_mass_burning_rate'))
    f_pool = AccidentParameters(type_accident='fire_pool')
    nonvelocity = f_pool.compute_nonvelocity(wind=float(data.get(
        'accident_fire_pool_vel_wind')), density_fuel=fuel_density, mass_burn_rate=mass_burn_rate, eff_diameter=diameter)
    flame_angle = f_pool.get_flame_deflection_angle(nonvelocity=nonvelocity)
    air_density = compute_density_gas_phase(
        molar_mass=28.97, temperature=float(data.get('accident_fire_pool_temperature')))
    flame_lenght = f_pool.compute_lenght_flame_pool(
        nonvelocity=nonvelocity, density_air=air_density, mass_burn_rate=mass_burn_rate, eff_diameter=diameter)
    sep = f_pool.compute_surface_emissive_power(
        eff_diameter=diameter, subst=subst)
    x, y = f_pool.compute_heat_flux(
        eff_diameter=diameter, sep=sep, lenght_flame=flame_lenght, angle=flame_angle)
    sep_4 = f_pool.get_distance_at_sep(x_values=x, y_values=y, sep=4)
    dist_43 = f_pool.get_sep_at_distance(x_values=x, y_values=y, distance=43)
    # log.info(f'4.0 кВт на раст. м: {sep_4} = {dist_43}')
    # text_annotate = f"Тепловой поток: {max(y):.2f} кВт/м²\nПросто текст"
    media = get_plot_graph(x_values=x, y_values=y, label=i18n.get('plot_pool_label'), x_label=i18n.get('x_pool_label'), y_label=i18n.get('y_pool_label'),
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
    data.setdefault("accident_fire_flash_nkpr", "1.4")
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
        {'id': i18n.get('saturated_fuel_vapor_density_at_boiling_point'),
            'var': 'Cнкпр', 'unit_1': data.get('accident_fire_flash_nkpr'), 'unit_2': i18n.get('percent_volume')},
        {'id': i18n.get('ambient_air_density'), 'var': 'ρₒ',
            'unit_1': f"{air_density:.2f}", 'unit_2': i18n.get('kg_per_m_cub')},
        {'id': i18n.get('ambient_temperature'), 'var': 'tₒ', 'unit_1': data.get(
            'accident_fire_flash_temperature'), 'unit_2': i18n.get('celsius')},
        {'id': i18n.get('substance'), 'var': '-', 'unit_1': i18n.get(subst), 'unit_2': '-'}]

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


@fire_accident_router.callback_query(F.data.in_(['edit_flash_mass']))
async def edit_flash_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    if callback.data == 'edit_flash_mass':
        await state.set_state(FSMFireAccidentForm.edit_fire_flash_mass_state)
    data = await state.get_data()
    state_data = await state.get_state()
    if state_data == FSMFireAccidentForm.edit_fire_flash_mass_state:
        text = i18n.edit_fire_flash.text(fire_flash_param=i18n.get(
            "name_fire_flash_mass"), edit_fire_flash=data.get("accident_fire_flash_mass_fuel", 0))

    kb = ['one', 'two', 'three', 'four', 'five', 'six', 'seven',
          'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready']

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, *kb, i18n=i18n))
    await callback.answer('')


@fire_accident_router.callback_query(StateFilter(*SFilter_fire_flash), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'dooble_zero', 'point', 'clear']))
async def edit_fire_flash_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    if state_data == FSMFireAccidentForm.edit_fire_flash_mass_state:
        fire_flash_param = i18n.get("name_fire_flash_mass")

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
    data = await state.get_data()
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
        {'id': i18n.get('saturated_fuel_vapor_density_at_boiling_point'),
            'var': 'Cнкпр', 'unit_1': data.get('accident_fire_flash_nkpr'), 'unit_2': i18n.get('percent_volume')},
        {'id': i18n.get('ambient_air_density'), 'var': 'ρₒ',
            'unit_1': f"{air_density:.2f}", 'unit_2': i18n.get('kg_per_m_cub')},
        {'id': i18n.get('ambient_temperature'), 'var': 'tₒ', 'unit_1': data.get(
            'accident_fire_flash_temperature'), 'unit_2': i18n.get('celsius')},
        {'id': i18n.get('substance'), 'var': '-', 'unit_1': i18n.get(subst), 'unit_2': '-'}]

    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_fire_flash', 'run_fire_flash', i18n=i18n, param_back=True, back_data='back_typical_accidents', check_role=True, role=role))
    await state.update_data(edit_accident_fire_flash_param='')
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'run_fire_flash')
async def run_fire_flash_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    text = i18n.fire_flash.text()
    subst = data.get('accident_fire_flash_sub')
    rad_pool = float(data.get('accident_fire_flash_radius_pool'))
    mass = float(data.get('accident_fire_flash_mass_fuel'))
    clfl = float(data.get('accident_fire_flash_nkpr'))
    temperature = float(data.get('accident_fire_flash_temperature'))
    molar_mass = float(data.get(
        'accident_fire_flash_molar_mass_fuel'))

    density_fuel = compute_density_gas_phase(
        molar_mass=molar_mass, temperature=temperature)
    # air_density = compute_density_gas_phase(
    #     molar_mass=28.97, temperature=float(data.get('accident_fire_flash_temperature')))
    f_flash = AccidentParameters(type_accident='fire_flash')
    radius_LFL = f_flash.compute_radius_LFL(
        density=density_fuel, mass=mass, clfl=clfl)
    height_LFL = f_flash.compute_height_LFL(
        density=density_fuel, mass=mass, clfl=clfl)

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
            'var': i18n.get('lower_concentration_limit'), 'unit_1': clfl, 'unit_2': i18n.get('percent_volume')},
        # {'id': i18n.get('ambient_air_density'), 'var': 'ρₒ',
        #     'unit_1': f"{air_density:.2f}", 'unit_2': i18n.get('kg_per_m_cub')},
        {'id': i18n.get('ambient_temperature'), 'var': 'tₒ',
         'unit_1': temperature, 'unit_2': i18n.get('celsius')},
        {'id': i18n.get('substance'), 'var': '-', 'unit_1': i18n.get(subst), 'unit_2': '-'}]

    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=5)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_fire_flash', check_role=True, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'cloud_explosion')
async def cloud_explosion_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    data.setdefault("accident_cloud_explosion_sub", "Метан")
    data.setdefault("accident_cloud_explosion_class_fuel", "4")
    data.setdefault("accident_cloud_explosion_class_space", "1")
    data.setdefault("accident_cloud_explosion_mass_fuel", "500")
    data.setdefault("accident_cloud_explosion_expl_cond",
                    "above_surface")  # on_surface

    text = i18n.cloud_explosion.text()
    cloud_exp = AccidentParameters(type_accident=callback.data)
    data_out, headers, label = cloud_exp.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_cloud_explosion', 'run_cloud_explosion', i18n=i18n, param_back=True, back_data='back_typical_accidents', check_role=True, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'horizontal_jet')
async def horizontal_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    data.setdefault("accident_horizontal_jet_sub", "Метан")
    data.setdefault("accident_horizontal_jet_mass_rate", "5")
    data.setdefault("accident_horizontal_jet_state", "jet_state_liq_gas_vap")
    data.setdefault("accident_horizontal_jet_human_distance", "30")

    text = i18n.horizontal_jet.text()
    h_jet = AccidentParameters(type_accident=callback.data)
    data_out, headers, label = h_jet.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_horizontal_jet', 'run_horizontal_jet', i18n=i18n, param_back=True, back_data='back_typical_accidents', check_role=True, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'vertical_jet')
async def vertical_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    data.setdefault("accident_vertical_jet_sub", "Метан")
    data.setdefault("accident_vertical_jet_mass_rate", "5")
    data.setdefault("accident_vertical_jet_state", "jet_state_liq_gas_vap")
    data.setdefault("accident_vertical_jet_human_distance", "30")

    text = i18n.vertical_jet.text()
    v_jet = AccidentParameters(type_accident=callback.data)
    data_out, headers, label = v_jet.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_vertical_jet', 'run_vertical_jet', i18n=i18n, param_back=True, back_data='back_typical_accidents', check_role=True, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'fire_ball')
async def fire_ball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    data.setdefault("accident_fire_ball_sub", "Метан")
    data.setdefault("accident_fire_ball_center", "50")
    data.setdefault("accident_fire_ball_mass_fuel", "500")
    data.setdefault("accident_fire_ball_human_distance", "30")

    text = i18n.fire_ball.text()
    f_ball = AccidentParameters(type_accident=callback.data)
    data_out, headers, label = f_ball.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_fire_ball', 'run_fire_ball', i18n=i18n, param_back=True, back_data='back_typical_accidents', check_role=True, role=role))
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
    data.setdefault("accident_bleve_", "20")
    data.setdefault("accident_bleve_human_distance", "30")

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
        {'id': i18n.get('effective_explosion_energy'), 'var': 'Eeff',
            'unit_1': f"{expl_energy:.2e}", 'unit_2': '-'},
        {'id': i18n.get('pressure_wave_energy_fraction'), 'var': 'k',
            'unit_1': coef_k, 'unit_2': '-'},
        # {'id': i18n.get('distance_bleve'), 'var': 'r',  'unit_1': data.get(
        #     'accident_bleve_human_distance'), 'unit_2': i18n.get('meter')},
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


@fire_accident_router.callback_query(F.data.in_(['edit_bleve_mass']))
async def edit_bleve_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    if callback.data == 'edit_bleve_mass':
        await state.set_state(FSMFireAccidentForm.edit_bleve_mass_state)
    data = await state.get_data()
    state_data = await state.get_state()
    if state_data == FSMFireAccidentForm.edit_bleve_mass_state:
        text = i18n.edit_bleve.text(bleve_param=i18n.get(
            "name_bleve_mass"), edit_bleve=data.get("accident_bleve_mass_fuel", 0))

    kb = ['one', 'two', 'three', 'four', 'five', 'six', 'seven',
          'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready']

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, *kb, i18n=i18n))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'run_accident_bleve')
async def run_bleve_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
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
    reduced_mass = acc_bleve.compute_redused_mass(expl_energy=expl_energy)
    overpres, impuls = acc_bleve.compute_overpres_inopen(
        reduced_mass=reduced_mass)
    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('accident_bleve')
    data_out = [
        {'id': i18n.get('impuls_overpressure'), 'var': 'I',
         'unit_1': f"{impuls:.2e}", 'unit_2': i18n.get('pascal_in_sec')},
        {'id': i18n.get('overpressure'), 'var': 'P',
         'unit_1': f"{overpres:.2e}", 'unit_2': i18n.get('pascal')},
        {'id': i18n.get('distance_bleve'), 'var': 'r',  'unit_1': data.get(
            'accident_bleve_human_distance'), 'unit_2': i18n.get('meter')},

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
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_accident_bleve', check_role=True, role=role))
    await callback.answer('')


@fire_accident_router.callback_query(StateFilter(*SFilter_bleve), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'dooble_zero', 'point', 'clear']))
async def edit_bleve_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    if state_data == FSMFireAccidentForm.edit_bleve_mass_state:
        bleve_param = i18n.get("name_bleve_mass")

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
        {'id': i18n.get('effective_explosion_energy'), 'var': 'Eeff',
            'unit_1': f"{expl_energy:.2e}", 'unit_2': '-'},
        {'id': i18n.get('pressure_wave_energy_fraction'), 'var': 'k',
            'unit_1': coef_k, 'unit_2': '-'},
        # {'id': i18n.get('distance_bleve'), 'var': 'r',  'unit_1': data.get(
        #     'accident_bleve_human_distance'), 'unit_2': i18n.get('meter')},
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
    await state.update_data(edit_accident_bleve_param='')
    await callback.answer('')
