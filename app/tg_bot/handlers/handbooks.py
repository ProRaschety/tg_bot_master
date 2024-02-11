import logging
import json

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.chat_action import ChatActionSender
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message, FSInputFile, InputMediaPhoto, InputFile, BufferedInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from fluentogram import TranslatorRunner

from app.infrastructure.database.database.db import DB
from app.tg_bot.models.role import UserRole
from app.tg_bot.filters.filter_role import IsGuest
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb, get_inline_sub_kb, SubCallbackFactory
from app.tg_bot.utilities.misc_utils import get_temp_folder, get_picture_filling
from app.tg_bot.states.fsm_state_data import FSMClimateForm
from app.calculation.database_mode.substance import SubstanceDB
from app.calculation.database_mode.climate import Climate


log = logging.getLogger(__name__)
# logger = logging.getLogger(__name__)
# logger = logging.getLogger('matplotlib').setLevel(logging.ERROR)
# logger = logging.getLogger('PIL.PngImagePlugin').setLevel(logging.ERROR)


handbooks_router = Router()
handbooks_router.message.filter(IsGuest())
handbooks_router.callback_query.filter(IsGuest())


# handbooks_kb = [
#     'substances',
#     # 'typical_flammable_load',
#     'climate',
#     # 'frequencys',
#     # 'statistics',
#     'general_menu']


@handbooks_router.callback_query(F.data.in_(['handbooks', 'back_to_handbooks']), StateFilter(default_state))
async def handbooks_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    log.info('Запрос: Справочники')
    if role == "subscriber":
        handbooks_kb = [
            'substances',
            # 'typical_flammable_load',
            'climate',
            # 'frequencys',
            # 'statistics',
            'general_menu']
    elif role == "comrade":
        handbooks_kb = [
            'substances',
            # 'typical_flammable_load',
            'climate',
            # 'frequencys',
            # 'statistics',
            'general_menu']
    elif role == "admin":
        handbooks_kb = [
            'substances',
            # 'typical_flammable_load',
            'climate',
            # 'frequencys',
            # 'statistics',
            'general_menu']
    elif role == "owner":
        handbooks_kb = [
            'substances',
            # 'typical_flammable_load',
            'climate',
            # 'frequencys',
            # 'statistics',
            'general_menu']
    else:
        handbooks_kb = [
            'substances_guest',
            # 'typical_flammable_load',
            'climate',
            # 'frequencys',
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


@handbooks_router.callback_query(F.data.in_(['climate', 'stop_select_city']), StateFilter(default_state))
async def climate_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole, db: DB) -> None:
    log.info('Запрос: Справочник метеоданных')
    await state.set_state(state=None)
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    text = i18n.climate.text()
    # data = dict(await db.climate_tables.get_climate_region_list())
    # regions = list(data.values())
    # log.info(f'Данные из Справочника метеоданных: {regions[0]}')
    # data = dict(await db.climate_tables.get_climate_cities_list(region=regions[0]))
    # cities = list(data.values())
    # log.info(f'Данные из Справочника метеоданных: {cities}')

    # data = await db.climate_tables.get_climate_record(city='Москва')
    # print(data)
    # log.info(
    #     f'Данные из Справочника метеоданных: {data.region, data.city, data.cwind, data.pwinde, data.pwindne, data.temperature}')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'to_cities', 'back_to_handbooks', i18n=i18n))


@handbooks_router.callback_query(F.data.in_(["to_cities"]), StateFilter(default_state))
async def to_cities_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, db: DB) -> None:
    log.info('Запрос: Поиск по городам')
    chat_id = str(callback.message.chat.id)
    message_id = callback.message.message_id
    await state.update_data(chat_id=chat_id, cities_mes_id=message_id)
    text = i18n.to_cities.text()

    # markup = InlineKeyboardMarkup(
    #     inline_keyboard=[
    #         [InlineKeyboardButton(
    #             text="Выбрать населенный пункт 🔎",
    #             switch_inline_query_current_chat="")]
    #     ])

    markup = get_inline_cd_kb(1, i18n=i18n,
                              switch=True, switch_text='select_city', switch_data='',
                              param_back=True, back_data='stop_select_city')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=markup)
    await state.set_state(FSMClimateForm.select_city_state)


@handbooks_router.inline_query(StateFilter(FSMClimateForm.select_city_state))
async def show_cities(inline_query: InlineQuery, state: FSMContext, i18n: TranslatorRunner, db: DB):
    data = dict(await db.climate_tables.get_climate_cities())
    list_cities = list(data.values())
    # data = await state.get_data()
    # q_keys = SteelFireStrength(i18n=i18n, data=data)
    # list_cities = q_keys.get_list_num_profile()
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
    # strength_calculation = SteelFireStrength(i18n=i18n, data=data)
    # data_out, label = strength_calculation.get_init_data_table()
    # media = get_data_table(data=data_out, label=label)
    # ptm = strength_calculation.get_reduced_thickness()
    # await state.update_data(ptm=ptm)
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
