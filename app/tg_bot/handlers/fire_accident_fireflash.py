import logging

from dataclasses import asdict, astuple

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
# , InlineQueryResultArticle, InputTextMessageContent
# from aiogram.types import InlineQuery
from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaPhoto

from fluentogram import TranslatorRunner

# from app.infrastructure.database.database.db import DB
from app.tg_bot.models.role import UserRole
from app.tg_bot.models.keyboard import InlineKeyboardModel

from app.tg_bot.filters.filter_role import IsGuest
from app.tg_bot.states.fsm_state_data import FSMFireAccidentForm, FSMEditForm
from app.tg_bot.utilities import tables
from app.tg_bot.utilities.misc_utils import get_data_table, get_plot_graph, get_dataframe_table, find_key_path, get_dict_value
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_keypad, get_inline_keyboard

from app.calculation.physics.accident_parameters import AccidentParameters
from app.calculation.physics.physics_utils import compute_density_gas_phase, compute_density_vapor_at_boiling, get_property_fuel, compute_stoichiometric_coefficient_with_fuel, compute_stoichiometric_coefficient_with_oxygen

from app.infrastructure.database.models.calculations import AccidentModel
from app.infrastructure.database.models.substance import SubstanceModel


log = logging.getLogger(__name__)

fire_accident_fireflash_router = Router()
fire_accident_fireflash_router.message.filter(IsGuest())
fire_accident_fireflash_router.callback_query.filter(IsGuest())


@fire_accident_fireflash_router.callback_query(F.data.in_(['fire_flash', 'back_fire_flash']))
async def fire_flash_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_typical_accidents'))

    context_data = await state.get_data()
    text = i18n.fire_flash.text()

    accident_model = AccidentModel(**context_data.get('accident_model'))
    dataframe = tables.get_dataframe(
        request=callback.data, i18n=i18n, accident_model=accident_model)
    media = get_dataframe_table(data=dataframe)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_fire_flash',
                                      i18n=i18n,
                                      penult_button='run_fire_flash',
                                      back_data='back_typical_accidents'
                                      )
    )
    await state.update_data(temporary_request=callback.data)
    await callback.answer('')


@fire_accident_fireflash_router.callback_query(F.data.in_(['edit_fire_flash']))
async def edit_fire_flash_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(4, *i18n.get('edit_fire_flash_kb').split('\n'),
                                      i18n=i18n,
                                      penult_button='run_fire_flash',
                                      back_data='back_fire_flash'
                                      )
    )


@fire_accident_fireflash_router.callback_query(F.data.in_(['mass_vapor_fuel', 'lower_flammability_limit']))
async def edit_flash_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:

    context_data = await state.get_data()
    path_edited_parameter = find_key_path(
        dictionary=context_data, key=callback.data)

    editable_parameter = get_dict_value(
        dictionary=context_data, keys_list=path_edited_parameter)

    text = i18n.temporary_parameter.text(
        text=i18n.get('name_' + callback.data), value=editable_parameter)

    kb = InlineKeyboardModel(
        width=4, buttons='edit_fire_flash_kb', penultimate='run_fire_flash', ultimate='back_fire_flash')

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


# @fire_accident_fireflash_router.callback_query(StateFilter(*SFilter_fire_flash), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'dooble_zero', 'point', 'clear']))
# async def edit_fire_flash_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
#     state_data = await state.get_state()
#     if state_data == FSMFireAccidentForm.edit_fire_flash_mass_state:
#         fire_flash_param = i18n.get("name_fire_flash_mass")
#     elif state_data == FSMFireAccidentForm.edit_fire_flash_lcl_state:
#         fire_flash_param = i18n.get("name_fire_flash_lcl")

#     edit_data = await state.get_data()
#     if callback.data == 'clear':
#         await state.update_data(edit_accident_fire_flash_param="")
#         edit_d = await state.get_data()
#         edit_data = edit_d.get('edit_accident_fire_flash_param', 1)
#         text = i18n.edit_fire_flash.text(
#             fire_flash_param=fire_flash_param, edit_fire_flash=edit_data)

#     else:
#         edit_param_1 = edit_data.get('edit_accident_fire_flash_param')
#         edit_sum = edit_param_1 + i18n.get(callback.data)
#         await state.update_data(edit_accident_fire_flash_param=edit_sum)
#         edit_data = await state.get_data()
#         edit_param = edit_data.get('edit_accident_fire_flash_param', 0)
#         text = i18n.edit_fire_flash.text(
#             fire_flash_param=fire_flash_param, edit_fire_flash=edit_param)

#     await bot.edit_message_caption(
#         chat_id=callback.message.chat.id,
#         message_id=callback.message.message_id,
#         caption=text,
#         reply_markup=get_inline_cd_kb(3,
#                                       *i18n.get('calculator_buttons').split('\n'),
#                                       i18n=i18n))


# @fire_accident_fireflash_router.callback_query(StateFilter(*SFilter_fire_flash), F.data.in_(['ready']))
# async def edit_fire_flash_param_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
#     state_data = await state.get_state()
#     data = await state.get_data()
#     value = data.get("edit_accident_fire_flash_param")
#     if state_data == FSMFireAccidentForm.edit_fire_flash_mass_state:
#         if value != '' and value != '.' and (float(value)) > 0:
#             await state.update_data(accident_fire_flash_mass_fuel=value)
#         else:
#             await state.update_data(accident_fire_flash_mass_fuel=10)
#     elif state_data == FSMFireAccidentForm.edit_fire_flash_lcl_state:
#         if value != '' and value != '.' and (float(value)) > 0:
#             await state.update_data(accident_fire_flash_lcl=value)
#         else:
#             await state.update_data(accident_fire_flash_lcl=1.4)

#     data = await state.get_data()
#     text = i18n.fire_flash.text()
#     subst = data.get('accident_fire_flash_sub')
#     # f_flash = AccidentParameters(type_accident='fire_flash')
#     lcl = float(data.get('accident_fire_flash_lcl'))
#     air_density = compute_density_gas_phase(
#         molar_mass=28.97, temperature=float(data.get('accident_fire_flash_temperature')))
#     headers = (i18n.get('name'), i18n.get('variable'),
#                i18n.get('value'), i18n.get('unit'))
#     label = i18n.get('fire_flash')
#     data_out = [
#         {'id': i18n.get('radius_of_the_strait_above_which_an_explosive_zone_is_formed'), 'var': 'r',
#             'unit_1': data.get('accident_fire_flash_radius_pool'), 'unit_2': i18n.get('meter')},
#         {'id': i18n.get('mass_of_flammable_gases_entering_the_surrounding_space'), 'var': 'mг',  'unit_1': data.get(
#             'accident_fire_flash_mass_fuel'), 'unit_2': i18n.get('kilogram')},
#         {'id': i18n.get('saturated_fuel_vapor_density_at_boiling_point'),
#             'var': 'Cнкпр', 'unit_1': f"{lcl:.2f}", 'unit_2': i18n.get('percent_volume')},
#         {'id': i18n.get('ambient_air_density'), 'var': 'ρₒ',
#             'unit_1': f"{air_density:.2f}", 'unit_2': i18n.get('kg_per_m_cub')},
#         {'id': i18n.get('ambient_temperature'), 'var': 'tₒ', 'unit_1': data.get(
#             'accident_fire_flash_temperature'), 'unit_2': i18n.get('celsius')},
#         # {'id': i18n.get('substance'), 'var': '-', 'unit_1': i18n.get(subst), 'unit_2': '-'}
#     ]

#     media = get_data_table(data=data_out, headers=headers, label=label)
#     await bot.edit_message_media(
#         chat_id=callback.message.chat.id,
#         message_id=callback.message.message_id,
#         media=InputMediaPhoto(media=BufferedInputFile(
#             file=media, filename="pic_filling"), caption=text),
#         reply_markup=get_inline_cd_kb(1, 'edit_fire_flash', 'run_fire_flash', i18n=i18n, param_back=True, back_data='back_typical_accidents'))
#     await state.update_data(edit_accident_fire_flash_param='')
#     await state.set_state(state=None)


@fire_accident_fireflash_router.callback_query(F.data == 'run_fire_flash')
async def run_fire_flash_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    # data = await state.get_data()
    text = i18n.calculation_progress.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_fire_flash'))

    text = i18n.fire_flash.text()
    # subst = data.get('accident_fire_flash_sub')
    # rad_pool = float(data.get('accident_fire_flash_radius_pool'))
    # mass = float(data.get('accident_fire_flash_mass_fuel'))
    # lcl = float(data.get('accident_fire_flash_lcl'))
    # temperature = float(data.get('accident_fire_flash_temperature'))
    # molar_mass = float(data.get(
    #     'accident_fire_flash_molar_mass_fuel'))

    # density_fuel = compute_density_gas_phase(
    #     molar_mass=molar_mass, temperature=temperature)
    # f_flash = AccidentParameters(type_accident='fire_flash')
    # radius_LFL = f_flash.compute_radius_LFL(
    #     density=density_fuel, mass=mass, clfl=lcl)
    # height_LFL = f_flash.compute_height_LFL(
    #     density=density_fuel, mass=mass, clfl=lcl)

    # headers = (i18n.get('name'), i18n.get('variable'),
    #            i18n.get('value'), i18n.get('unit'))
    # label = i18n.get('fire_flash')
    # data_out = [
    #     {'id': i18n.get('radius_zone_Rf'), 'var': i18n.get('radius_Rf'),
    #         'unit_1': f"{(radius_LFL if radius_LFL>rad_pool else rad_pool) * 1.2:.2f}", 'unit_2': i18n.get('meter')},
    #     {'id': i18n.get('height_zone_LFL'), 'var': i18n.get('height_LFL'),
    #         'unit_1': f"{height_LFL:.2f}", 'unit_2': i18n.get('meter')},
    #     {'id': i18n.get('radius_zone_LFL'), 'var': i18n.get('radius_LFL'),
    #         'unit_1': f"{(radius_LFL if radius_LFL>rad_pool else rad_pool):.2f}", 'unit_2': i18n.get('meter')},
    #     {'id': i18n.get('density_flammable_gases_at_ambient_temperature'),
    #         'var': 'ρг', 'unit_1': f"{density_fuel:.3f}", 'unit_2': i18n.get('kg_per_m_cub')},
    #     # {'id': i18n.get('radius_of_the_strait_above_which_an_explosive_zone_is_formed'), 'var': 'r',
    #     #     'unit_1': f"{rad_pool:.2f}", 'unit_2': i18n.get('meter')},
    #     {'id': i18n.get('mass_of_flammable_gases_entering_the_surrounding_space'),
    #      'var': 'mг',  'unit_1': mass, 'unit_2': i18n.get('kilogram')},
    #     {'id': i18n.get('lower_concentration_limit_of_flame_propagation'),
    #         'var': i18n.get('lower_concentration_limit'), 'unit_1': f"{lcl:.2f}", 'unit_2': i18n.get('percent_volume')},
    #     # {'id': i18n.get('ambient_air_density'), 'var': 'ρₒ',
    #     #     'unit_1': f"{air_density:.2f}", 'unit_2': i18n.get('kg_per_m_cub')},
    #     {'id': i18n.get('ambient_temperature'), 'var': 'tₒ',
    #      'unit_1': temperature, 'unit_2': i18n.get('celsius')},
    #     # {'id': i18n.get('substance'), 'var': '-', 'unit_1': i18n.get(subst), 'unit_2': '-'}
    # ]

    # media = get_data_table(data=data_out, headers=headers,
    #                        label=label, results=True, row_num=4)

    context_data = await state.get_data()

    accident_model = AccidentModel(**context_data.get('accident_model'))
    dataframe = tables.get_dataframe(
        request=callback.data, i18n=i18n, accident_model=accident_model)
    media = get_dataframe_table(data=dataframe, results=True, row_num=7)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_fire_flash'))
    await callback.answer('')
