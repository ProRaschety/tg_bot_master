import logging

from dataclasses import asdict

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
from app.tg_bot.states.fsm_state_data import FSMEditForm
# from app.tg_bot.utilities import tables
from app.tg_bot.utilities.tables import DataFrameBuilder
from app.tg_bot.utilities.result_plotter import DataPlotter
from app.tg_bot.utilities.misc_utils import get_plot_graph, plot_graph, get_dataframe_table, find_key_path, get_dict_value, get_picture_filling
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_keypad, get_inline_keyboard

from app.calculation.physics.accident_parameters import AccidentParameters
from app.calculation.physics.physics_utils import compute_density_gas_phase, compute_density_vapor_at_boiling, get_property_fuel, compute_stoichiometric_coefficient_with_fuel, compute_stoichiometric_coefficient_with_oxygen

from app.infrastructure.database.models.calculations import AccidentModel
from app.infrastructure.database.models.substance import SubstanceModel

from pprint import pprint

log = logging.getLogger(__name__)

fire_accident_jet_and_flare_router = Router()
fire_accident_jet_and_flare_router.message.filter(IsGuest())
fire_accident_jet_and_flare_router.callback_query.filter(IsGuest())


@fire_accident_jet_and_flare_router.callback_query(F.data == 'jet_and_flare_combustion')
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
            *i18n.get('jet_and_flare_combustion_kb').split('\n'),
            i18n=i18n, back_data='back_jet_and_flare_combustion'
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

    await state.update_data(model=asdict(accident_model), temporary_parameter='', temporary_request='')


@fire_accident_jet_and_flare_router.callback_query(F.data == 'back_jet_and_flare_combustion')
async def back_typical_accidents_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(
            i18n=i18n, back_data='back_typical_accidents'
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
            *i18n.get('jet_and_flare_combustion_kb').split('\n'),
            i18n=i18n, back_data='back_typical_accidents'
        )
    )
    await callback.answer('')


@fire_accident_jet_and_flare_router.callback_query(F.data.in_(['flare_combustion']))
async def flare_combustion_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_jet_and_flare_combustion'
                                      )
    )

    text = i18n.flare_combustion.text()

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))

    dfb = DataFrameBuilder(i18n=i18n,  request='flare_combustion',
                           model=accident_model)
    dataframe = dfb.action_request()

    media = get_dataframe_table(data=dataframe)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('horizontal_jet_kb_guest').split('\n') if role in ['guest'] else i18n.get('horizontal_jet_kb').split('\n'),
                                      i18n=i18n, back_data='back_jet_and_flare_combustion'
                                      )
    )
    await state.update_data(temporary_request='flare_combustion')


@fire_accident_jet_and_flare_router.callback_query(F.data.in_(['horizontal_jet', 'back_horizontal_jet']))
async def horizontal_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_jet_and_flare_combustion'
                                      )
    )

    text = i18n.horizontal_jet.text()

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))

    dfb = DataFrameBuilder(i18n=i18n,  request='horizontal_jet',
                           model=accident_model)
    dataframe = dfb.action_request()

    media = get_dataframe_table(data=dataframe)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('horizontal_jet_kb_guest').split('\n') if role in ['guest'] else i18n.get('horizontal_jet_kb').split('\n'),
                                      i18n=i18n, back_data='back_jet_and_flare_combustion'
                                      )
    )
    await state.update_data(temporary_request='horizontal_jet')


@fire_accident_jet_and_flare_router.callback_query(F.data.in_(['edit_horizontal_jet_guest']))
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


@fire_accident_jet_and_flare_router.callback_query(F.data.in_(['edit_horizontal_jet']))
async def edit_horizontal_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)

    context_data = await state.get_data()

    kb = InlineKeyboardModel(
        width=1, buttons='edit_horizontal_jet_kb', ultimate='back_horizontal_jet', reference=None)

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

    # await bot.edit_message_reply_markup(
    #     chat_id=callback.message.chat.id,
    #     message_id=callback.message.message_id,
    #     reply_markup=get_inline_cd_kb(1, *i18n.get('edit_horizontal_jet_kb').split('\n'),
    #                                   i18n=i18n, back_data='back_horizontal_jet'))


@fire_accident_jet_and_flare_router.callback_query(F.data.in_(['vertical_jet', 'back_vertical_jet']))
async def vertical_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_jet_and_flare_combustion'
                                      )
    )

    text = i18n.vertical_jet.text()

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))

    dfb = DataFrameBuilder(i18n=i18n, request='vertical_jet',
                           model=accident_model)
    dataframe = dfb.action_request()

    media = get_dataframe_table(data=dataframe)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('vertical_jet_kb_guest').split('\n') if role in ['guest'] else i18n.get('vertical_jet_kb').split('\n'),
                                      i18n=i18n, back_data='back_jet_and_flare_combustion'
                                      )
    )
    await state.update_data(temporary_request='vertical_jet')


@fire_accident_jet_and_flare_router.callback_query(F.data.in_(['edit_vertical_jet_guest']))
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


@fire_accident_jet_and_flare_router.callback_query(F.data.in_(['edit_vertical_jet']))
async def edit_vertical_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)

    context_data = await state.get_data()

    kb = InlineKeyboardModel(
        width=1, buttons='edit_vertical_jet_kb', ultimate='back_vertical_jet', reference=None)

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


@fire_accident_jet_and_flare_router.callback_query(F.data.in_(['jet_state_fuel']))
async def hjet_state_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = ''

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      'jet_state_liquid_kb',
                                      'jet_state_comp_gas_kb',
                                      'jet_state_liq_gas_vap_kb', i18n=i18n
                                      )
    )


@fire_accident_jet_and_flare_router.callback_query(F.data.in_(['jet_state_liquid_kb', 'jet_state_comp_gas_kb', 'jet_state_liq_gas_vap_kb']))
async def horizontal_jet_state_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    call_data = callback.data
    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))

    if call_data == 'jet_state_liquid_kb':
        accident_model.jet_state_fuel = 'jet_state_liquid'
    elif call_data == 'jet_state_comp_gas_kb':
        accident_model.jet_state_fuel = 'jet_state_comp_gas'
    elif call_data == 'jet_state_liq_gas_vap_kb':
        accident_model.jet_state_fuel = 'jet_state_liq_gas_vap'

    text = i18n.horizontal_jet.text()

    dfb = DataFrameBuilder(i18n=i18n,  request=context_data.get(
        'temporary_request'), model=accident_model)
    dataframe = dfb.action_request()
    media = get_dataframe_table(data=dataframe)

    kb = InlineKeyboardModel(**context_data['keyboard_model'])
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_keyboard(keyboard=kb, i18n=i18n,
                                         )
    )
    await state.update_data(accident_model=asdict(accident_model))


@fire_accident_jet_and_flare_router.callback_query(F.data.in_(['jet_mass_rate', 'distance']))
async def edit_param_horizontal_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    context_data = await state.get_data()

    path_edited_parameter = find_key_path(
        dictionary=context_data, key=callback.data)
    editable_parameter = get_dict_value(
        dictionary=context_data, keys_list=path_edited_parameter)

    text = i18n.temporary_parameter.text(
        text=i18n.get('name_' + callback.data), value=editable_parameter)

    if context_data.get('temporary_request', None) == 'horizontal_jet':
        kb = InlineKeyboardModel(
            width=1, buttons='edit_horizontal_jet_kb', ultimate='back_horizontal_jet', reference=None)
    else:
        kb = InlineKeyboardModel(
            width=1, buttons='edit_vertical_jet_kb', ultimate='back_vertical_jet', reference=None)

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


@fire_accident_jet_and_flare_router.callback_query(F.data.in_(['plot_horizontal_jet']))
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

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))
    dpm = DataPlotter(i18n=i18n, request=callback.data, model=accident_model)
    data = dpm.action_request()
    media = plot_graph(data=data)

    text = i18n.horizontal_jet.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_horizontal_jet'))


@fire_accident_jet_and_flare_router.callback_query(F.data.in_(['plot_vertical_jet']))
async def vertical_jet_plot_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      i18n=i18n, back_data='back_vertical_jet'))

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))
    dpm = DataPlotter(i18n=i18n, request=callback.data, model=accident_model)
    data = dpm.action_request()
    media = plot_graph(data=data)

    text = i18n.vertical_jet.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      i18n=i18n, back_data='back_vertical_jet'))
