import logging
import io
import json

from dataclasses import asdict, astuple

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
# , InlineQueryResultArticle, InputTextMessageContent
# from aiogram.types import InlineQuery
from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaPhoto

from fluentogram import TranslatorRunner

# from app.infrastructure.database.database.db import DB
# from app.tg_bot.models.tables import DataFrameModel
from app.tg_bot.models.role import UserRole
from app.tg_bot.models.keyboard import InlineKeyboardModel

from app.tg_bot.filters.filter_role import IsGuest
from app.tg_bot.states.fsm_state_data import FSMEditForm, FSMFireAccidentForm
from app.tg_bot.utilities.misc_utils import get_picture_filling, get_data_table, get_plot_graph, get_dataframe_table, find_key_path, get_dict_value
# from app.tg_bot.utilities import tables
from app.tg_bot.utilities.tables import DataFrameBuilder

from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_keypad

from app.calculation.physics.accident_parameters import AccidentParameters
from app.calculation.physics.physics_utils import compute_characteristic_diameter, compute_density_gas_phase, compute_density_vapor_at_boiling, get_property_fuel, compute_stoichiometric_coefficient_with_fuel, compute_stoichiometric_coefficient_with_oxygen
from app.calculation.qra_mode import probits
from app.calculation.utilities import misc_utils

from app.infrastructure.database.models.calculations import AccidentModel
from app.infrastructure.database.models.substance import SubstanceModel

from pprint import pprint

log = logging.getLogger(__name__)

fire_accident_router = Router()
fire_accident_router.message.filter(IsGuest())
fire_accident_router.callback_query.filter(IsGuest())


# SFilter_horizontal_jet = [FSMFireAccidentForm.edit_horizontal_jet_mass_flow_state,
#                           FSMFireAccidentForm.edit_horizontal_jet_distance_state]

# SFilter_vertical_jet = [FSMFireAccidentForm.edit_vertical_jet_mass_flow_state,
#                         FSMFireAccidentForm.edit_vertical_jet_distance_state]

# SFilter_fire_ball = [FSMFireAccidentForm.edit_fire_ball_mass_state,
#                      FSMFireAccidentForm.edit_fire_ball_distance_state]

# SFilter_bleve = [FSMFireAccidentForm.edit_bleve_mass_state,
#                  FSMFireAccidentForm.edit_bleve_distance_state]

# SFilter_cloud_explosion = [FSMFireAccidentForm.edit_cloud_explosion_correction_parameter_state,
#                            FSMFireAccidentForm.edit_cloud_explosion_stc_coef_oxygen_state,
#                            FSMFireAccidentForm.edit_cloud_explosion_coef_z_state,
#                            FSMFireAccidentForm.edit_cloud_explosion_mass_state,
#                            FSMFireAccidentForm.edit_cloud_explosion_distance_state]


@fire_accident_router.callback_query(F.data == 'back_typical_accidents')
async def back_typical_accidents_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(
            i18n=i18n, back_data='back_fire_risks'
        )
    )

    text = i18n.typical_accidents.text()
    media = get_picture_filling(i18n.get('path_typical_accident'))
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(
            1,
            *i18n.get('accidents_kb_' + role).split('\n'),
            i18n=i18n, back_data='back_fire_risks'
        )
    )
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'typical_accidents')
async def typical_accidents_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.typical_accidents.text()
    media = get_picture_filling(i18n.get('path_typical_accident'))

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(
            1,
            *i18n.get('accidents_kb_' + role).split('\n'),
            i18n=i18n, back_data='back_fire_risks'
        )
    )

    context_data = await state.get_data()
    # pprint(context_data)
    subst = context_data.get('substance')
    subs_state = context_data.get('substance_state')

    molar_mass, boling_point, mass_burning_rate, LFL = await get_property_fuel(subst=subst)
    substance = SubstanceModel(substance_name=subst,
                               molar_mass=molar_mass,
                               boiling_point=boling_point,
                               mass_burning_rate=mass_burning_rate,
                               lower_flammability_limit=LFL,
                               )
    accident_model = AccidentModel(substance_state=subs_state,
                                   substance_name=subst,
                                   substance=substance,
                                   )

    await state.update_data(accident_model=asdict(accident_model), temporary_parameter='', temporary_request='')


@fire_accident_router.callback_query(F.data.in_(['fire_pool', 'back_fire_pool']))
async def fire_pool_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_typical_accidents'
                                      )
    )

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))
    dfb = DataFrameBuilder(i18n=i18n,  request='fire_pool',
                           accident_model=accident_model)
    dataframe = dfb.action_request()
    media = get_dataframe_table(data=dataframe)

    text = i18n.fire_pool.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(
            1,
            *i18n.get('fire_pool_kb_guest').split('\n') if role in ['guest'] else i18n.get('fire_pool_kb').split('\n'),
            i18n=i18n, back_data='back_typical_accidents'
        )
    )
    await state.update_data(temporary_request='fire_pool')


@fire_accident_router.callback_query(F.data.in_(['run_fire_pool']))
async def run_fire_pool_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    context_data = await state.get_data()
    text = i18n.calculation_progress.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(
            i18n=i18n, back_data='back_fire_pool'
        )
    )

    accident_model = AccidentModel(**context_data.get('accident_model'))

    dfb = DataFrameBuilder(i18n=i18n,  request='run_fire_pool',
                           accident_model=accident_model)
    dataframe = dfb.action_request()

    media = get_dataframe_table(data=dataframe, results=True, row_num=7)
    text = i18n.fire_pool.text()

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(
            1,
            *i18n.get('result_fire_pool_kb_' + role).split('\n'),
            i18n=i18n, back_data='back_fire_pool'
        )
    )
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_fire_pool_guest']))
async def edit_fire_pool_guest_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.get('initial_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(
            1,
            *i18n.get('fire_pool_kb_guest').split('\n'),
            i18n=i18n, back_data='back_fire_pool'
        )
    )

    text = i18n.get('repeated_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(
            1,
            *i18n.get('fire_pool_kb_guest').split('\n'),
            i18n=i18n, back_data='back_fire_pool'
        )
    )

    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_fire_pool']))
async def edit_fire_pool_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(
            4,
            *i18n.get('edit_fire_pool_kb').split('\n'),
            i18n=i18n, penult_button='run_fire_pool', back_data='back_fire_pool'
        )
    )
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_pool_substance']))
async def pool_subst_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, 'gasoline', 'diesel', 'LNG', 'LPG', 'liq_hydrogen', i18n=i18n, back_data='back_fire_pool'
                                      )
    )


@fire_accident_router.callback_query(F.data.in_(['gasoline', 'diesel', 'LNG', 'LPG', 'liq_hydrogen', 'other_liquid', 'any_substance']))
async def fire_pool_subst_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    call_data = callback.data

    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_typical_accidents'))

    molar_mass, boling_point, mass_burning_rate, LFL = await get_property_fuel(subst=call_data)
    substance = SubstanceModel(substance_name='',
                               molar_mass=molar_mass,
                               boiling_point=boling_point,
                               mass_burning_rate=mass_burning_rate,
                               lower_flammability_limit=LFL)

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))
    accident_model.substance_name = call_data
    accident_model.substance = substance

    dfb = DataFrameBuilder(i18n=i18n,  request='fire_pool',
                           accident_model=accident_model)
    dataframe = dfb.action_request()
    media = get_dataframe_table(data=dataframe)

    text = i18n.fire_pool.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(
            1,
            *i18n.get('fire_pool_kb_guest').split('\n') if role in ['guest'] else i18n.get('fire_pool_kb').split('\n'),
            i18n=i18n, back_data='back_typical_accidents'
        )
    )

    await state.update_data(accident_model=asdict(accident_model))
    # await state.update_data(substance=asdict(substance))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['pool_area', 'pool_distance', 'velocity_wind']))
async def edit_pool_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    context_data = await state.get_data()

    path_edited_parameter = find_key_path(
        dictionary=context_data, key=callback.data)

    editable_parameter = get_dict_value(
        dictionary=context_data, keys_list=path_edited_parameter)

    text = i18n.temporary_parameter.text(
        text=i18n.get('name_' + callback.data), value=editable_parameter)

    kb = InlineKeyboardModel(
        width=4, buttons='edit_fire_pool_kb', penultimate='run_fire_pool', ultimate='back_fire_pool')

    context_data['keyboard_model'] = asdict(kb)
    context_data['temporary_text'] = callback.data
    context_data['path_edited_parameter'] = path_edited_parameter

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_keypad(
            i18n=i18n, penult_button='ready'
        )
    )

    await state.update_data(context_data)
    await state.set_state(FSMEditForm.keypad_state)
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'plot_fire_pool')
async def plot_fire_pool_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_fire_pool'))

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))
    # substance = SubstanceModel(**accident_model.substance)
    substance = accident_model.substance

    distance = accident_model.distance
    diameter = compute_characteristic_diameter(
        area=accident_model.pool_area)
    f_pool = AccidentParameters(type_accident='fire_pool')
    fuel_density = compute_density_gas_phase(
        molar_mass=substance.molar_mass, temperature=substance.boiling_point)
    air_density = compute_density_gas_phase(
        molar_mass=28.97,
        temperature=accident_model.air_temperature
    )
    nonvelocity = f_pool.compute_nonvelocity(
        wind=accident_model.velocity_wind, density_fuel=fuel_density, mass_burn_rate=substance.mass_burning_rate, eff_diameter=diameter)
    flame_angle = f_pool.get_flame_deflection_angle(nonvelocity=nonvelocity)

    flame_lenght = f_pool.compute_lenght_flame_pool(
        nonvelocity=nonvelocity, density_air=air_density, mass_burn_rate=substance.mass_burning_rate, eff_diameter=diameter)
    sep = f_pool.compute_surface_emissive_power(
        eff_diameter=diameter, subst=accident_model.substance_name)

    x, y = f_pool.compute_heat_flux(
        eff_diameter=diameter, sep=sep, lenght_flame=flame_lenght, angle=flame_angle)

    # dist_num = f_pool.get_distance_at_sep(x_values=x, y_values=y, sep=4)
    # sep_num = f_pool.get_sep_at_distance(
    #     x_values=x, y_values=y, distance=distance + diameter / 2)
    # value_x0 = 4.0
    # x0 = misc_utils.get_distance_at_value(
    #     x_values=x, y_values=y, value=value_x0)
    sep_num = misc_utils.get_value_at_distance(
        x_values=x, y_values=y, distance=distance + diameter / 2)

    unit_sep = i18n.get('kwatt_per_meter_square')
    # unit_x0 = i18n.get('meter')

    text_annotate = f"q({distance + diameter / 2:.1f})= {sep_num:.1f} {unit_sep}"
    # text_annotate_nd = f"r({value_x0:.1f})= {x0:.1f} {unit_x0}"

    plot_label = i18n.eq_heat_flux()
    media = get_plot_graph(x_values=x, y_values=y, ylim=max(y) + max(y) * 0.05,

                           add_annotate=True, text_annotate=text_annotate, x_ann=distance + diameter / 2, y_ann=sep_num,

                           label=i18n.get('plot_pool_label'), x_label=i18n.get('distance_label'), y_label=i18n.get('y_pool_label'),
                           add_legend=True, loc_legend=1,
                           plot_label=plot_label
                           )
    text = i18n.fire_pool.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'probit_fire_pool', i18n=i18n, back_data='back_fire_pool'))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'probit_fire_pool')
async def probability_defeat_firepool_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    log.info(f'Запрос: {i18n.probit_heat_flux.text()}')

    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_fire_pool'))

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))
    substance = accident_model.substance
    distance = accident_model.distance

    diameter = compute_characteristic_diameter(
        area=accident_model.pool_area)
    f_pool = AccidentParameters(type_accident='fire_pool')
    fuel_density = compute_density_gas_phase(
        molar_mass=substance.molar_mass, temperature=substance.boiling_point)
    air_density = compute_density_gas_phase(
        molar_mass=28.97,
        temperature=accident_model.air_temperature
    )
    nonvelocity = f_pool.compute_nonvelocity(
        wind=accident_model.velocity_wind, density_fuel=fuel_density, mass_burn_rate=substance.mass_burning_rate, eff_diameter=diameter)
    flame_angle = f_pool.get_flame_deflection_angle(nonvelocity=nonvelocity)

    flame_lenght = f_pool.compute_lenght_flame_pool(
        nonvelocity=nonvelocity, density_air=air_density, mass_burn_rate=substance.mass_burning_rate, eff_diameter=diameter)
    sep = f_pool.compute_surface_emissive_power(
        eff_diameter=diameter, subst=accident_model.substance_name)

    x, y = f_pool.compute_heat_flux(
        eff_diameter=diameter, sep=sep, lenght_flame=flame_lenght, angle=flame_angle)
    x, y = probits.compute_thermal_fatality_prob_for_plot(
        type_accident='fire_pool', x_val=x, heat_flux=y, eff_diameter=diameter)
    # dist_num = f_pool.get_distance_at_sep(x_values=x, y_values=y, sep=4)
    # sep_num = f_pool.get_sep_at_distance(
    #     x_values=x, y_values=y, distance=distance + diameter / 2)

    value = misc_utils.get_value_at_distance(
        x_values=x, y_values=y, distance=distance + diameter / 2)
    # unit_sep = i18n.get('kwatt_per_meter_square')
    unit_sep = ''
    text_annotate = f"Q({distance + diameter / 2:.1f})= {value:.1e} {unit_sep}"

    plot_label = i18n.eq_heat_flux()

    text = i18n.probit_heat_flux.text()
    media = get_plot_graph(x_values=x, y_values=y, ylim=max(y) + max(y) * 0.05, ymin=-0.01,
                           add_annotate=True, text_annotate=text_annotate, x_ann=distance + diameter / 2, y_ann=value,
                           label=i18n.get('plot_probit_label'), x_label=i18n.get('distance_label'), y_label=i18n.get('y_probit_label'),
                           add_legend=False, loc_legend=1,
                           plot_label=plot_label
                           )

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(
            1,
            'plot_fire_pool', i18n=i18n, back_data='back_fire_pool'
        )
    )
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['cloud_explosion', 'back_cloud_explosion']))
async def cloud_explosion_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_typical_accidents'
                                      )
    )

    text = i18n.cloud_explosion.text()

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))

    dfb = DataFrameBuilder(i18n=i18n,  request='cloud_explosion',
                           accident_model=accident_model)
    dataframe = dfb.action_request()

    media = get_dataframe_table(data=dataframe)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('cloud_explosion_kb_guest').split('\n') if role in ['guest'] else i18n.get('cloud_explosion_kb').split('\n'),
                                      i18n=i18n, back_data='back_typical_accidents'
                                      )
    )
    await state.update_data(temporary_request='cloud_explosion')


@fire_accident_router.callback_query(F.data.in_(['run_cloud_explosion']))
async def run_cloud_explosion_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    context_data = await state.get_data()
    text = i18n.calculation_progress.text()

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_cloud_explosion'
                                      )
    )

    accident_model = AccidentModel(**context_data.get('accident_model'))

    dfb = DataFrameBuilder(i18n=i18n,  request='run_cloud_explosion',
                           accident_model=accident_model)
    dataframe = dfb.action_request()

    media = get_dataframe_table(data=dataframe, results=True, row_num=7)

    text = i18n.cloud_explosion_result.text(distance=accident_model.distance)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'plot_accident_cloud_explosion_pressure', 'plot_accident_cloud_explosion_impuls',
                                      i18n=i18n, back_data='back_cloud_explosion'
                                      )
    )

    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_cloud_explosion_guest']))
async def edit_cloud_explosion_guest_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.get('initial_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('cloud_explosion_kb_guest').split('\n'),
                                      i18n=i18n, back_data='back_cloud_explosion'))
    text = i18n.get('repeated_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('cloud_explosion_kb_guest').split('\n'),
                                      i18n=i18n, back_data='back_cloud_explosion'))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_cloud_explosion', 'back_edit_cloud_explosion']))
async def edit_cloud_explosion_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2,
                                      *i18n.get('edit_cloud_explosion_kb').split('\n'),
                                      i18n=i18n, penult_button='run_cloud_explosion', back_data='back_cloud_explosion'))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_cloud_explosion_state']))
async def cloud_explosion_state_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, 'cloud_explosion_state_gas', 'cloud_explosion_state_dust', i18n=i18n, back_data='back_edit_cloud_explosion',))


@fire_accident_router.callback_query(F.data.in_(['edit_cloud_explosion_class_fuel']))
async def cloud_explosion_class_fuel_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.edit_cloud_explosion_class_fuel.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(4, 'class_fuel_first', 'class_fuel_second', 'class_fuel_third', 'class_fuel_fourth', i18n=i18n, back_data='back_edit_cloud_explosion',))


@fire_accident_router.callback_query(F.data.in_(['class_space']))
async def cloud_explosion_class_space_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.edit_cloud_explosion_class_space.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(4, 'class_space_first', 'class_space_second', 'class_space_third', 'class_space_fourth', i18n=i18n, back_data='back_edit_cloud_explosion',))


@fire_accident_router.callback_query(F.data.in_(['edit_cloud_explosion_expl_cond']))
async def cloud_explosion_cond_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, 'above_surface', 'on_surface', i18n=i18n, back_data='back_edit_cloud_explosion',))


@fire_accident_router.callback_query(F.data.in_(['cloud_explosion_methodology']))
async def cloud_explosion_methodology_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, 'methodology_404', 'methodology_2024', i18n=i18n, back_data='back_edit_cloud_explosion',))


@fire_accident_router.callback_query(F.data.in_(['cloud_explosion_state_gas', 'cloud_explosion_state_dust',
                                                 'class_fuel_first', 'class_fuel_second', 'class_fuel_third', 'class_fuel_fourth',
                                                 'class_space_first', 'class_space_second', 'class_space_third', 'class_space_fourth',
                                                 'above_surface', 'on_surface', 'methodology_404', 'methodology_2024']))
async def cloud_explosion_state_close(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.update_data.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_edit_cloud_explosion'))

    call_data = callback.data

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))
    # accident_model.substance_name = call_data

    if call_data == 'cloud_explosion_state_gas':
        accident_model.explosion_state_fuel = call_data
        # await state.update_data(accident_cloud_explosion_state_fuel='gas')
    elif call_data == 'cloud_explosion_state_dust':
        accident_model.explosion_state_fuel = call_data
        # await state.update_data(accident_cloud_explosion_state_fuel='dust')
    elif call_data == 'class_fuel_first':
        accident_model.substance.class_fuel = call_data
        # await state.update_data(accident_cloud_explosion_class_fuel='1')
    elif call_data == 'class_fuel_second':
        accident_model.substance.class_fuel = call_data
        # await state.update_data(accident_cloud_explosion_class_fuel='2')
    elif call_data == 'class_fuel_third':
        accident_model.substance.class_fuel = call_data
        # await state.update_data(accident_cloud_explosion_class_fuel='3')
    elif call_data == 'class_fuel_fourth':
        accident_model.substance.class_fuel = call_data
        # await state.update_data(accident_cloud_explosion_class_fuel='4')
    elif call_data == 'class_space_first':
        accident_model.class_space = call_data
        # await state.update_data(accident_cloud_explosion_class_space='1')
    elif call_data == 'class_space_second':
        accident_model.class_space = call_data
        # await state.update_data(accident_cloud_explosion_class_space='2')
    elif call_data == 'class_space_third':
        accident_model.class_space = call_data
        # await state.update_data(accident_cloud_explosion_class_space='3')
    elif call_data == 'class_space_fourth':
        accident_model.class_space = call_data
        # await state.update_data(accident_cloud_explosion_class_space='4')
    elif call_data == 'above_surface':
        accident_model.explosion_condition = call_data
        # await state.update_data(accident_cloud_explosion_expl_cond='above_surface')
    elif call_data == 'on_surface':
        accident_model.explosion_condition = call_data
        # await state.update_data(accident_cloud_explosion_expl_cond='on_surface')
    elif call_data == 'methodology_404':
        accident_model.methodology = call_data
        # await state.update_data(accident_cloud_explosion_methodology='methodology_404')
    elif call_data == 'methodology_2024':
        accident_model.methodology = call_data
        # await state.update_data(accident_cloud_explosion_methodology='methodology_2024')

    # data = await state.get_data()
    text = i18n.cloud_explosion.text()
    # subst = data.get('accident_cloud_explosion_state_fuel')
    # methodology = data.get('accident_cloud_explosion_methodology')
    # mass = float(data.get('accident_cloud_explosion_mass_fuel'))
    # stc_coef_oxygen = float(
    #     data.get('accident_cloud_explosion_stc_coef_oxygen'))
    # class_fuel = int(data.get('accident_cloud_explosion_class_fuel'))
    # class_space = int(data.get('accident_cloud_explosion_class_space'))
    # distance = float(data.get('accident_cloud_explosion_distance'))
    # cloud_exp = AccidentParameters(type_accident='cloud_explosion')
    # mode_expl = cloud_exp.get_mode_explosion(
    #     class_fuel=class_fuel, class_space=class_space)

    # headers = (i18n.get('name'), i18n.get('variable'),
    #            i18n.get('value'), i18n.get('unit'))
    # label = i18n.get('cloud_explosion')
    # data_out = [
    #     {'id': i18n.get('cloud_explosion_methodology'),
    #         'var': '-',
    #         'unit_1': i18n.get(methodology),
    #         'unit_2': '-'},
    #     {'id': i18n.get('cloud_explosion_distance'),
    #         'var': 'R',
    #         'unit_1': f"{distance:.1f}",
    #         'unit_2': i18n.get('meter')},
    #     {'id': i18n.get('cloud_explosion_mass_fuel'),
    #         'var': 'm',
    #         'unit_1': f"{mass:.2f}",
    #         'unit_2': i18n.get('kilogram')},
    #     {'id': i18n.get('cloud_explosion_coefficient_z'),
    #         'var': 'Z',
    #         'unit_1': data.get('accident_cloud_explosion_coef_z'),
    #         'unit_2': '-'},
    #     {'id': i18n.get('cloud_explosion_cond_ground'),
    #         'var': '-',
    #         'unit_1': i18n.get(data.get(
    #             'accident_cloud_explosion_expl_cond')),
    #         'unit_2': '-'},
    #     {'id': i18n.get('cloud_explosion_mode_expl'),
    #         'var': '-',
    #         'unit_1': f"{mode_expl:.0f}",
    #         'unit_2': '-'},
    #     {'id': i18n.get('cloud_explosion_class_space'),
    #         'var': '-',
    #         'unit_1': data.get('accident_cloud_explosion_class_space'),
    #         'unit_2': '-'},
    #     {'id': i18n.get('cloud_explosion_class_fuel'),
    #         'var': '-',
    #         'unit_1': data.get('accident_cloud_explosion_class_fuel'),
    #         'unit_2': '-'},
    #     {'id': i18n.get('stoichiometric_coefficient_for_oxygen'),
    #         'var': 'k',
    #         'unit_1': f"{stc_coef_oxygen:.2f}",
    #         'unit_2': '-'},
    #     {'id': i18n.get('cloud_explosion_correction_parameter'),
    #         'var': 'β',
    #         'unit_1': data.get('accident_cloud_explosion_correction_parameter'),
    #         'unit_2': '-'},
    #     # {'id': i18n.get('cloud_explosion_heat_combustion'),
    #     #     'var': 'Eуд0',
    #     #     'unit_1': data.get('accident_cloud_explosion_heat_combustion'),
    #     #     'unit_2': i18n.get('kJ_per_kg')},
    #     {'id': i18n.get('cloud_explosion_state_fuel'),
    #         'var': '-',
    #         'unit_1': i18n.get(subst),
    #         'unit_2': '-'}]

    # media = get_data_table(data=data_out, headers=headers, label=label)
    # accident_model.substance = asdict(substance)

    dataframe = tables.get_dataframe(
        request='fire_pool', i18n=i18n, accident_model=accident_model)
    media = get_dataframe_table(data=dataframe)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(2,
                                      *i18n.get('edit_cloud_explosion_kb').split('\n'),
                                      i18n=i18n, penult_button='run_cloud_explosion', back_data='back_cloud_explosion'))

    await state.update_data(accident_model=asdict(accident_model))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_cloud_explosion_correction_parameter', 'edit_cloud_explosion_stc_coef_oxygen',
                                                 'edit_cloud_explosion_coef_z', 'explosion_mass_fuel', 'edit_cloud_explosion_distance']))
async def edit_cloud_explosion_num_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    # if callback.data == 'edit_cloud_explosion_correction_parameter':
    #     await state.set_state(FSMFireAccidentForm.edit_cloud_explosion_correction_parameter_state)
    # elif callback.data == 'edit_cloud_explosion_stc_coef_oxygen':
    #     await state.set_state(FSMFireAccidentForm.edit_cloud_explosion_stc_coef_oxygen_state)
    # elif callback.data == 'edit_cloud_explosion_coef_z':
    #     await state.set_state(FSMFireAccidentForm.edit_cloud_explosion_coef_z_state)
    # elif callback.data == 'edit_cloud_explosion_mass_fuel':
    #     await state.set_state(FSMFireAccidentForm.edit_cloud_explosion_mass_state)
    # elif callback.data == 'edit_cloud_explosion_distance':
    #     await state.set_state(FSMFireAccidentForm.edit_cloud_explosion_distance_state)

    # data = await state.get_data()
    # user_state = await state.get_state()

    # if user_state == FSMFireAccidentForm.edit_cloud_explosion_correction_parameter_state:
    #     text = i18n.edit_cloud_explosion.text(cloud_explosion_param=i18n.get(
    #         "name_cloud_explosion_correction_parameter"), edit_cloud_explosion=data.get("accident_cloud_explosion_correction_parameter", 0))
    # elif user_state == FSMFireAccidentForm.edit_cloud_explosion_stc_coef_oxygen_state:
    #     text = i18n.edit_cloud_explosion.text(cloud_explosion_param=i18n.get(
    #         "name_cloud_explosion_stc_coef_oxygen"), edit_cloud_explosion=data.get("accident_cloud_explosion_stc_coef_oxygen", 0))

    # elif user_state == FSMFireAccidentForm.edit_cloud_explosion_coef_z_state:
    #     text = i18n.edit_cloud_explosion.text(cloud_explosion_param=i18n.get(
    #         "name_cloud_explosion_coef_z"), edit_cloud_explosion=data.get("accident_cloud_explosion_coef_z", 0))

    # elif user_state == FSMFireAccidentForm.edit_cloud_explosion_mass_state:
    #     text = i18n.edit_cloud_explosion.text(cloud_explosion_param=i18n.get(
    #         "name_cloud_explosion_mass_fuel"), edit_cloud_explosion=data.get("accident_cloud_explosion_mass_fuel", 0))

    # elif user_state == FSMFireAccidentForm.edit_cloud_explosion_distance_state:
    #     text = i18n.edit_cloud_explosion.text(cloud_explosion_param=i18n.get(
    #         "name_cloud_explosion_distance"), edit_cloud_explosion=data.get("accident_cloud_explosion_distance", 0))

    # await bot.edit_message_caption(
    #     chat_id=callback.message.chat.id,
    #     message_id=callback.message.message_id,
    #     caption=text,
    #     reply_markup=get_inline_cd_kb(3,
    #                                   *i18n.get('calculator_buttons').split('\n'),
    #                                   i18n=i18n))

    context_data = await state.get_data()

    path_edited_parameter = find_key_path(
        dictionary=context_data, key=callback.data)

    editable_parameter = get_dict_value(
        dictionary=context_data, keys_list=path_edited_parameter)

    text = i18n.temporary_parameter.text(
        text=i18n.get('name_' + callback.data), value=editable_parameter)

    kb = InlineKeyboardModel(
        width=4, buttons='edit_cloud_explosion_kb', penultimate='run_cloud_explosion', ultimate='back_cloud_explosion')

    context_data['keyboard_model'] = asdict(kb)
    context_data['temporary_text'] = callback.data
    context_data['path_edited_parameter'] = path_edited_parameter

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_keypad(
            i18n=i18n, penult_button='ready'
        )
    )

    await state.update_data(context_data)
    await state.set_state(FSMEditForm.keypad_state)


@fire_accident_router.callback_query(F.data.in_(['plot_accident_cloud_explosion_pressure']))
async def plot_cloud_explosion_pres_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_cloud_explosion'))
    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))
    substance = accident_model.substance

    text = i18n.cloud_explosion.text()

    # methodology = True if data.get(
    #     'accident_cloud_explosion_methodology') == 'methodology_2024' else False
    # mass = float(data.get('accident_cloud_explosion_mass_fuel'))
    # coef_z = float(data.get('accident_cloud_explosion_coef_z'))
    # class_fuel = int(data.get('accident_cloud_explosion_class_fuel'))
    # class_space = int(data.get('accident_cloud_explosion_class_space'))
    # heat = float(data.get('accident_cloud_explosion_heat_combustion'))
    # beta = float(data.get('accident_cloud_explosion_correction_parameter'))
    # distance = float(data.get('accident_cloud_explosion_distance'))
    # expl_sf = True if data.get(
    #     'accident_cloud_explosion_expl_cond') == 'on_surface' else False
    # stc_coef_oxygen = compute_stoichiometric_coefficient_with_oxygen(
    #     n_C=6.911, n_H=12.168)
    # stc_coef_fuel = compute_stoichiometric_coefficient_with_fuel(
    #     beta=stc_coef_oxygen)
    subst = accident_model.explosion_state_fuel
    methodology = accident_model.methodology
    mass = accident_model.explosion_mass_fuel
    stc_coef_oxygen = accident_model.explosion_stc_coef_oxygen
    class_fuel = substance.class_fuel
    class_space = accident_model.class_space
    distance = accident_model.distance
    stc_coef_oxygen = accident_model.explosion_stc_coef_oxygen
    stc_coef_fuel = compute_stoichiometric_coefficient_with_fuel(
        beta=stc_coef_oxygen)
    coef_z = substance.coefficient_z_participation_in_explosion
    expl_sf = True if accident_model.explosion_condition == 'on_surface' else False

    cloud_exp = AccidentParameters(type_accident='cloud_explosion')
    mode_expl = cloud_exp.get_mode_explosion(
        class_fuel=class_fuel, class_space=class_space)
    # cloud_exp = AccidentParameters()

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
    text_annotate = f"ΔP\n = {value:.2e} {unit_p}\n = {(value*0.000010197):.2e} {unit_p1}"

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
        reply_markup=get_inline_cd_kb(1, 'plot_accident_cloud_explosion_impuls', i18n=i18n, back_data='back_cloud_explosion'))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['plot_accident_cloud_explosion_impuls']))
async def plot_cloud_explosion_impuls_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_cloud_explosion'))
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
        reply_markup=get_inline_cd_kb(1, 'plot_accident_cloud_explosion_pressure', i18n=i18n, back_data='back_cloud_explosion'))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['horizontal_jet', 'back_horizontal_jet']))
async def horizontal_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_typical_accidents'))

    text = i18n.horizontal_jet.text()

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))

    dfb = DataFrameBuilder(i18n=i18n,  request='horizontal_jet',
                           accident_model=accident_model)
    dataframe = dfb.action_request()

    media = get_dataframe_table(data=dataframe)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('horizontal_jet_kb_guest').split('\n') if role in ['guest'] else i18n.get('horizontal_jet_kb').split('\n'),
                                      i18n=i18n, back_data='back_typical_accidents'
                                      )
    )
    await state.update_data(temporary_request='horizontal_jet')


@fire_accident_router.callback_query(F.data.in_(['edit_horizontal_jet_guest']))
async def edit_horizontal_jet_guest_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.get('initial_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('horizontal_jet_kb_guest').split('\n'),
                                      i18n=i18n, back_data='back_horizontal_jet'))
    text = i18n.get('repeated_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('horizontal_jet_kb_guest').split('\n'),
                                      i18n=i18n, back_data='back_horizontal_jet'))
    await callback.answer('')


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
                                      i18n=i18n, back_data='back_horizontal_jet'))
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
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_horizontal_jet'))


@fire_accident_router.callback_query(F.data.in_(['edit_horizontal_jet']))
async def edit_horizontal_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, *i18n.get('edit_horizontal_jet_kb').split('\n'),
                                      i18n=i18n, back_data='back_horizontal_jet'))


@fire_accident_router.callback_query(F.data.in_(['edit_hjet_state']))
async def hjet_state_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, 'horizontal_jet_state_liquid_kb', 'horizontal_jet_state_comp_gas_kb', 'horizontal_jet_state_liq_gas_vap_kb', i18n=i18n))


@fire_accident_router.callback_query(F.data.in_(['horizontal_jet_state_liquid_kb', 'horizontal_jet_state_comp_gas_kb', 'horizontal_jet_state_liq_gas_vap_kb']))
async def horizontal_jet_state_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    # user_state = await state.get_state()
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
        reply_markup=get_inline_cd_kb(1, *i18n.get('edit_horizontal_jet_kb').split('\n'), i18n=i18n, back_data='back_horizontal_jet'))


@fire_accident_router.callback_query(F.data.in_(['edit_hjet_mass_rate', 'edit_hjet_distance']))
async def edit_param_horizontal_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    if callback.data == 'edit_hjet_mass_rate':
        await state.set_state(FSMFireAccidentForm.edit_horizontal_jet_mass_flow_state)
    elif callback.data == 'edit_hjet_distance':
        await state.set_state(FSMFireAccidentForm.edit_horizontal_jet_distance_state)
    data = await state.get_data()
    user_state = await state.get_state()

    if user_state == FSMFireAccidentForm.edit_horizontal_jet_mass_flow_state:
        text = i18n.edit_hjet.text(hjet_param=i18n.get(
            "name_hjet_mass_rate"), edit_hjet=data.get("accident_horizontal_jet_mass_rate", 0))

    elif user_state == FSMFireAccidentForm.edit_horizontal_jet_distance_state:
        text = i18n.edit_hjet.text(hjet_param=i18n.get(
            "name_hjet_distance"), edit_hjet=data.get("accident_horizontal_jet_human_distance", 0))

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3,
                                      *i18n.get('calculator_buttons').split('\n'),
                                      i18n=i18n))


@fire_accident_router.callback_query(F.data.in_(['vertical_jet', 'back_vertical_jet']))
async def vertical_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_typical_accidents'))

    text = i18n.vertical_jet.text()

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))

    dfb = DataFrameBuilder(i18n=i18n,  request='vertical_jet',
                           accident_model=accident_model)
    dataframe = dfb.action_request()

    media = get_dataframe_table(data=dataframe)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('vertical_jet_kb_guest').split('\n') if role in ['guest'] else i18n.get('vertical_jet_kb').split('\n'),
                                      i18n=i18n, back_data='back_typical_accidents'
                                      )
    )
    await state.update_data(temporary_request='vertical_jet')


@fire_accident_router.callback_query(F.data.in_(['edit_vertical_jet_guest']))
async def edit_vertical_jet_guest_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.get('initial_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('vertical_jet_kb_guest').split('\n'),
                                      i18n=i18n, back_data='back_vertical_jet'))
    text = i18n.get('repeated_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('vertical_jet_kb_guest').split('\n'),
                                      i18n=i18n, back_data='back_vertical_jet'))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_vertical_jet']))
async def edit_vertical_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, *i18n.get('edit_vertical_jet_kb').split('\n'),
                                      i18n=i18n, back_data='back_vertical_jet'))


@fire_accident_router.callback_query(F.data.in_(['edit_vjet_state']))
async def vjet_state_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, 'vertical_jet_state_liquid_kb', 'vertical_jet_state_comp_gas_kb', 'vertical_jet_state_liq_gas_vap_kb', i18n=i18n))


@fire_accident_router.callback_query(F.data.in_(['vertical_jet_state_liquid_kb', 'vertical_jet_state_comp_gas_kb', 'vertical_jet_state_liq_gas_vap_kb']))
async def vertical_jet_state_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    # user_state = await state.get_state()
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
            'unit_1': data.get('accident_vertical__jet_human_distance'),
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('vjet_flame_width'),
            'var': 'Df',
            'unit_1': f'{diameter_flame:.2f}',
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('vjet_flame_length'),
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
                                      i18n=i18n, back_data='back_typical_accidents'))


@fire_accident_router.callback_query(F.data.in_(['edit_vjet_mass_rate', 'edit_vjet_distance']))
async def edit_vertical_jet_num_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    if callback.data == 'edit_vjet_mass_rate':
        await state.set_state(FSMFireAccidentForm.edit_vertical_jet_mass_flow_state)
    elif callback.data == 'edit_vjet_distance':
        await state.set_state(FSMFireAccidentForm.edit_vertical_jet_distance_state)
    data = await state.get_data()
    user_state = await state.get_state()

    if user_state == FSMFireAccidentForm.edit_vertical_jet_mass_flow_state:
        text = i18n.edit_vjet.text(vjet_param=i18n.get(
            "name_vjet_mass_rate"), edit_vjet=data.get("accident_vertical_jet_mass_rate", 0))

    elif user_state == FSMFireAccidentForm.edit_vertical_jet_distance_state:
        text = i18n.edit_vjet.text(vjet_param=i18n.get(
            "name_vjet_distance"), edit_vjet=data.get("accident_vertical_jet_human_distance", 0))

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3,
                                      *i18n.get('calculator_buttons').split('\n'),
                                      i18n=i18n))


@fire_accident_router.callback_query(F.data.in_(['plot_vertical_jet']))
async def vertical_jet_plot_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      i18n=i18n, back_data='back_vertical_jet'))
    data = await state.get_data()
    text = i18n.vertical_jet.text()
    distance = float(data.get('accident_vertical_jet_human_distance'))
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
                                      i18n=i18n, back_data='back_vertical_jet'))


@fire_accident_router.callback_query(F.data.in_(['fire_ball', 'back_fire_ball']))
async def fire_ball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_typical_accidents'))
    text = i18n.fire_ball.text()

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))

    dfb = DataFrameBuilder(i18n=i18n,  request='fire_ball',
                           accident_model=accident_model)
    dataframe = dfb.action_request()

    media = get_dataframe_table(data=dataframe)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, *i18n.get('fire_ball_kb_guest').split('\n') if role in ['guest'] else i18n.get('fire_ball_kb').split('\n'),
                                      i18n=i18n, back_data='back_typical_accidents'
                                      )
    )
    await state.update_data(temporary_request='fire_ball')


@fire_accident_router.callback_query(F.data.in_(['run_fire_ball']))
async def run_fire_ball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    text = i18n.calculation_progress.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_fire_ball'))
    text = i18n.fire_ball.text()

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))

    dfb = DataFrameBuilder(i18n=i18n,  request='run_fire_ball',
                           accident_model=accident_model)
    dataframe = dfb.action_request()

    media = get_dataframe_table(data=dataframe, row_num=7)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'plot_fire_ball', 'probit_fire_ball', i18n=i18n, back_data='back_fire_ball'))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_fire_ball']))
async def edit_fire_ball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, *i18n.get('edit_fire_ball_kb').split('\n'),
                                      i18n=i18n, penult_button='run_fire_ball', back_data='back_fire_ball'))


@fire_accident_router.callback_query(F.data.in_(['edit_fire_ball_guest']))
async def edit_fire_ball_guest_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    text = i18n.get('initial_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('fire_ball_kb_guest').split('\n'),
                                      i18n=i18n, back_data='back_fire_ball'))
    text = i18n.get('repeated_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('fire_ball_kb_guest').split('\n'),
                                      i18n=i18n, back_data='back_fire_ball'))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_ball_mass', 'edit_ball_distance']))
async def edit_ball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    if callback.data == 'edit_ball_mass':
        await state.set_state(FSMFireAccidentForm.edit_fire_ball_mass_state)
    elif callback.data == 'edit_ball_distance':
        await state.set_state(FSMFireAccidentForm.edit_fire_ball_distance_state)
    data = await state.get_data()
    user_state = await state.get_state()
    if user_state == FSMFireAccidentForm.edit_fire_ball_mass_state:
        text = i18n.edit_fire_ball.text(fire_ball_param=i18n.get(
            "name_fire_ball_mass"), edit_fire_ball=data.get("accident_fire_ball_mass_fuel", 0))
    elif user_state == FSMFireAccidentForm.edit_fire_ball_distance_state:
        text = i18n.edit_fire_ball.text(fire_ball_param=i18n.get(
            "name_fire_ball_distance"), edit_fire_ball=data.get("accident_fire_ball_distance", 0))

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3,
                                      *i18n.get('calculator_buttons').split('\n'),
                                      i18n=i18n))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['plot_fire_ball']))
async def plot_fire_ball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_fire_ball'))

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
    text_annotate = f" q({distance:.1f})= {sep_num:.1f} {unit_sep}"
    plot_label = i18n.eq_heat_flux()
    media = get_plot_graph(x_values=x, y_values=y, ylim=max(y) + max(y) * 0.05,
                           add_annotate=True, text_annotate=text_annotate, x_ann=distance, y_ann=sep_num,
                           label=i18n.get('plot_ball_label'), x_label=i18n.get('distance_label'), y_label=i18n.get('y_ball_label'),
                           add_legend=True, loc_legend=1,
                           plot_label=plot_label
                           )

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'probit_fire_ball', i18n=i18n, back_data='back_fire_ball'))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'probit_fire_ball')
async def probability_defeat_fireball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    log.info(f'Запрос: {i18n.probit_heat_flux.text()}')

    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_fire_ball'))

    data = await state.get_data()
    text = i18n.probit_heat_flux.text()

    mass = float(data.get('accident_fire_ball_mass_fuel'))
    sep = float(data.get('accident_fire_ball_sep'))
    distance = float(data.get('accident_fire_ball_distance'))
    f_ball = AccidentParameters(type_accident='fire_ball')
    diameter_ball = f_ball.compute_fire_ball_diameter(mass=mass)

    x, y = f_ball.compute_heat_flux_fire_ball(
        diameter_ball=diameter_ball, height=diameter_ball, sep=sep)

    x, y = probits.compute_thermal_fatality_prob_for_plot(
        type_accident='fire_ball', x_val=x, heat_flux=y, mass_ball=mass)

    value = misc_utils.get_value_at_distance(
        x_values=x, y_values=y, distance=distance)
    unit_sep = ''
    text_annotate = f"Q({distance:.1f})= {value:.1e} {unit_sep}"

    plot_label = i18n.eq_heat_flux()

    media = get_plot_graph(x_values=x, y_values=y, ylim=max(y) + max(y) * 0.05, ymin=-0.01,
                           add_annotate=True, text_annotate=text_annotate, x_ann=distance, y_ann=value,
                           label=i18n.get('plot_probit_label'), x_label=i18n.get('distance_label'), y_label=i18n.get('y_probit_label'),
                           add_legend=False, loc_legend=1,
                           plot_label=plot_label
                           )

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'plot_fire_ball', i18n=i18n, back_data='back_fire_ball'))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['accident_bleve', 'back_accident_bleve']))
async def bleve_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_typical_accidents'))

    text = i18n.accident_bleve.text()

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))

    dfb = DataFrameBuilder(i18n=i18n,  request='accident_bleve',
                           accident_model=accident_model)
    dataframe = dfb.action_request()

    media = get_dataframe_table(data=dataframe)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('accident_bleve_kb_guest').split('\n') if role in ['guest'] else i18n.get('accident_bleve_kb').split('\n'),
                                      i18n=i18n, back_data='back_typical_accidents'
                                      )
    )
    await state.update_data(temporary_request='accident_bleve')
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['run_accident_bleve']))
async def run_bleve_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    text = i18n.calculation_progress.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_accident_bleve'))

    text = i18n.accident_bleve.text()

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))

    dfb = DataFrameBuilder(i18n=i18n,  request='run_accident_bleve',
                           accident_model=accident_model)
    dataframe = dfb.action_request()

    media = get_dataframe_table(data=dataframe, row_num=8)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'plot_accident_bleve_pressure', 'plot_accident_bleve_impuls', i18n=i18n, back_data='back_accident_bleve'))

    # await state.update_data(accident_bleve_overpressure_on_30m=overpres)
    # await state.update_data(accident_bleve_impuls_on_30m=impuls)
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_accident_bleve_guest']))
async def edit_accident_bleve_guest_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.get('initial_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('accident_bleve_kb_guest').split('\n'),
                                      i18n=i18n, back_data='back_accident_bleve'))
    text = i18n.get('repeated_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('accident_bleve_kb_guest').split('\n'),
                                      i18n=i18n, back_data='back_accident_bleve'))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_accident_bleve']))
async def edit_accident_bleve_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, *i18n.get('edit_accident_bleve_kb').split('\n'),
                                      i18n=i18n, penult_button='run_accident_bleve', back_data='back_accident_bleve'
                                      )
    )
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_bleve_mass', 'edit_bleve_distance']))
async def edit_bleve_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    if callback.data == 'edit_bleve_mass':
        await state.set_state(FSMFireAccidentForm.edit_bleve_mass_state)
    elif callback.data == 'edit_bleve_distance':
        await state.set_state(FSMFireAccidentForm.edit_bleve_distance_state)
    data = await state.get_data()
    user_state = await state.get_state()
    if user_state == FSMFireAccidentForm.edit_bleve_mass_state:
        text = i18n.edit_bleve.text(bleve_param=i18n.get(
            "name_bleve_mass"), edit_bleve=data.get("accident_bleve_mass_fuel", 0))
    elif user_state == FSMFireAccidentForm.edit_bleve_distance_state:
        text = i18n.edit_bleve.text(bleve_param=i18n.get(
            "name_bleve_distance"), edit_bleve=data.get("accident_bleve_distance", 0))

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3,
                                      *i18n.get('calculator_buttons').split('\n'),
                                      i18n=i18n))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'plot_accident_bleve_pressure')
async def plot_accident_bleve_pressure_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_accident_bleve'))
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
                                      'plot_accident_bleve_impuls', i18n=i18n, back_data='back_accident_bleve'))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'plot_accident_bleve_impuls')
async def plot_accident_bleve_impuls_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_accident_bleve'))
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
                                      i18n=i18n, back_data='back_accident_bleve'))
    await callback.answer('')
