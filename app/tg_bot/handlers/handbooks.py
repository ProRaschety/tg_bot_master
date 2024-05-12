import logging
import time

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
# from aiogram.filters.callback_data import CallbackData
# from aiogram.utils.chat_action import ChatActionSender
# from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, BufferedInputFile
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from fluentogram import TranslatorRunner

from app.infrastructure.database.database.db import DB
from app.tg_bot.models.role import UserRole
from app.tg_bot.filters.filter_role import IsGuest
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb
from app.tg_bot.utilities.misc_utils import get_picture_filling, get_data_table, get_plot_graph
from app.tg_bot.states.fsm_state_data import FSMClimateForm, FSMFrequencyForm
# from app.calculation.database_mode.substance import SubstanceDB
from app.calculation.database_mode.climate import Climate
from app.calculation.qra_mode.fire_risk_calculator import FireRisk

log = logging.getLogger(__name__)


handbooks_router = Router()
handbooks_router.message.filter(IsGuest())
handbooks_router.callback_query.filter(IsGuest())

SFilter_area = [FSMFrequencyForm.edit_area_to_frequency]

# handbooks_kb = [
#     'substances',
#     # 'typical_flammable_load',
#     'climate',
#     # 'frequencies',
#     # 'statistics',
#     'general_menu']


@handbooks_router.callback_query(F.data.in_(['handbooks', 'back_to_handbooks']), StateFilter(default_state))
async def handbooks_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner, role: UserRole) -> None:
    log.info('Запрос: Справочники')
    if role == "subscriber":
        handbooks_kb = [
            'substances',
            # 'typical_flammable_load',
            'climate',
            'frequencies',
            # 'statistics',
            'general_menu']
    elif role == "comrade":
        handbooks_kb = [
            'substances',
            # 'typical_flammable_load',
            'climate',
            'frequencies',
            # 'statistics',
            'general_menu']
    elif role == "admin":
        handbooks_kb = [
            'substances',
            # 'typical_flammable_load',
            'climate',
            'frequencies',
            # 'statistics',
            'general_menu']
    elif role == "owner":
        handbooks_kb = [
            'substances',
            # 'typical_flammable_load',
            'climate',
            'frequencies',
            # 'statistics',
            'general_menu']
    else:
        handbooks_kb = [
            'substances_guest',
            # 'typical_flammable_load',
            'climate_guest',
            'frequencies',
            # 'statistics',
            'general_menu']

    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    text = i18n.handbooks.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, *handbooks_kb, i18n=i18n))


@handbooks_router.callback_query(F.data.in_(['climate', 'stop_select_city']))
async def climate_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    log.info('Запрос: Справочник метеоданных')
    await state.set_state(state=None)
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')

    text = i18n.climate.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        # reply_markup=get_inline_cd_kb(1, 'to_cities', 'back_to_handbooks', i18n=i18n))
        reply_markup=get_inline_cd_kb(1, 'to_cities', i18n=i18n, param_back=True, back_data='back_to_handbooks', check_role=True, role=role))


@handbooks_router.callback_query(F.data.in_(['climate_guest']))
async def climate_guest_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole, db: DB) -> None:
    log.info('Запрос: Справочник метеоданных')
    await state.set_state(state=None)
    # media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')

    data = await db.climate_tables.get_climate_record(city='Москва')
    clim = Climate()
    media = clim.get_climate_info(data=data)

    text = i18n.climate.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        # reply_markup=get_inline_cd_kb(1, 'to_cities', 'back_to_handbooks', i18n=i18n))
        reply_markup=get_inline_cd_kb(1, 'to_cities', i18n=i18n, param_back=True, back_data='back_to_handbooks', check_role=True, role=role))


@handbooks_router.callback_query(F.data.in_(["to_cities"]), StateFilter(default_state))
async def to_cities_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    log.info('Запрос: Поиск по городам')
    chat_id = str(callback.message.chat.id)
    message_id = callback.message.message_id
    await state.update_data(chat_id=chat_id, cities_mes_id=message_id)
    text = i18n.to_cities.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, i18n=i18n,
                                      switch=True, switch_text='select_city', switch_data='',
                                      param_back=True, back_data='stop_select_city'))
    await state.set_state(FSMClimateForm.select_city_state)


@handbooks_router.inline_query(StateFilter(FSMClimateForm.select_city_state))
async def show_cities(inline_query: InlineQuery, db: DB):
    data = dict(await db.climate_tables.get_climate_cities())
    list_cities = list(data.values())
    results = []
    for name in list_cities:
        if inline_query.query in str(name):
            results.append(InlineQueryResultArticle(id=str(name), title=f'{name}',
                                                    input_message_content=InputTextMessageContent(message_text=f'{name}')))
    await inline_query.answer(results=results[:30], cache_time=0, is_personal=True)


@handbooks_router.message(StateFilter(FSMClimateForm.select_city_state))
async def cities_inline_search_input(message: Message, bot: Bot, state: FSMContext, i18n: TranslatorRunner, db: DB) -> None:
    city = message.text
    await message.delete()
    await state.set_state(state=None)
    await state.update_data(city=city)
    data = await state.get_data()
    message_id = data.get('cities_mes_id')
    data = await db.climate_tables.get_climate_record(city=city)
    clim = Climate()
    media = clim.get_climate_info(data=data)
    # media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    text = i18n.to_cities_select.text(
        region=data.region, city=city, temp=data.temperature, cwind=data.cwind/100, velocity=data.windvelocity)
    await bot.edit_message_media(
        chat_id=message.chat.id,
        message_id=message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'to_cities', 'back_to_handbooks', i18n=i18n))


@handbooks_router.callback_query(F.data.in_(['frequencies', 'back_to_frequencies']))
async def frequencies_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    data = await state.get_data()
    data.setdefault("edit_frequencies_param", "1")
    data.setdefault("edit_area_to_frequency", "1")
    data.setdefault("type_building_to_frequency", "power_stations")
    data.setdefault("type_table_to_frequency", "table_1_3")
    data.setdefault("fire_frequency_industrial", "0.04")

    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    text = i18n.frequencies.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'table_1_3', 'table_2_3', 'table_2_4',
                                      i18n=i18n, param_back=True, back_data='back_to_handbooks'))
    await state.update_data(data)


@ handbooks_router.callback_query(F.data.in_(['table_1_3']))
async def table_st_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.update_data(type_table_to_frequency=callback.data)
    data = await state.get_data()
    unit = i18n.get('one_per_meter_square_in_year')
    area_to_frequencies = float(data.get("edit_area_to_frequency"))
    type_building = data.get('type_building_to_frequency')

    FireFrequency = FireRisk(type_obj='industrial')
    fire_frequency = FireFrequency.get_fire_frequency(
        area=area_to_frequencies, type_building=type_building, type_table=data.get('type_table_to_frequency'))

    headers = (i18n.get('name_obj_to_frequencies'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('frequencies_table_1_3')
    data_out = [
        {'id': i18n.get('fire_frequency'),
            'var': 'Q',
            'unit_1': f"{fire_frequency:.2e}",
            'unit_2': i18n.get('one_per_year')},
        {'id': i18n.get('area_to_frequencies'),
            'var': 'F',
            'unit_1': f"{area_to_frequencies:.1f}",
            'unit_2': i18n.get('meter_square')},
        {'id': i18n.get('textile_manufacturing'),
            'var': '○' if type_building != 'textile_manufacturing' else '●',
            'unit_1': f"{0.000022:.1e}",
            'unit_2': unit},
        {'id': i18n.get('hot_metal_rolling_shops'),
            'var': '○' if type_building != 'hot_metal_rolling_shops' else '●',
            'unit_1': f"{0.000019:.1e}",
            'unit_2': unit},
        {'id': i18n.get('meat_and_fish_products_processing_workshops'),
            'var': '○' if type_building != 'meat_and_fish_products_processing_workshops' else '●',
            'unit_1': f"{0.000015:.1e}",
            'unit_2': unit},
        {'id': i18n.get('foundries_and_smelting_shops'),
            'var': '○' if type_building != 'foundries_and_smelting_shops' else '●',
            'unit_1': f"{0.000019:.1e}",
            'unit_2': unit},
        {'id': i18n.get('workshops_for_processing_synthetic_rubber'),
            'var': '○' if type_building != 'workshops_for_processing_synthetic_rubber' else '●',
            'unit_1': f"{0.000027:.1e}",
            'unit_2': unit},
        {'id': i18n.get('tool_and_mechanical_workshops'),
            'var': '○' if type_building != 'tool_and_mechanical_workshops' else '●',
            'unit_1': f"{0.000006:.1e}",
            'unit_2': unit},
        {'id': i18n.get('warehouses_for_multi_item_products'),
            'var': '○' if type_building != 'warehouses_for_multi_item_products' else '●',
            'unit_1': f"{0.000090:.1e}",
            'unit_2': unit},
        {'id': i18n.get('chemical_products_warehouses'),
            'var': '○' if type_building != 'chemical_products_warehouses' else '●',
            'unit_1': f"{0.000012:.1e}",
            'unit_2': unit},
        {'id': i18n.get('power_stations'),
            'var': '○' if type_building != 'power_stations' else '●',
            'unit_1': f"{0.000022:.1e}",
            'unit_2': unit}]

    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=9)
    text = i18n.frequencies.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'type_to_table_1_3', 'area_to_frequencies', i18n=i18n, param_back=True, back_data='back_to_frequencies'))
    await state.update_data(fire_frequency_industrial=fire_frequency)


@ handbooks_router.callback_query(F.data.in_(['table_2_3']))
async def table_nd_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.update_data(type_table_to_frequency=callback.data)
    data = await state.get_data()
    unit = i18n.get('one_per_meter_square_in_year')
    area_to_frequencies = float(data.get("edit_area_to_frequency"))
    type_building = data.get('type_building_to_frequency', 'power_stations')

    FireFrequency = FireRisk(type_obj='industrial')
    fire_frequency = FireFrequency.get_fire_frequency(
        area=area_to_frequencies, type_building=type_building, type_table=data.get('type_table_to_frequency'))

    headers = (i18n.get('name_obj_to_frequencies'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('frequencies_table_2_3')
    data_out = [
        {'id': i18n.get('fire_frequency'),
            'var': 'Q',
            'unit_1': f"{fire_frequency:.2e}",
            'unit_2': i18n.get('one_per_year')},
        {'id': i18n.get('area_to_frequencies'),
            'var': 'F',
            'unit_1': f"{area_to_frequencies:.1f}",
            'unit_2': i18n.get('meter_square')},
        {'id': i18n.get('administrative_buildings_of_industrial_facilities'),
            'var': '○' if type_building != 'administrative_buildings_of_industrial_facilities' else '●',
            'unit_1': f"{0.000012:.1e}",
            'unit_2': unit},
        {'id': i18n.get('textile_manufacturing'),
            'var': '○' if type_building != 'textile_manufacturing' else '●',
            'unit_1': f"{0.000022:.1e}",
            'unit_2': unit},
        {'id': i18n.get('hot_metal_rolling_shops'),
            'var': '○' if type_building != 'hot_metal_rolling_shops' else '●',
            'unit_1': f"{0.000019:.1e}",
            'unit_2': unit},
        {'id': i18n.get('meat_and_fish_products_processing_workshops'),
            'var': '○' if type_building != 'meat_and_fish_products_processing_workshops' else '●',
            'unit_1': f"{0.000015:.1e}",
            'unit_2': unit},
        {'id': i18n.get('foundries_and_smelting_shops'),
            'var': '○' if type_building != 'foundries_and_smelting_shops' else '●',
            'unit_1': f"{0.000019:.1e}",
            'unit_2': unit},
        {'id': i18n.get('workshops_for_processing_synthetic_rubber'),
            'var': '○' if type_building != 'workshops_for_processing_synthetic_rubber' else '●',
            'unit_1': f"{0.000027:.1e}",
            'unit_2': unit},
        {'id': i18n.get('tool_and_mechanical_workshops'),
            'var': '○' if type_building != 'tool_and_mechanical_workshops' else '●',
            'unit_1': f"{0.000006:.1e}",
            'unit_2': unit},
        {'id': i18n.get('warehouses_for_multi_item_products'),
            'var': '○' if type_building != 'warehouses_for_multi_item_products' else '●',
            'unit_1': f"{0.000090:.1e}",
            'unit_2': unit},
        {'id': i18n.get('chemical_products_warehouses'),
            'var': '○' if type_building != 'chemical_products_warehouses' else '●',
            'unit_1': f"{0.000012:.1e}",
            'unit_2': unit},
        {'id': i18n.get('power_stations'),
            'var': '○' if type_building != 'power_stations' else '●',
            'unit_1': f"{0.000022:.1e}",
            'unit_2': unit}]

    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=10)
    text = i18n.frequencies.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'type_to_table_2_3', 'area_to_frequencies', i18n=i18n, param_back=True, back_data='back_to_frequencies'))
    await state.update_data(fire_frequency_industrial=fire_frequency)


@ handbooks_router.callback_query(F.data.in_(['table_2_4']))
async def table_th_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.update_data(type_table_to_frequency=callback.data)
    data = await state.get_data()
    area_to_frequencies = float(data.get("edit_area_to_frequency"))
    type_building = data.get('type_building_to_frequency', 'textile_industry')

    FireFrequency = FireRisk(type_obj='industrial')
    fire_frequency = FireFrequency.get_fire_frequency(
        area=area_to_frequencies, type_building=type_building, type_table=data.get('type_table_to_frequency'))

    headers = (i18n.get('name_obj_to_frequencies'),
               i18n.get('variable'), 'a', 'b')
    label = i18n.get('frequencies_table_2_4')
    data_out = [
        {'id': i18n.get('fire_frequency'),
            'var': 'Q',
            'unit_1': f"{fire_frequency:.2e}",
            'unit_2': i18n.get('one_per_year')},
        {'id': i18n.get('area_to_frequencies'),
            'var': 'F',
            'unit_1': f"{area_to_frequencies:.1f}",
            'unit_2': i18n.get('meter_square')},

        {'id': i18n.get('other_types_of_industrial_buildings'),
            'var': '○' if type_building != 'other_types_of_industrial_buildings' else '●',
            'unit_1': f"{0.00840:.5f}",
            'unit_2': 0.41},
        {'id': i18n.get('administrative_buildings_of_industrial_facilities'),
            'var': '○' if type_building != 'administrative_buildings_of_industrial_facilities' else '●',
            'unit_1': f"{0.00006:.5f}",
            'unit_2': 0.90},
        {'id': i18n.get('printing_enterprises_publishing_business'),
            'var': '○' if type_building != 'printing_enterprises_publishing_business' else '●',
            'unit_1': f"{0.00070:.5f}",
            'unit_2': 0.91},
        {'id': i18n.get('textile_industry'),
            'var': '○' if type_building != 'textile_industry' else '●',
            'unit_1': f"{0.00750:.5f}",
            'unit_2': 0.35},
        {'id': i18n.get('vehicle_servicing'),
            'var': '○' if type_building != 'vehicle_servicing' else '●',
            'unit_1': f"{0.00012:.5f}",
            'unit_2': 0.86},
        {'id': i18n.get('placement_of_electrical_equipment'),
            'var': '○' if type_building != 'placement_of_electrical_equipment' else '●',
            'unit_1': f"{0.00610:.5f}",
            'unit_2': 0.59},
        {'id': i18n.get('recycling_of_combustible_substances_chemical_industry'),
            'var': '○' if type_building != 'recycling_of_combustible_substances_chemical_industry' else '●',
            'unit_1': f"{0.00690:.5f}",
            'unit_2': 0.46},
        {'id': i18n.get('food_and_tobacco_industry_buildings'),
            'var': '○' if type_building != 'food_and_tobacco_industry_buildings' else '●',
            'unit_1': f"{0.00110:.5f}",
            'unit_2': 0.60}]

    start = time.time()
    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=8)
    end = time.time()
    total = end - start
    log.info(f"Время выполнения функции: {total}")

    text = i18n.frequencies.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'type_to_table_2_4', 'area_to_frequencies', i18n=i18n, param_back=True, back_data='back_to_frequencies'))
    await state.update_data(fire_frequency_industrial=fire_frequency)


@ handbooks_router.callback_query(F.data.in_(['type_to_table_1_3']))
async def type_to_table_st_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(FSMFrequencyForm.edit_type_to_table_1_3)
    kb = ['power_stations', 'chemical_products_warehouses', 'warehouses_for_multi_item_products', 'tool_and_mechanical_workshops', 'workshops_for_processing_synthetic_rubber', 'foundries_and_smelting_shops', 'meat_and_fish_products_processing_workshops',
          'hot_metal_rolling_shops', 'textile_manufacturing']
    text = i18n.name_frequency_type.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, *kb, i18n=i18n))
    await callback.answer('')


@ handbooks_router.callback_query(StateFilter(FSMFrequencyForm.edit_type_to_table_1_3),
                                  F.data.in_(['power_stations',
                                             'chemical_products_warehouses',
                                              'warehouses_for_multi_item_products',
                                              'tool_and_mechanical_workshops',
                                              'workshops_for_processing_synthetic_rubber',
                                              'foundries_and_smelting_shops',
                                              'meat_and_fish_products_processing_workshops',
                                              'hot_metal_rolling_shops',
                                              'textile_manufacturing']))
async def type_to_building_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.update_data(type_building_to_frequency=callback.data)

    data = await state.get_data()
    unit = i18n.get('one_per_meter_square_in_year')
    area_to_frequencies = float(data.get("edit_area_to_frequency"))
    type_building = data.get('type_building_to_frequency')

    FireFrequency = FireRisk(type_obj='industrial')
    fire_frequency = FireFrequency.get_fire_frequency(
        area=area_to_frequencies, type_building=type_building, type_table=data.get('type_table_to_frequency'))

    headers = (i18n.get('name_obj_to_frequencies'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))

    label = i18n.get('frequencies_table_1_3')
    data_out = [
        {'id': i18n.get('fire_frequency'),
            'var': 'Q',
            'unit_1': f"{fire_frequency:.2e}",
            'unit_2': i18n.get('one_per_year')},
        {'id': i18n.get('area_to_frequencies'),
            'var': 'F',
            'unit_1': f"{area_to_frequencies:.1f}",
            'unit_2': i18n.get('meter_square')},
        {'id': i18n.get('textile_manufacturing'),
            'var': '○' if type_building != 'textile_manufacturing' else '●',
            'unit_1': f"{0.000022:.1e}",
            'unit_2': unit},
        {'id': i18n.get('hot_metal_rolling_shops'),
            'var': '○' if type_building != 'hot_metal_rolling_shops' else '●',
            'unit_1': f"{0.000019:.1e}",
            'unit_2': unit},
        {'id': i18n.get('meat_and_fish_products_processing_workshops'),
            'var': '○' if type_building != 'meat_and_fish_products_processing_workshops' else '●',
            'unit_1': f"{0.000015:.1e}",
            'unit_2': unit},
        {'id': i18n.get('foundries_and_smelting_shops'),
            'var': '○' if type_building != 'foundries_and_smelting_shops' else '●',
            'unit_1': f"{0.000019:.1e}",
            'unit_2': unit},
        {'id': i18n.get('workshops_for_processing_synthetic_rubber'),
            'var': '○' if type_building != 'workshops_for_processing_synthetic_rubber' else '●',
            'unit_1': f"{0.000027:.1e}",
            'unit_2': unit},
        {'id': i18n.get('tool_and_mechanical_workshops'),
            'var': '○' if type_building != 'tool_and_mechanical_workshops' else '●',
            'unit_1': f"{0.000006:.1e}",
            'unit_2': unit},
        {'id': i18n.get('warehouses_for_multi_item_products'),
            'var': '○' if type_building != 'warehouses_for_multi_item_products' else '●',
            'unit_1': f"{0.000090:.1e}",
            'unit_2': unit},
        {'id': i18n.get('chemical_products_warehouses'),
            'var': '○' if type_building != 'chemical_products_warehouses' else '●',
            'unit_1': f"{0.000012:.1e}",
            'unit_2': unit},
        {'id': i18n.get('power_stations'),
            'var': '○' if type_building != 'power_stations' else '●',
            'unit_1': f"{0.000022:.1e}",
            'unit_2': unit}]

    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=9, sel_row_num=1)
    text = i18n.frequencies.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'type_to_table_1_3', 'area_to_frequencies', i18n=i18n, param_back=True, back_data='back_to_frequencies'))
    await state.update_data(fire_frequency_industrial=fire_frequency)


@ handbooks_router.callback_query(F.data.in_(['type_to_table_2_3']))
async def type_to_table_nd_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(FSMFrequencyForm.edit_type_to_table_2_3)
    kb = ['power_stations', 'chemical_products_warehouses', 'warehouses_for_multi_item_products', 'tool_and_mechanical_workshops', 'workshops_for_processing_synthetic_rubber', 'foundries_and_smelting_shops', 'meat_and_fish_products_processing_workshops',
          'hot_metal_rolling_shops', 'textile_manufacturing', 'administrative_buildings_of_industrial_facilities']
    text = i18n.name_frequency_type.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, *kb, i18n=i18n))
    await callback.answer('')


@ handbooks_router.callback_query(StateFilter(FSMFrequencyForm.edit_type_to_table_2_3),
                                  F.data.in_(['power_stations',
                                             'chemical_products_warehouses',
                                              'warehouses_for_multi_item_products',
                                              'tool_and_mechanical_workshops',
                                              'workshops_for_processing_synthetic_rubber',
                                              'foundries_and_smelting_shops',
                                              'meat_and_fish_products_processing_workshops',
                                              'hot_metal_rolling_shops',
                                              'textile_manufacturing',
                                              'administrative_buildings_of_industrial_facilities']))
async def type_to_building_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.update_data(type_building_to_frequency=callback.data)

    data = await state.get_data()
    unit = i18n.get('one_per_meter_square_in_year')
    area_to_frequencies = float(data.get("edit_area_to_frequency"))
    type_building = data.get('type_building_to_frequency')

    FireFrequency = FireRisk(type_obj='industrial')
    fire_frequency = FireFrequency.get_fire_frequency(
        area=area_to_frequencies, type_building=type_building, type_table=data.get('type_table_to_frequency'))
    headers = (i18n.get('name_obj_to_frequencies'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    label = i18n.get('frequencies_table_2_3')
    data_out = [
        {'id': i18n.get('fire_frequency'),
            'var': 'Q',
            'unit_1': f"{fire_frequency:.2e}",
            'unit_2': i18n.get('one_per_year')},
        {'id': i18n.get('area_to_frequencies'),
            'var': 'F',
            'unit_1': f"{area_to_frequencies:.1f}",
            'unit_2': i18n.get('meter_square')},
        {'id': i18n.get('administrative_buildings_of_industrial_facilities'),
            'var': '○' if type_building != 'administrative_buildings_of_industrial_facilities' else '●',
            'unit_1': f"{0.000012:.1e}",
            'unit_2': unit},
        {'id': i18n.get('textile_manufacturing'),
            'var': '○' if type_building != 'textile_manufacturing' else '●',
            'unit_1': f"{0.000022:.1e}",
            'unit_2': unit},
        {'id': i18n.get('hot_metal_rolling_shops'),
            'var': '○' if type_building != 'hot_metal_rolling_shops' else '●',
            'unit_1': f"{0.000019:.1e}",
            'unit_2': unit},
        {'id': i18n.get('meat_and_fish_products_processing_workshops'),
            'var': '○' if type_building != 'meat_and_fish_products_processing_workshops' else '●',
            'unit_1': f"{0.000015:.1e}",
            'unit_2': unit},
        {'id': i18n.get('foundries_and_smelting_shops'),
            'var': '○' if type_building != 'foundries_and_smelting_shops' else '●',
            'unit_1': f"{0.000019:.1e}",
            'unit_2': unit},
        {'id': i18n.get('workshops_for_processing_synthetic_rubber'),
            'var': '○' if type_building != 'workshops_for_processing_synthetic_rubber' else '●',
            'unit_1': f"{0.000027:.1e}",
            'unit_2': unit},
        {'id': i18n.get('tool_and_mechanical_workshops'),
            'var': '○' if type_building != 'tool_and_mechanical_workshops' else '●',
            'unit_1': f"{0.000006:.1e}",
            'unit_2': unit},
        {'id': i18n.get('warehouses_for_multi_item_products'),
            'var': '○' if type_building != 'warehouses_for_multi_item_products' else '●',
            'unit_1': f"{0.000090:.1e}",
            'unit_2': unit},
        {'id': i18n.get('chemical_products_warehouses'),
            'var': '○' if type_building != 'chemical_products_warehouses' else '●',
            'unit_1': f"{0.000012:.1e}",
            'unit_2': unit},
        {'id': i18n.get('power_stations'),
            'var': '○' if type_building != 'power_stations' else '●',
            'unit_1': f"{0.000022:.1e}",
            'unit_2': unit}]

    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=10)
    text = i18n.frequencies.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'type_to_table_2_3', 'area_to_frequencies', i18n=i18n, param_back=True, back_data='back_to_frequencies'))
    await state.update_data(fire_frequency_industrial=fire_frequency)


@ handbooks_router.callback_query(F.data.in_(['type_to_table_2_4']))
async def type_to_table_th_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(FSMFrequencyForm.edit_type_to_table_2_4)
    kb = ['food_and_tobacco_industry_buildings',
          'recycling_of_combustible_substances_chemical_industry',
          'placement_of_electrical_equipment',
          'vehicle_servicing',
          'textile_industry',
          'printing_enterprises_publishing_business',
          'administrative_buildings_of_industrial_facilities',
          'other_types_of_industrial_buildings']
    text = i18n.name_frequency_type.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, *kb, i18n=i18n))
    await callback.answer('')


@ handbooks_router.callback_query(StateFilter(FSMFrequencyForm.edit_type_to_table_2_4),
                                  F.data.in_(['food_and_tobacco_industry_buildings',
                                             'recycling_of_combustible_substances_chemical_industry',
                                              'placement_of_electrical_equipment',
                                              'vehicle_servicing',
                                              'textile_industry',
                                              'printing_enterprises_publishing_business',
                                              'administrative_buildings_of_industrial_facilities',
                                              'other_types_of_industrial_buildings']))
async def type_to_building_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.update_data(type_building_to_frequency=callback.data)
    data = await state.get_data()
    area_to_frequencies = float(data.get("edit_area_to_frequency"))
    type_building = data.get('type_building_to_frequency')

    FireFrequency = FireRisk(type_obj='industrial')
    fire_frequency = FireFrequency.get_fire_frequency(
        area=area_to_frequencies, type_building=type_building, type_table=data.get('type_table_to_frequency'))

    headers = (i18n.get('name_obj_to_frequencies'),
               i18n.get('variable'), 'a', 'b')
    label = i18n.get('frequencies_table_2_4')
    data_out = [
        {'id': i18n.get('fire_frequency'),
            'var': 'Q',
            'unit_1': f"{fire_frequency:.2e}",
            'unit_2': i18n.get('one_per_year')},
        {'id': i18n.get('area_to_frequencies'),
            'var': 'F',
            'unit_1': f"{area_to_frequencies:.1f}",
            'unit_2': i18n.get('meter_square')},

        {'id': i18n.get('other_types_of_industrial_buildings'),
            'var': '○' if type_building != 'other_types_of_industrial_buildings' else '●',
            'unit_1': f"{0.00840:.5f}",
            'unit_2': 0.41},
        {'id': i18n.get('administrative_buildings_of_industrial_facilities'),
            'var': '○' if type_building != 'administrative_buildings_of_industrial_facilities' else '●',
            'unit_1': f"{0.00006:.5f}",
            'unit_2': 0.90},
        {'id': i18n.get('printing_enterprises_publishing_business'),
            'var': '○' if type_building != 'printing_enterprises_publishing_business' else '●',
            'unit_1': f"{0.00070:.5f}",
            'unit_2': 0.91},
        {'id': i18n.get('textile_industry'),
            'var': '○' if type_building != 'textile_industry' else '●',
            'unit_1': f"{0.00750:.5f}",
            'unit_2': 0.35},
        {'id': i18n.get('vehicle_servicing'),
            'var': '○' if type_building != 'vehicle_servicing' else '●',
            'unit_1': f"{0.00012:.5f}",
            'unit_2': 0.86},
        {'id': i18n.get('placement_of_electrical_equipment'),
            'var': '○' if type_building != 'placement_of_electrical_equipment' else '●',
            'unit_1': f"{0.00610:.5f}",
            'unit_2': 0.59},
        {'id': i18n.get('recycling_of_combustible_substances_chemical_industry'),
            'var': '○' if type_building != 'recycling_of_combustible_substances_chemical_industry' else '●',
            'unit_1': f"{0.00690:.5f}",
            'unit_2': 0.46},
        {'id': i18n.get('food_and_tobacco_industry_buildings'),
            'var': '○' if type_building != 'food_and_tobacco_industry_buildings' else '●',
            'unit_1': f"{0.00110:.5f}",
            'unit_2': 0.60}]

    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=8)
    text = i18n.frequencies.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'type_to_table_2_4', 'area_to_frequencies', i18n=i18n, param_back=True, back_data='back_to_frequencies'))
    await state.update_data(fire_frequency_industrial=fire_frequency)


@ handbooks_router.callback_query(F.data.in_(['area_to_frequencies']))
async def area_to_frequencies_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(FSMFrequencyForm.edit_area_to_frequency)
    kb = ['one', 'two', 'three', 'four', 'five', 'six', 'seven',
          'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready']
    data = await state.get_data()
    text = i18n.edit_frequency.text(
        frequency_param=i18n.get("name_frequency_area"), edit_frequency=data.get("edit_area_to_frequency", 0))
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, *kb, i18n=i18n))
    await callback.answer('')


@ handbooks_router.callback_query(StateFilter(*SFilter_area), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'dooble_zero', 'point', 'clear']))
async def edit_frequency_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    # state_data = await state.get_state()
    frequency_param = i18n.get("name_frequency_area")

    edit_data = await state.get_data()
    if callback.data == 'clear':
        await state.update_data(edit_frequencies_param="")
        edit_d = await state.get_data()
        edit_data = edit_d.get('edit_frequencies_param', 1)
        text = i18n.edit_frequency.text(
            frequency_param=frequency_param, edit_frequency=edit_data)

    else:
        edit_param_1 = edit_data.get('edit_frequencies_param')
        edit_sum = edit_param_1 + i18n.get(callback.data)
        await state.update_data(edit_frequencies_param=edit_sum)
        edit_data = await state.get_data()
        edit_param = edit_data.get('edit_frequencies_param', 0)
        text = i18n.edit_frequency.text(
            frequency_param=frequency_param, edit_frequency=edit_param)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready', i18n=i18n))


@ handbooks_router.callback_query(StateFilter(*SFilter_area), F.data.in_(['ready']))
async def edit_area_freq_param_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    state_data = await state.get_state()
    data = await state.get_data()
    data_table = data.get('type_table_to_frequency')
    value = data.get("edit_frequencies_param")
    if state_data == FSMFrequencyForm.edit_area_to_frequency:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(edit_area_to_frequency=value)
        else:
            await state.update_data(edit_area_to_frequency='10')
    data = await state.get_data()
    unit = i18n.get('one_per_meter_square_in_year')
    area_to_frequencies = float(data.get("edit_area_to_frequency"))
    type_building = data.get('type_building_to_frequency')

    FireFrequency = FireRisk(type_obj='industrial')
    fire_frequency = FireFrequency.get_fire_frequency(
        area=area_to_frequencies, type_building=type_building, type_table=data_table)

    headers = (i18n.get('name_obj_to_frequencies'), i18n.get('variable'),
               i18n.get('value'), i18n.get('unit'))
    if data_table == 'table_1_3':
        kb = ['type_to_table_1_3', 'area_to_frequencies']
        row_num = 9
        label = i18n.get('frequencies_table_1_3')
        data_out = [
            {'id': i18n.get('fire_frequency'),
                'var': 'Q',
                'unit_1': f"{fire_frequency:.2e}",
                'unit_2': i18n.get('one_per_year')},
            {'id': i18n.get('area_to_frequencies'),
                'var': 'F',
                'unit_1': f"{area_to_frequencies:.1f}",
                'unit_2': i18n.get('meter_square')},
            {'id': i18n.get('textile_manufacturing'),
                'var': '○' if type_building != 'textile_manufacturing' else '●',
                'unit_1': f"{0.000022:.1e}",
                'unit_2': unit},
            {'id': i18n.get('hot_metal_rolling_shops'),
                'var': '○' if type_building != 'hot_metal_rolling_shops' else '●',
                'unit_1': f"{0.000019:.1e}",
                'unit_2': unit},
            {'id': i18n.get('meat_and_fish_products_processing_workshops'),
                'var': '○' if type_building != 'meat_and_fish_products_processing_workshops' else '●',
                'unit_1': f"{0.000015:.1e}",
                'unit_2': unit},
            {'id': i18n.get('foundries_and_smelting_shops'),
                'var': '○' if type_building != 'foundries_and_smelting_shops' else '●',
                'unit_1': f"{0.000019:.1e}",
                'unit_2': unit},
            {'id': i18n.get('workshops_for_processing_synthetic_rubber'),
                'var': '○' if type_building != 'workshops_for_processing_synthetic_rubber' else '●',
                'unit_1': f"{0.000027:.1e}",
                'unit_2': unit},
            {'id': i18n.get('tool_and_mechanical_workshops'),
                'var': '○' if type_building != 'tool_and_mechanical_workshops' else '●',
                'unit_1': f"{0.000006:.1e}",
                'unit_2': unit},
            {'id': i18n.get('warehouses_for_multi_item_products'),
                'var': '○' if type_building != 'warehouses_for_multi_item_products' else '●',
                'unit_1': f"{0.000090:.1e}",
                'unit_2': unit},
            {'id': i18n.get('chemical_products_warehouses'),
                'var': '○' if type_building != 'chemical_products_warehouses' else '●',
                'unit_1': f"{0.000012:.1e}",
                'unit_2': unit},
            {'id': i18n.get('power_stations'),
                'var': '○' if type_building != 'power_stations' else '●',
                'unit_1': f"{0.000022:.1e}",
                'unit_2': unit}]
    elif data_table == 'table_2_3':
        kb = ['type_to_table_2_3', 'area_to_frequencies']
        row_num = 10
        label = i18n.get('frequencies_table_2_3')
        data_out = [
            {'id': i18n.get('fire_frequency'),
                'var': 'Q',
                'unit_1': f"{fire_frequency:.2e}",
                'unit_2': i18n.get('one_per_year')},
            {'id': i18n.get('area_to_frequencies'),
                'var': 'F',
                'unit_1': f"{area_to_frequencies:.1f}",
                'unit_2': i18n.get('meter_square')},
            {'id': i18n.get('administrative_buildings_of_industrial_facilities'),
                'var': '○' if type_building != 'administrative_buildings_of_industrial_facilities' else '●',
                'unit_1': f"{0.000012:.1e}",
                'unit_2': unit},
            {'id': i18n.get('textile_manufacturing'),
                'var': '○' if type_building != 'textile_manufacturing' else '●',
                'unit_1': f"{0.000022:.1e}",
                'unit_2': unit},
            {'id': i18n.get('hot_metal_rolling_shops'),
                'var': '○' if type_building != 'hot_metal_rolling_shops' else '●',
                'unit_1': f"{0.000019:.1e}",
                'unit_2': unit},
            {'id': i18n.get('meat_and_fish_products_processing_workshops'),
                'var': '○' if type_building != 'meat_and_fish_products_processing_workshops' else '●',
                'unit_1': f"{0.000015:.1e}",
                'unit_2': unit},
            {'id': i18n.get('foundries_and_smelting_shops'),
                'var': '○' if type_building != 'foundries_and_smelting_shops' else '●',
                'unit_1': f"{0.000019:.1e}",
                'unit_2': unit},
            {'id': i18n.get('workshops_for_processing_synthetic_rubber'),
                'var': '○' if type_building != 'workshops_for_processing_synthetic_rubber' else '●',
                'unit_1': f"{0.000027:.1e}",
                'unit_2': unit},
            {'id': i18n.get('tool_and_mechanical_workshops'),
                'var': '○' if type_building != 'tool_and_mechanical_workshops' else '●',
                'unit_1': f"{0.000006:.1e}",
                'unit_2': unit},
            {'id': i18n.get('warehouses_for_multi_item_products'),
                'var': '○' if type_building != 'warehouses_for_multi_item_products' else '●',
                'unit_1': f"{0.000090:.1e}",
                'unit_2': unit},
            {'id': i18n.get('chemical_products_warehouses'),
                'var': '○' if type_building != 'chemical_products_warehouses' else '●',
                'unit_1': f"{0.000012:.1e}",
                'unit_2': unit},
            {'id': i18n.get('power_stations'),
                'var': '○' if type_building != 'power_stations' else '●',
                'unit_1': f"{0.000022:.1e}",
                'unit_2': unit}]
    elif data_table == 'table_2_4':
        kb = ['type_to_table_2_4', 'area_to_frequencies']
        row_num = 8
        headers = (i18n.get('name_obj_to_frequencies'),
                   i18n.get('variable'), 'a', 'b')
        label = i18n.get('frequencies_table_2_4')
        data_out = [
            {'id': i18n.get('fire_frequency'),
                'var': 'Q',
                'unit_1': f"{fire_frequency:.2e}",
                'unit_2': i18n.get('one_per_year')},
            {'id': i18n.get('area_to_frequencies'),
                'var': 'F',
                'unit_1': f"{area_to_frequencies:.1f}",
                'unit_2': i18n.get('meter_square')},

            {'id': i18n.get('other_types_of_industrial_buildings'),
                'var': '○' if type_building != 'other_types_of_industrial_buildings' else '●',
                'unit_1': f"{0.00840:.5f}",
                'unit_2': 0.41},
            {'id': i18n.get('administrative_buildings_of_industrial_facilities'),
                'var': '○' if type_building != 'administrative_buildings_of_industrial_facilities' else '●',
                'unit_1': f"{0.00006:.5f}",
                'unit_2': 0.90},
            {'id': i18n.get('printing_enterprises_publishing_business'),
                'var': '○' if type_building != 'printing_enterprises_publishing_business' else '●',
                'unit_1': f"{0.00070:.5f}",
                'unit_2': 0.91},
            {'id': i18n.get('textile_industry'),
                'var': '○' if type_building != 'textile_industry' else '●',
                'unit_1': f"{0.00750:.5f}",
                'unit_2': 0.35},
            {'id': i18n.get('vehicle_servicing'),
                'var': '○' if type_building != 'vehicle_servicing' else '●',
                'unit_1': f"{0.00012:.5f}",
                'unit_2': 0.86},
            {'id': i18n.get('placement_of_electrical_equipment'),
                'var': '○' if type_building != 'placement_of_electrical_equipment' else '●',
                'unit_1': f"{0.00610:.5f}",
                'unit_2': 0.59},
            {'id': i18n.get('recycling_of_combustible_substances_chemical_industry'),
                'var': '○' if type_building != 'recycling_of_combustible_substances_chemical_industry' else '●',
                'unit_1': f"{0.00690:.5f}",
                'unit_2': 0.46},
            {'id': i18n.get('food_and_tobacco_industry_buildings'),
                'var': '○' if type_building != 'food_and_tobacco_industry_buildings' else '●',
                'unit_1': f"{0.00110:.5f}",
                'unit_2': 0.60}]

    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=row_num)
    text = i18n.frequencies.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, *kb, i18n=i18n, param_back=True, back_data='back_to_frequencies'))
    await state.update_data(edit_frequencies_param='')
    await state.update_data(fire_frequency_industrial=fire_frequency)
    await callback.answer('')
