import logging

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
# , InlineQueryResultArticle, InputTextMessageContent
# from aiogram.types import InlineQuery
from aiogram.types import CallbackQuery, Message, BufferedInputFile, InputMediaPhoto, InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from fluentogram import TranslatorRunner

# from app.infrastructure.database.database.db import DB
from app.tg_bot.models.role import UserRole
from app.tg_bot.filters.filter_role import IsGuest
from app.calculation.physics.physics_utils import compute_specific_isobaric_heat_capacity_of_air
from app.tg_bot.utilities.misc_utils import get_picture_filling, get_data_table
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb
from app.tg_bot.states.fsm_state_data import FSMFireModelForm
from app.calculation.qra_mode.fire_risk_calculator import FireModel

log = logging.getLogger(__name__)

fire_model_router = Router()
fire_model_router.message.filter(IsGuest())
fire_model_router.callback_query.filter(IsGuest())

SFilter_analytics_model = [FSMFireModelForm.edit_analytics_model_width_room,
                           FSMFireModelForm.edit_analytics_model_lenght_room,
                           FSMFireModelForm.edit_analytics_model_height_room,
                           FSMFireModelForm.edit_analytics_model_air_temperature]


@fire_model_router.callback_query(F.data == 'fire_model')
async def fire_model_call(callback_data: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.fire_model.text()
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'analytics_model', i18n=i18n, param_back=True, back_data='back_fire_risks'))
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
        reply_markup=get_inline_cd_kb(1, 'analytics_model', i18n=i18n, param_back=True, back_data='back_fire_risks'))
    await callback.answer('')


"""______________________Аналитическая модель пожара______________________"""


@fire_model_router.callback_query(F.data.in_(['analytics_model', 'back_analytics_model', 'back_edit_analytics_model']))
async def analytics_model_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_fire_model'))

    data = await state.get_data()
    data.setdefault("edit_analytics_model_param", "0")

    data.setdefault("analytics_model_fire_load",
                    "Здания I-II ст. огнест.; бытовые и")
    data.setdefault("analytics_model_lenght_room", "10")
    data.setdefault("analytics_model_width_room", "5")
    data.setdefault("analytics_model_height_room", "3")
    data.setdefault("analytics_model_free_volume_room", "150")
    data.setdefault("analytics_model_initial_temperature", "25.0")
    data.setdefault("analytics_model_height_working_area", "1.7")
    data.setdefault("analytics_model_visibility", "20.0")
    data.setdefault("analytics_model_initial_illumination", "50.0")
    data.setdefault("analytics_model_reflection_coefficient", "0.30")
    data.setdefault("analytics_model_heat_loss", "0.55")
    data.setdefault("analytics_model_initial_oxygen", "0.230")
    data.setdefault("analytics_model_current_oxygen", "0.230")
    data.setdefault("analytics_model_exponent_taking_n", "3")
    await state.update_data(data)

    model = FireModel()
    substance = model.get_data_standard_fire_load(
        name=data.get('analytics_model_fire_load'))
    param_z = model.compute_z(h=float(data.get('analytics_model_height_working_area')), H=float(
        data.get("analytics_model_height_room")))
    cp = compute_specific_isobaric_heat_capacity_of_air(
        temperature=float(data.get('analytics_model_initial_temperature')))
    vol = float(data.get("analytics_model_lenght_room")) * float(data.get(
        "analytics_model_width_room")) * float(data.get("analytics_model_height_room"))

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('analytics_model_label')
    data_out = [
        {'id': i18n.get('exponent_taking_n'),
            'var': 'n',
            'unit_1': data.get('analytics_model_exponent_taking_n'),
            'unit_2': '-'},
        {'id': i18n.get('nondimensional_parameter'),
            'var': 'z',
            'unit_1': f'{param_z:.3f}',
            'unit_2': '-'},
        {'id': i18n.get('specific_isobaric_heat_capacity_of_gas'),
            'var': 'Cp',
            'unit_1': f'{cp:.5f}',
            'unit_2': i18n.get('kJ_per_kg_in_kelvin')},
        {'id': i18n.get('height_working_area'),
            'var': 'h',
            'unit_1': data.get('analytics_model_height_working_area'),
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('initial_indoor_air_temperature'),
            'var': 't',
            'unit_1': data.get('analytics_model_initial_temperature'),
            'unit_2': i18n.get('celsius')},
        {'id': i18n.get('free_volume_room'),
            'var': '0.8*V',
            'unit_1': f'{0.8 * vol:.2f}',
            'unit_2': i18n.get('meter_cub')},
        {'id': i18n.get('height_room'),
            'var': 'H',
            'unit_1': f'{float(data.get("analytics_model_height_room")):.1f}',
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('width_room'),
            'var': 'b',
            'unit_1': f'{float(data.get("analytics_model_width_room")):.1f}',
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('lenght_room'),
            'var': 'a',
            'unit_1': f'{float(data.get("analytics_model_lenght_room")):.1f}',
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('standard_fire_load'),
            'var': '',
            'unit_1': '',
            'unit_2': substance['substance_name']}]

    media = get_data_table(data=data_out, headers=headers,
                           label=label, row_num_patch=1)
    text = i18n.analytics_model.text()
    # media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_analytics_model', 'run_analytics_model', i18n=i18n, param_back=True, back_data='back_fire_model'))


@fire_model_router.callback_query(F.data.in_(['run_analytics_model']))
async def run_analytics_model_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.calculation_progress.text()
    await bot.edit_message_caption(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_analytics_model'))

    data = await state.get_data()

    model = FireModel()
    substance = model.get_data_standard_fire_load(
        name=data.get('analytics_model_fire_load'))
    param_z = model.compute_z(h=float(data.get('analytics_model_height_working_area')), H=float(
        data.get("analytics_model_height_room")))
    cp = compute_specific_isobaric_heat_capacity_of_air(
        temperature=float(data.get('analytics_model_initial_temperature')))
    vol = float(data.get("analytics_model_lenght_room")) * float(data.get(
        "analytics_model_width_room")) * float(data.get("analytics_model_height_room"))
    eta = model.compute_coefficient_completeness_combustion(
        initial_oxygen=0.230, current_oxygen=0.230)
    param_A = model.compute_A(
        psi=substance['specific_burnout_rate'], n=3, velocity=substance['linear_flame_velocity'])

    param_B = model.compute_B(phi=0.55, vol_free=vol*0.8,
                              cp=cp/1000, eta=eta, heat_comb=substance['lower_heat_of_combustion'])
    crit_temp = model.compute_time_by_temperature(
        B=param_B, A=param_A, z=param_z, n=3)
    crit_vis = model.compute_time_by_loss_visibility(
        B=param_B, A=param_A, z=param_z, Dm=substance['smoke_forming_ability'], vol_free=0.8*vol)
    crit_oxygen = model.compute_time_by_low_oxygen(
        B=param_B, A=param_A, z=param_z, n=3, vol_free=0.8*vol, lo2=substance['hydrogen_chloride_output'])
    crit_co2 = model.compute_critical_combustion_product(
        B=param_B, A=param_A, z=param_z, n=3, vol_free=0.8*vol, param=substance['oxygen_consumption'], lim_param=0.1100)
    crit_co = model.compute_critical_combustion_product(
        B=param_B, A=param_A, z=param_z, n=3, vol_free=0.8*vol, param=substance['carbon_dioxide_output'], lim_param=0.00116)
    crit_hcl = model.compute_critical_combustion_product(
        B=param_B, A=param_A, z=param_z, n=3, vol_free=0.8*vol, param=substance['carbon_monoxide_output'], lim_param=0.000023)

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('analytics_model_label')

    data_out = [
        {'id': i18n.get('content_hydrogen_chloride'),
            'var': 'τ_HCL',
            'unit_1': f'{crit_hcl:.2f}' if crit_hcl != 0 else "не опасно",
            'unit_2': i18n.get('seconds') if crit_hcl != 0 else "-"},
        {'id': i18n.get('content_carbon_monoxide'),
            'var': 'τ_CO2',
            'unit_1': f'{crit_co2:.2f}' if crit_co2 != 0 else "не опасно",
            'unit_2': i18n.get('seconds') if crit_co2 != 0 else "-"},
        {'id': i18n.get('content_carbon_dioxide'),
            'var': 'τ_CO',
            'unit_1': f'{crit_co:.2f}' if crit_co != 0 else "не опасно",
            'unit_2': i18n.get('seconds') if crit_co != 0 else "-"},
        {'id': i18n.get('low_content_oxygen'),
            'var': 'τ_О2',
            'unit_1': f'{crit_oxygen:.2f}',
            'unit_2': i18n.get('seconds')},
        {'id': i18n.get('loss_of_visibility'),
            'var': 'τ_v',
            'unit_1': f'{crit_vis:.2f}',
            'unit_2': i18n.get('seconds')},
        {'id': i18n.get('elevated_temperature'),
            'var': 'τ_T',
            'unit_1': f'{crit_temp:.2f}',
            'unit_2': i18n.get('seconds')},
        {'id': i18n.get('nondimensional_parameter'),
            'var': 'B',
            'unit_1': f'{param_B:.2f}',
            'unit_2': '-'},
        {'id': i18n.get('nondimensional_parameter'),
            'var': 'A',
            'unit_1': f'{param_A:.2e}',
            'unit_2': '-'},
        {'id': i18n.get('combustion_efficiency_coefficient'),
            'var': i18n.get('eta'),
            'unit_1': f'{eta:.3f}',
            'unit_2': '-'}]

    media = get_data_table(data=data_out, headers=headers,
                           label=label)
    text = i18n.run_analytics_model.text()
    # media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_analytics_model', i18n=i18n, param_back=True, back_data='fire_model'))
    # await state.update_data(data)


@fire_model_router.callback_query(F.data.in_(['edit_analytics_model', 'stop_edit_analytics_model']))
async def edit_analytics_model_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.set_state(state=None)
    edit_analytics_model_kb = [4, 'edit_lenght_room', 'edit_width_room',
                               'edit_height_room', 'edit_air_temperature', 'standard_fire_load']
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(*edit_analytics_model_kb, i18n=i18n, param_back=True, back_data='back_analytics_model'))


@fire_model_router.callback_query(F.data.in_(['standard_fire_load', 'stop_select_fire_load']))
async def standard_fire_load_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.set_state(state=None)
    data = await state.get_data()
    model = FireModel()
    model_data = model.get_data_standard_fire_load(
        name=data.get('analytics_model_fire_load'))

    # {'substance_name': 'Промтовары; текстильные изделия',
    #  'lower_heat_of_combustion': 16.7,
    #  'linear_flame_velocity': 0.0071,
    #  'specific_burnout_rate': 0.0244,
    #  'smoke_forming_ability': 60.6,
    #  'oxygen_consumption': 0.879,
    #  'carbon_dioxide_output': 0.0626,
    #  'carbon_monoxide_output': 0,
    #  'hydrogen_chloride_output': 2.56,
    #  'substance_type': 'solid'}

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('standard_fire_load')

    data_out = [
        {'id': i18n.get('hydrogen_chloride_output'),
            'var': 'HCl',
            'unit_1': f"{model_data['hydrogen_chloride_output']:.4f}",
            'unit_2': i18n.get('kg_per_kg')},
        {'id': i18n.get('carbon_monoxide_output'),
            'var': 'CO',
            'unit_1': f"{model_data['carbon_monoxide_output']:.4f}",
            'unit_2': i18n.get('kg_per_kg')},
        {'id': i18n.get('carbon_dioxide_output'),
            'var': 'CO2',
            'unit_1': f"{model_data['carbon_dioxide_output']:.4f}",
            'unit_2': i18n.get('kg_per_kg')},
        {'id': i18n.get('oxygen_consumption'),
            'var': 'LО2',
            'unit_1': f"{model_data['oxygen_consumption']:.4f}",
            'unit_2': i18n.get('kg_per_kg')},
        {'id': i18n.get('smoke_forming_ability'),
            'var': 'Dm',
            'unit_1': f"{model_data['smoke_forming_ability']:.1f}",
            'unit_2': i18n.get('neper_in_m_square_per_kg')},
        {'id': i18n.get('specific_burnout_rate'),
            'var': i18n.get('psi'),
            'unit_1': f"{model_data['specific_burnout_rate']:.4f}",
            'unit_2': i18n.get('kg_per_m_square_in_sec')},
        {'id': i18n.get('linear_flame_velocity'),
            'var': 'v',
            'unit_1': f"{model_data['linear_flame_velocity']:.4f}",
            'unit_2': i18n.get('m_per_sec')},
        {'id': i18n.get('lower_heat_of_combustion'),
            'var': 'Qн',
            'unit_1': f"{model_data['lower_heat_of_combustion']:.2f}",
            'unit_2': i18n.get('MJ_per_kg')},
        {'id': model_data['substance_name'],
            'var': '',
            'unit_1': '',
            'unit_2': ''}]
    media = get_data_table(data=data_out, headers=headers, label=label)
    text = i18n.standard_fire_load.text(
        standard_fire_load=model_data['substance_name'])
    # model = FireModel()
    # substance = model.get_data_standard_fire_load(
    #     name=data.get('analytics_model_fire_load'))
    # # data.setdefault("edit_analytics_model_param", "0")
    # # data.setdefault("analytics_model_fire_load", "fl_1")

    # headers = (i18n.get('name'), i18n.get('variable'),
    #            i18n.get('value'), i18n.get('unit'))
    # label = i18n.get('standard_fire_load')

    # data_out = [
    #     {'id': i18n.get('hydrogen_chloride_output'),
    #         'var': 'HCl',
    #         'unit_1': f'{0.0140:.4f}',
    #         'unit_2': i18n.get('kg_per_kg')},
    #     {'id': i18n.get('carbon_monoxide_output'),
    #         'var': 'CO',
    #         'unit_1': f'{0.0022:.4f}',
    #         'unit_2': i18n.get('kg_per_kg')},
    #     {'id': i18n.get('carbon_dioxide_output'),
    #         'var': 'CO2',
    #         'unit_1': f'{0.203:.4f}',
    #         'unit_2': i18n.get('kg_per_kg')},
    #     {'id': i18n.get('oxygen_consumption'),
    #         'var': 'LО2',
    #         'unit_1': f'{1.03:.2f}',
    #         'unit_2': i18n.get('kg_per_kg')},
    #     {'id': i18n.get('smoke_forming_ability'),
    #         'var': 'Dm',
    #         'unit_1': f'{270:.1f}',
    #         'unit_2': i18n.get('neper_in_m_square_per_kg')},
    #     {'id': i18n.get('specific_burnout_rate'),
    #         'var': i18n.get('psi'),
    #         'unit_1': f'{0.0145:.4f}',
    #         'unit_2': i18n.get('kg_per_m_square_in_sec')},
    #     {'id': i18n.get('linear_flame_velocity'),
    #         'var': 'v',
    #         'unit_1': f'{0.0108:.4f}',
    #         'unit_2': i18n.get('m_per_sec')},
    #     {'id': i18n.get('lower_heat_of_combustion'),
    #         'var': 'Qн',
    #         'unit_1': f'{13.8:.2f}',
    #         'unit_2': i18n.get('MJ_per_kg')},
    #     {'id': i18n.get('fl_1'),
    #         'var': '',
    #         'unit_1': '',
    #         'unit_2': ''}]

    # media = get_data_table(data=data_out, headers=headers,
    #                        label=label, row_num_patch=1)
    # text = i18n.standard_fire_load.text(standard_fire_load=i18n.get('fl_1'))
    # media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'select_standard_fire_load', i18n=i18n, param_back=True, back_data='back_edit_analytics_model'))
    # await state.update_data(data)


@fire_model_router.callback_query(F.data == 'select_standard_fire_load')
async def num_profile_inline_search_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    message_id = callback.message.message_id
    await state.update_data(chat_id=chat_id, message_id=message_id)
    text = i18n.select_standard_fire_load.text()
    # kb_1 = InlineKeyboardButton(
    #     text="Выбрать профиль 🔎", switch_inline_query_current_chat="")
    # kb_2 = InlineKeyboardButton(
    #     text="🔙 Назад", callback_data="stop_edit_strength")
    # kb = InlineKeyboardBuilder()
    # kb.row(kb_1, kb_2, width=1)
    # markup = kb.as_markup()
    markup = get_inline_cd_kb(1, i18n=i18n,
                              switch=True, switch_text='select_fire_load', switch_data='',
                              param_back=True, back_data='stop_select_fire_load')
    # markup = InlineKeyboardMarkup(inline_keyboard=[
    #     [InlineKeyboardButton(
    #         text="Выбрать профиль 🔎", switch_inline_query_current_chat="")]])
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=markup)
    await state.set_state(FSMFireModelForm.edit_standard_fire_load)


@fire_model_router.inline_query(StateFilter(FSMFireModelForm.edit_standard_fire_load))
async def show_standard_fire_load(inline_query: InlineQuery, state: FSMContext, i18n: TranslatorRunner):
    data = await state.get_data()
    sfl = FireModel()
    list_sfl = sfl.get_list_standard_fire_load()
    results = []
    for names in list_sfl:
        name = names[:34]
        if inline_query.query in str(name):
            results.append(InlineQueryResultArticle(id=str(name), title=f'{name}',
                                                    input_message_content=InputTextMessageContent(message_text=f'{name}')))
    await inline_query.answer(results=results[:25], cache_time=0, is_personal=True)


@fire_model_router.message(StateFilter(FSMFireModelForm.edit_standard_fire_load))
async def select_fire_load_inline_search_input(message: Message, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    message_id = data.get('message_id')

    model = FireModel()
    model_data = model.get_data_standard_fire_load(name=message.text)

    # {'substance_name': 'Промтовары; текстильные изделия',
    #  'lower_heat_of_combustion': 16.7,
    #  'linear_flame_velocity': 0.0071,
    #  'specific_burnout_rate': 0.0244,
    #  'smoke_forming_ability': 60.6,
    #  'oxygen_consumption': 0.879,
    #  'carbon_dioxide_output': 0.0626,
    #  'carbon_monoxide_output': 0,
    #  'hydrogen_chloride_output': 2.56,
    #  'substance_type': 'solid'}

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('standard_fire_load')

    data_out = [
        {'id': i18n.get('hydrogen_chloride_output'),
            'var': 'HCl',
            'unit_1': f"{model_data['hydrogen_chloride_output']:.4f}",
            'unit_2': i18n.get('kg_per_kg')},
        {'id': i18n.get('carbon_monoxide_output'),
            'var': 'CO',
            'unit_1': f"{model_data['carbon_monoxide_output']:.4f}",
            'unit_2': i18n.get('kg_per_kg')},
        {'id': i18n.get('carbon_dioxide_output'),
            'var': 'CO2',
            'unit_1': f"{model_data['carbon_dioxide_output']:.4f}",
            'unit_2': i18n.get('kg_per_kg')},
        {'id': i18n.get('oxygen_consumption'),
            'var': 'LО2',
            'unit_1': f"{model_data['oxygen_consumption']:.4f}",
            'unit_2': i18n.get('kg_per_kg')},
        {'id': i18n.get('smoke_forming_ability'),
            'var': 'Dm',
            'unit_1': f"{model_data['smoke_forming_ability']:.1f}",
            'unit_2': i18n.get('neper_in_m_square_per_kg')},
        {'id': i18n.get('specific_burnout_rate'),
            'var': i18n.get('psi'),
            'unit_1': f"{model_data['specific_burnout_rate']:.4f}",
            'unit_2': i18n.get('kg_per_m_square_in_sec')},
        {'id': i18n.get('linear_flame_velocity'),
            'var': 'v',
            'unit_1': f"{model_data['linear_flame_velocity']:.4f}",
            'unit_2': i18n.get('m_per_sec')},
        {'id': i18n.get('lower_heat_of_combustion'),
            'var': 'Qн',
            'unit_1': f"{model_data['lower_heat_of_combustion']:.2f}",
            'unit_2': i18n.get('MJ_per_kg')},
        {'id': model_data['substance_name'],
            'var': '',
            'unit_1': '',
            'unit_2': ''}]
    media = get_data_table(data=data_out, headers=headers, label=label)
    text = i18n.standard_fire_load.text(
        standard_fire_load=model_data['substance_name'])
    await message.delete()
    await state.set_state(state=None)

    await bot.edit_message_media(
        chat_id=message.chat.id,
        message_id=message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'select_standard_fire_load', i18n=i18n, param_back=True, back_data='back_edit_analytics_model'))
    await state.update_data(analytics_model_fire_load=message.text)
    # await state.update_data(analytics_model_fire_load=sfl_data['substance_name'],
    #                         lower_heat_of_combustion=sfl_data['lower_heat_of_combustion'],
    #                         linear_flame_velocity=sfl_data['linear_flame_velocity'],
    #                         specific_burnout_rate=sfl_data['specific_burnout_rate'],
    #                         smoke_forming_ability=sfl_data['smoke_forming_ability'],
    #                         oxygen_consumption=sfl_data['oxygen_consumption'],
    #                         carbon_dioxide_output=sfl_data['carbon_dioxide_output'],
    #                         carbon_monoxide_output=sfl_data['carbon_monoxide_output'],
    #                         hydrogen_chloride_output=sfl_data['hydrogen_chloride_output'])


@fire_model_router.callback_query(F.data.in_(['edit_lenght_room', 'edit_width_room', 'edit_height_room', 'edit_air_temperature']))
async def edit_analytics_model_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    if callback.data == 'edit_lenght_room':
        await state.set_state(FSMFireModelForm.edit_analytics_model_lenght_room)
    elif callback.data == 'edit_width_room':
        await state.set_state(FSMFireModelForm.edit_analytics_model_width_room)
    elif callback.data == 'edit_height_room':
        await state.set_state(FSMFireModelForm.edit_analytics_model_height_room)
    elif callback.data == 'edit_air_temperature':
        await state.set_state(FSMFireModelForm.edit_analytics_model_air_temperature)

    data = await state.get_data()
    state_data = await state.get_state()
    if state_data == FSMFireModelForm.edit_analytics_model_lenght_room:
        text = i18n.edit_analytics_model.text(analytics_model_param=i18n.get(
            "name_analytics_model_lenght_room"), edit_analytics_model=data.get("analytics_model_lenght_room", 0))
    elif state_data == FSMFireModelForm.edit_analytics_model_width_room:
        text = i18n.edit_analytics_model.text(analytics_model_param=i18n.get(
            "name_analytics_model_width_room"), edit_analytics_model=data.get("analytics_model_width_room", 0))
    elif state_data == FSMFireModelForm.edit_analytics_model_height_room:
        text = i18n.edit_analytics_model.text(analytics_model_param=i18n.get(
            "name_analytics_model_height_room"), edit_analytics_model=data.get("analytics_model_height_room", 0))
    elif state_data == FSMFireModelForm.edit_analytics_model_air_temperature:
        text = i18n.edit_analytics_model.text(analytics_model_param=i18n.get(
            "name_analytics_model_air_temperature"), edit_analytics_model=data.get("analytics_model_initial_temperature", 0))

    kb = ['one', 'two', 'three', 'four', 'five', 'six', 'seven',
          'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready']

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, *kb, i18n=i18n))
    await callback.answer('')


@fire_model_router.callback_query(StateFilter(*SFilter_analytics_model), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'dooble_zero', 'point', 'clear']))
async def edit_analytics_model_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    if state_data == FSMFireModelForm.edit_analytics_model_lenght_room:
        analytics_model_param = i18n.get("name_analytics_model_lenght_room")
    elif state_data == FSMFireModelForm.edit_analytics_model_width_room:
        analytics_model_param = i18n.get("name_analytics_model_width_room")
    elif state_data == FSMFireModelForm.edit_analytics_model_height_room:
        analytics_model_param = i18n.get("name_analytics_model_height_room")
    elif state_data == FSMFireModelForm.edit_analytics_model_air_temperature:
        analytics_model_param = i18n.get(
            "name_analytics_model_air_temperature")

    edit_data = await state.get_data()
    if callback.data == 'clear':
        await state.update_data(edit_analytics_model_param="")
        edit_d = await state.get_data()
        edit_data = edit_d.get('edit_analytics_model_param', 1)
        text = i18n.edit_analytics_model.text(
            analytics_model_param=analytics_model_param, edit_analytics_model=edit_data)

    else:
        edit_param_1 = edit_data.get('edit_analytics_model_param')
        edit_sum = edit_param_1 + i18n.get(callback.data)
        await state.update_data(edit_analytics_model_param=edit_sum)
        edit_data = await state.get_data()
        edit_param = edit_data.get('edit_analytics_model_param', 0)
        text = i18n.edit_analytics_model.text(
            analytics_model_param=analytics_model_param, edit_analytics_model=edit_param)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready', i18n=i18n))


@fire_model_router.callback_query(StateFilter(*SFilter_analytics_model), F.data.in_(['ready']))
async def edit_analytics_model_param_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    state_data = await state.get_state()
    data = await state.get_data()
    value = data.get("edit_analytics_model_param")
    if state_data == FSMFireModelForm.edit_analytics_model_lenght_room:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(analytics_model_lenght_room=value)
        else:
            await state.update_data(analytics_model_lenght_room=10)
    elif state_data == FSMFireModelForm.edit_analytics_model_width_room:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(analytics_model_width_room=value)
        else:
            await state.update_data(analytics_model_width_room=10)
    elif state_data == FSMFireModelForm.edit_analytics_model_height_room:
        if value != '' and value != '.' and (float(value)) > 0 and (float(value)) <= 6:
            await state.update_data(analytics_model_height_room=value)
        else:
            await state.update_data(analytics_model_height_room=6)
    elif state_data == FSMFireModelForm.edit_analytics_model_air_temperature:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(analytics_model_initial_temperature=value)
        else:
            await state.update_data(analytics_model_initial_temperature=25)

    data = await state.get_data()
    text = i18n.analytics_model.text()

    model = FireModel()
    substance = model.get_data_standard_fire_load(
        name=data.get('analytics_model_fire_load'))
    param_z = model.compute_z(h=float(data.get('analytics_model_height_working_area')), H=float(
        data.get("analytics_model_height_room")))
    cp = compute_specific_isobaric_heat_capacity_of_air(
        temperature=float(data.get('analytics_model_initial_temperature')))
    vol = float(data.get("analytics_model_lenght_room")) * float(data.get(
        "analytics_model_width_room")) * float(data.get("analytics_model_height_room"))

    headers = (i18n.get('name'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('analytics_model_label')
    data_out = [
        {'id': i18n.get('exponent_taking_n'),
            'var': 'n',
            'unit_1': data.get('analytics_model_exponent_taking_n'),
            'unit_2': '-'},
        {'id': i18n.get('nondimensional_parameter'),
            'var': 'z',
            'unit_1': f'{param_z:.3f}',
            'unit_2': '-'},
        {'id': i18n.get('specific_isobaric_heat_capacity_of_gas'),
            'var': 'Cp',
            'unit_1': f'{cp:.5f}',
            'unit_2': i18n.get('kJ_per_kg_in_kelvin')},
        {'id': i18n.get('height_working_area'),
            'var': 'h',
            'unit_1': data.get('analytics_model_height_working_area'),
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('initial_indoor_air_temperature'),
            'var': 't',
            'unit_1': data.get('analytics_model_initial_temperature'),
            'unit_2': i18n.get('celsius')},
        {'id': i18n.get('free_volume_room'),
            'var': '0.8*V',
            'unit_1': f'{0.8 * vol:.2f}',
            'unit_2': i18n.get('meter_cub')},
        {'id': i18n.get('height_room'),
            'var': 'H',
            'unit_1': f'{float(data.get("analytics_model_height_room")):.1f}',
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('width_room'),
            'var': 'b',
            'unit_1': f'{float(data.get("analytics_model_width_room")):.1f}',
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('lenght_room'),
            'var': 'a',
            'unit_1': f'{float(data.get("analytics_model_lenght_room")):.1f}',
            'unit_2': i18n.get('meter')},
        {'id': i18n.get('standard_fire_load'),
            'var': '',
            'unit_1': '',
            'unit_2': substance['substance_name']}]

    media = get_data_table(data=data_out, headers=headers,
                           label=label, row_num_patch=1)
    edit_analytics_model_kb = [4, 'edit_lenght_room', 'edit_width_room',
                               'edit_height_room', 'edit_air_temperature', 'standard_fire_load']
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*edit_analytics_model_kb, i18n=i18n, param_back=True, back_data='back_analytics_model'))
    await state.update_data(edit_analytics_model_param='')
    await state.set_state(state=None)
