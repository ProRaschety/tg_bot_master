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
from app.calculation.physics.physics_utils import compute_specific_isobaric_heat_capacity_of_air
from app.tg_bot.utilities.misc_utils import get_picture_filling, get_data_table
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb
from app.tg_bot.states.fsm_state_data import FSMFireRiskForm
from app.calculation.qra_mode.fire_risk_calculator import FireRisk

log = logging.getLogger(__name__)

fire_model_router = Router()
fire_model_router.message.filter(IsGuest())
fire_model_router.callback_query.filter(IsGuest())


@fire_model_router.callback_query(F.data == 'fire_model')
async def fire_model_call(callback_data: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.fire_model.text()
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'integral_model', i18n=i18n, param_back=True, back_data='back_fire_risks'))
    await callback_data.answer('')


@fire_model_router.callback_query(F.data == 'back_fire_model')
async def back_fire_model_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.fire_model.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'integral_model', i18n=i18n, param_back=True, back_data='back_fire_risks'))
    await callback.answer('')


"""______________________Интегральная модель пожара______________________"""


@fire_model_router.callback_query(F.data.in_(['integral_model', 'back_integral_model', 'back_edit_integral_model']))
async def integral_model_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    data.setdefault("edit_integral_model_param", "0")

    data.setdefault("integral_model_fire_load", "fl_1")
    data.setdefault("integral_model_lenght_room", "10")
    data.setdefault("integral_model_width_room", "5")
    data.setdefault("integral_model_height_room", "3")
    data.setdefault("integral_model_free_volume_room", "150")
    data.setdefault("integral_model_initial_temperature", "25.0")
    data.setdefault("integral_model_height_working_area", "1.7")
    data.setdefault("integral_model_visibility", "20.0")
    data.setdefault("integral_model_initial_illumination", "50.0")
    data.setdefault("integral_model_reflection_coefficient", "0.30")
    data.setdefault("integral_model_heat_loss", "0.55")
    data.setdefault("integral_model_initial_oxygen", "0.230")
    data.setdefault("integral_model_current_oxygen", "0.230")

    cp = compute_specific_isobaric_heat_capacity_of_air(
        temperature=float(data.get('integral_model_initial_temperature')))
    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('integral_model_label')
    data_out = [
        {'id': i18n.get('specific_isobaric_heat_capacity_of_gas'),
            'var': 'Cp',
            'unit_1': f'{cp:.5f}',
            'unit_2': i18n.get('kJ_per_kg_in_kelvin')},
        {'id': i18n.get('height_working_area'),
            'var': 'h',
            'unit_1': data.get('integral_model_height_working_area'),
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('initial_indoor_air_temperature'),
            'var': 'r',
            'unit_1': data.get('integral_model_initial_temperature'),
            'unit_2': i18n.get('celsius')},
        {'id': i18n.get('free_volume_room'),
            'var': '0.8*V',
            'unit_1': f'{0:.2f}',
            'unit_2': i18n.get('meter_cub')},
        {'id': i18n.get('height_room'),
            'var': 'H',
            'unit_1': f'{0:.2f}',
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('width_room'),
            'var': 'b',
            'unit_1': f'{0:.2f}',
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('lenght_room'),
            'var': 'a',
            'unit_1': 0,
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('fire_load'),
            'var': '',
            'unit_1': '',
            'unit_2': i18n.get(data.get('integral_model_fire_load'))}]
    media = get_data_table(data=data_out, headers=headers, label=label)
    text = i18n.integral_model.text()
    # media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_integral_model', 'run_integral_model', i18n=i18n, param_back=True, back_data='back_fire_model'))
    await state.update_data(data)


@fire_model_router.callback_query(F.data.in_(['run_integral_model']))
async def run_integral_model_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    # data.setdefault("edit_integral_model_param", "0")
    # data.setdefault("integral_model_fire_load", "fl_1")

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('integral_model_label')

    data_out = [
        {'id': i18n.get('content_hydrogen_chloride'),
            'var': 'τ_HCL',
            'unit_1': f'{0:.1f}',
            'unit_2': i18n.get('seconds')},
        {'id': i18n.get('content_carbon_monoxide'),
            'var': 'τ_CO2',
            'unit_1': f'{0:.1f}',
            'unit_2': i18n.get('seconds')},
        {'id': i18n.get('content_carbon_dioxide'),
            'var': 'τ_CO',
            'unit_1': f'{0:.1f}',
            'unit_2': i18n.get('seconds')},
        {'id': i18n.get('low_content_oxygen'),
            'var': 'τ_О2',
            'unit_1': f'{0:.1f}',
            'unit_2': i18n.get('seconds')},
        {'id': i18n.get('loss_of_visibility'),
            'var': 'τ_v',
            'unit_1': f'{0:.1f}',
            'unit_2': i18n.get('seconds')},
        {'id': i18n.get('elevated_temperature'),
            'var': 'τ_T',
            'unit_1': f'{0:.1f}',
            'unit_2': i18n.get('seconds')},
        {'id': i18n.get('nondimensional_parameter'),
            'var': 'B',
            'unit_1': f'{0:.1f}',
            'unit_2': '-'},
        {'id': i18n.get('nondimensional_parameter'),
            'var': 'A',
            'unit_1': f'{0:.2f}',
            'unit_2': '-'},
        {'id': i18n.get('combustion_efficiency_coefficient'),
            'var': i18n.get('eta'),
            'unit_1': f'{0:.2f}',
            'unit_2': '-'}]
    media = get_data_table(data=data_out, headers=headers, label=label)
    text = i18n.integral_model.text()
    # media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, i18n=i18n, param_back=True, back_data='back_fire_model'))
    # await state.update_data(data)


@fire_model_router.callback_query(F.data.in_(['edit_integral_model', 'stop_edit_integral_model']))
async def edit_integral_model_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.set_state(state=None)
    edit_integral_model_kb = [1, 'standard_fire_load']
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(*edit_integral_model_kb, i18n=i18n, param_back=True, back_data='back_integral_model'))


@fire_model_router.callback_query(F.data.in_(['standard_fire_load']))
async def standard_fire_load_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    # data.setdefault("edit_integral_model_param", "0")
    # data.setdefault("integral_model_fire_load", "fl_1")

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('standard_fire_load')

    data_out = [
        {'id': i18n.get('hydrogen_chloride_output'),
            'var': 'HCl',
            'unit_1': f'{0.0140:.4f}',
            'unit_2': i18n.get('kg_per_kg')},
        {'id': i18n.get('carbon_monoxide_output'),
            'var': 'CO',
            'unit_1': f'{0.0022:.4f}',
            'unit_2': i18n.get('kg_per_kg')},
        {'id': i18n.get('carbon_dioxide_output'),
            'var': 'CO2',
            'unit_1': f'{0.203:.4f}',
            'unit_2': i18n.get('kg_per_kg')},
        {'id': i18n.get('oxygen_consumption'),
            'var': 'LО2',
            'unit_1': f'{1.03:.2f}',
            'unit_2': i18n.get('kg_per_kg')},
        {'id': i18n.get('smoke_forming_ability'),
            'var': 'Dm',
            'unit_1': f'{270:.1f}',
            'unit_2': i18n.get('neper_in_m_square_per_kg')},
        {'id': i18n.get('specific_burnout_rate'),
            'var': i18n.get('psi'),
            'unit_1': f'{0.0145:.4f}',
            'unit_2': i18n.get('kg_per_m_square_in_sec')},
        {'id': i18n.get('linear_flame_velocity'),
            'var': 'v',
            'unit_1': f'{0.0108:.4f}',
            'unit_2': i18n.get('m_per_sec')},
        {'id': i18n.get('lower_heat_of_combustion'),
            'var': 'Qн',
            'unit_1': f'{13.8:.2f}',
            'unit_2': i18n.get('MJ_per_kg')},
        {'id': i18n.get('fl_1'),
            'var': '-',
            'unit_1': '-',
            'unit_2': '-'}]
    media = get_data_table(data=data_out, headers=headers, label=label)
    text = i18n.standard_fire_load.text()
    # media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, i18n=i18n, param_back=True, back_data='back_edit_integral_model'))
    # await state.update_data(data)
