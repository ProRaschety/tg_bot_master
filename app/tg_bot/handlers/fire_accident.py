import logging
# import io
# import json

from dataclasses import asdict, astuple

from aiogram import Router, F, Bot
# from aiogram.filters import StateFilter
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
from app.tg_bot.utilities.misc_utils import get_picture_filling, plot_graph, get_plot_graph, get_dataframe_table, find_key_path, get_dict_value
# from app.tg_bot.utilities import tables
from app.tg_bot.utilities.tables import DataFrameBuilder
from app.tg_bot.utilities.result_plotter import DataPlotter

from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_keypad, get_inline_keyboard

from app.calculation.physics.accident_parameters import AccidentParameters
from app.calculation.physics.physics_utils import compute_characteristic_diameter, compute_density_gas_phase, compute_density_vapor_at_boiling, get_property_fuel, compute_stoichiometric_coefficient_with_fuel, compute_stoichiometric_coefficient_with_oxygen
from app.calculation.qra_mode import probits
from app.calculation.utilities import misc_utils

from app.infrastructure.database.models.calculations import AccidentModel
from app.infrastructure.database.models.substance import SubstanceModel

# from app.tg_bot.models.plotter import DataPlotterModel

# from pprint import pprint

log = logging.getLogger(__name__)

fire_accident_router = Router()
fire_accident_router.message.filter(IsGuest())
fire_accident_router.callback_query.filter(IsGuest())


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
            i18n=i18n, back_data='general_menu'
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


@fire_accident_router.callback_query(F.data == 'back_typical_accidents')
async def back_typical_accidents_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(
            i18n=i18n, back_data='general_menu'
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
            i18n=i18n, back_data='general_menu'
        )
    )
    await callback.answer('')


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
                           model=accident_model)
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
                           model=accident_model)
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

    context_data = await state.get_data()

    kb = InlineKeyboardModel(
        width=4, buttons='edit_fire_pool_kb', penultimate='run_fire_pool', ultimate='back_fire_pool', reference=None)

    context_data['keyboard_model'] = asdict(kb)

    text = ''
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_keyboard(keyboard=kb, i18n=i18n,
                                         )
    )
    await state.update_data(context_data)
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

    # kb = InlineKeyboardModel(
    #     width=4, buttons='edit_fire_pool_kb', penultimate='run_fire_pool', ultimate='back_fire_pool')
    # kb = InlineKeyboardModel(**context_data['keyboard_model'])
    # context_data['keyboard_model'] = asdict(kb)
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
    dpm = DataPlotter(i18n=i18n, request=callback.data, model=accident_model)
    data = dpm.action_request()
    media = plot_graph(data=data)

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
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_fire_pool'))

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))
    dpm = DataPlotter(i18n=i18n, request=callback.data, model=accident_model)
    data = dpm.action_request()
    media = plot_graph(data=data)

    text = i18n.probit_heat_flux.text()
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
                           model=accident_model)
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
                           model=accident_model)
    dataframe = dfb.action_request()

    media = get_dataframe_table(data=dataframe, results=True, row_num=7)

    text = i18n.cloud_explosion_result.text(
        distance=accident_model.explosion_distance)

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

    context_data = await state.get_data()

    kb = InlineKeyboardModel(
        width=3, buttons='edit_cloud_explosion_kb', penultimate='run_cloud_explosion', ultimate='back_cloud_explosion', reference=None)

    context_data['keyboard_model'] = asdict(kb)

    text = ''
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_keyboard(keyboard=kb, i18n=i18n,
                                         )
    )
    await state.update_data(context_data)
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['explosion_state_fuel']))
async def cloud_explosion_state_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, 'cloud_explosion_state_gas', 'cloud_explosion_state_dust',
                                      i18n=i18n, back_data='back_edit_cloud_explosion',
                                      )
    )


@fire_accident_router.callback_query(F.data.in_(['class_fuel']))
async def cloud_explosion_class_fuel_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.edit_cloud_explosion_class_fuel.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(4, 'class_fuel_first', 'class_fuel_second', 'class_fuel_third', 'class_fuel_fourth',
                                      i18n=i18n, back_data='back_edit_cloud_explosion',
                                      )
    )


@fire_accident_router.callback_query(F.data.in_(['class_space']))
async def cloud_explosion_class_space_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.edit_cloud_explosion_class_space.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(4,
                                      'class_space_first', 'class_space_second', 'class_space_third', 'class_space_fourth',
                                      i18n=i18n, back_data='back_edit_cloud_explosion',
                                      )
    )


@fire_accident_router.callback_query(F.data.in_(['cloud_explosion_condition']))
async def cloud_explosion_cond_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.cloud_explosion_condition.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'above_surface', 'on_surface',
                                      i18n=i18n, back_data='back_edit_cloud_explosion'
                                      )
    )


@fire_accident_router.callback_query(F.data.in_(['methodology']))
async def cloud_explosion_methodology_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.methodology.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(2,
                                      'methodology_404', 'methodology_2024',
                                      i18n=i18n, back_data='back_edit_cloud_explosion',
                                      )
    )


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

    if call_data == 'cloud_explosion_state_gas':
        accident_model.explosion_state_fuel = 'gas'
    elif call_data == 'cloud_explosion_state_dust':
        accident_model.explosion_state_fuel = 'dust'
    elif call_data == 'class_fuel_first':
        accident_model.substance.class_fuel = 1
    elif call_data == 'class_fuel_second':
        accident_model.substance.class_fuel = 2
    elif call_data == 'class_fuel_third':
        accident_model.substance.class_fuel = 3
    elif call_data == 'class_fuel_fourth':
        accident_model.substance.class_fuel = 4
    elif call_data == 'class_space_first':
        accident_model.class_space = 1
    elif call_data == 'class_space_second':
        accident_model.class_space = 2
    elif call_data == 'class_space_third':
        accident_model.class_space = 3
    elif call_data == 'class_space_fourth':
        accident_model.class_space = 4
    elif call_data == 'above_surface':
        accident_model.explosion_condition = call_data
    elif call_data == 'on_surface':
        accident_model.explosion_condition = call_data
    elif call_data == 'methodology_404':
        accident_model.methodology = call_data
    elif call_data == 'methodology_2024':
        accident_model.methodology = call_data

    text = i18n.cloud_explosion.text()

    dfb = DataFrameBuilder(i18n=i18n,  request=context_data.get(
        'temporary_request'), model=accident_model)
    dataframe = dfb.action_request()
    media = get_dataframe_table(data=dataframe)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(3,
                                      *i18n.get('edit_cloud_explosion_kb').split('\n'),
                                      i18n=i18n, penult_button='run_cloud_explosion', back_data='back_cloud_explosion'
                                      )
    )

    await state.update_data(accident_model=asdict(accident_model))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['correction_parameter', 'explosion_stc_coef_oxygen',
                                                 'explosion_mass_fuel', 'explosion_distance']))
async def edit_cloud_explosion_num_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    context_data = await state.get_data()

    path_edited_parameter = find_key_path(
        dictionary=context_data, key=callback.data)

    editable_parameter = get_dict_value(
        dictionary=context_data, keys_list=path_edited_parameter)

    text = i18n.temporary_parameter.text(
        text=i18n.get('name_' + callback.data), value=editable_parameter)

    kb = InlineKeyboardModel(
        width=3, buttons='edit_cloud_explosion_kb',
        penultimate='run_cloud_explosion', ultimate='back_cloud_explosion')

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
    dpm = DataPlotter(i18n=i18n, request=callback.data, model=accident_model)
    data = dpm.action_request()
    media = plot_graph(data=data)

    text = i18n.cloud_explosion.text()
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

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))
    dpm = DataPlotter(i18n=i18n, request=callback.data, model=accident_model)
    data = dpm.action_request()
    media = plot_graph(data=data)

    text = i18n.cloud_explosion.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'plot_accident_cloud_explosion_pressure', i18n=i18n, back_data='back_cloud_explosion'))
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['fire_ball', 'back_fire_ball']))
async def fire_ball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_typical_accidents'
                                      )
    )

    text = i18n.fire_ball.text()

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))

    dfb = DataFrameBuilder(i18n=i18n,  request='fire_ball',
                           model=accident_model)
    dataframe = dfb.action_request()

    media = get_dataframe_table(data=dataframe)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('fire_ball_kb_guest').split('\n') if role in ['guest'] else i18n.get('fire_ball_kb').split('\n'),
                                      i18n=i18n, back_data='back_typical_accidents'
                                      )
    )
    await state.update_data(temporary_request='fire_ball')


@fire_accident_router.callback_query(F.data.in_(['run_fire_ball']))
async def run_fire_ball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.calculation_progress.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_fire_ball'
                                      )
    )

    text = i18n.fire_ball.text()

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))

    dfb = DataFrameBuilder(i18n=i18n,  request='run_fire_ball',
                           model=accident_model)
    dataframe = dfb.action_request()

    media = get_dataframe_table(data=dataframe, row_num=7)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'plot_fire_ball', 'probit_fire_ball',
                                      i18n=i18n, back_data='back_fire_ball'
                                      )
    )
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_fire_ball']))
async def edit_fire_ball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)

    context_data = await state.get_data()

    kb = InlineKeyboardModel(
        width=4, buttons='edit_fire_ball_kb', penultimate='run_fire_ball', ultimate='back_fire_ball', reference=None)

    context_data['keyboard_model'] = asdict(kb)

    text = ''
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_keyboard(keyboard=kb, i18n=i18n,
                                         )
    )
    await state.update_data(context_data)
    await callback.answer('')


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
                                      i18n=i18n, back_data='back_fire_ball'
                                      )
    )

    text = i18n.get('repeated_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('fire_ball_kb_guest').split('\n'),
                                      i18n=i18n, back_data='back_fire_ball'
                                      )
    )
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['fire_ball_mass_fuel', 'fire_ball_distance']))
async def edit_ball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    context_data = await state.get_data()

    path_edited_parameter = find_key_path(
        dictionary=context_data, key=callback.data)
    editable_parameter = get_dict_value(
        dictionary=context_data, keys_list=path_edited_parameter)

    text = i18n.temporary_parameter.text(
        text=i18n.get('name_' + callback.data), value=editable_parameter)

    kb = InlineKeyboardModel(
        width=4, buttons='edit_fire_ball_kb', penultimate='run_fire_ball', ultimate='back_fire_ball')

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


@fire_accident_router.callback_query(F.data.in_(['plot_fire_ball']))
async def plot_fire_ball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_fire_ball'))

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))
    dpm = DataPlotter(i18n=i18n, request=callback.data, model=accident_model)
    data = dpm.action_request()
    media = plot_graph(data=data)

    text = i18n.fire_ball.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'probit_fire_ball', i18n=i18n, back_data='back_fire_ball'))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'probit_fire_ball')
async def probability_defeat_fireball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_fire_ball'))

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))
    dpm = DataPlotter(i18n=i18n, request=callback.data, model=accident_model)
    data = dpm.action_request()
    media = plot_graph(data=data)

    text = i18n.probit_heat_flux.text()
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
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_typical_accidents'
                                      )
    )

    text = i18n.accident_bleve.text()

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))

    dfb = DataFrameBuilder(i18n=i18n,  request='accident_bleve',
                           model=accident_model)
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
    text = i18n.calculation_progress.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_accident_bleve'
                                      )
    )

    text = i18n.accident_bleve.text()

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))

    dfb = DataFrameBuilder(i18n=i18n,  request='run_accident_bleve',
                           model=accident_model)
    dataframe = dfb.action_request()
    media = get_dataframe_table(data=dataframe, row_num=8)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'plot_accident_bleve_pressure', 'plot_accident_bleve_impuls',
                                      i18n=i18n, back_data='back_accident_bleve'
                                      )
    )
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
                                      i18n=i18n, back_data='back_accident_bleve'
                                      )
    )

    text = i18n.get('repeated_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('accident_bleve_kb_guest').split('\n'),
                                      i18n=i18n, back_data='back_accident_bleve'
                                      )
    )
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['edit_accident_bleve']))
async def edit_accident_bleve_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)

    context_data = await state.get_data()

    kb = InlineKeyboardModel(
        width=4, buttons='edit_accident_bleve_kb', penultimate='run_accident_bleve', ultimate='back_accident_bleve', reference=None)

    context_data['keyboard_model'] = asdict(kb)

    text = ''
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_keyboard(keyboard=kb, i18n=i18n,
                                         )
    )
    await state.update_data(context_data)
    await callback.answer('')


@fire_accident_router.callback_query(F.data.in_(['bleve_mass_fuel', 'bleve_distance']))
async def edit_bleve_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    context_data = await state.get_data()

    path_edited_parameter = find_key_path(
        dictionary=context_data, key=callback.data)

    editable_parameter = get_dict_value(
        dictionary=context_data, keys_list=path_edited_parameter)

    text = i18n.temporary_parameter.text(
        text=i18n.get('name_' + callback.data), value=editable_parameter)

    kb = InlineKeyboardModel(
        width=4, buttons='edit_accident_bleve_kb', penultimate='run_accident_bleve', ultimate='back_accident_bleve')

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


@fire_accident_router.callback_query(F.data == 'plot_accident_bleve_pressure')
async def plot_accident_bleve_pressure_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_accident_bleve'))

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))
    dpm = DataPlotter(i18n=i18n, request=callback.data, model=accident_model)
    data = dpm.action_request()
    media = plot_graph(data=data)

    text = i18n.accident_bleve.text()
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

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))
    dpm = DataPlotter(i18n=i18n, request=callback.data, model=accident_model)
    data = dpm.action_request()
    media = plot_graph(data=data)

    text = i18n.accident_bleve.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'plot_accident_bleve_pressure',
                                      i18n=i18n, back_data='back_accident_bleve'))
    await callback.answer('')
