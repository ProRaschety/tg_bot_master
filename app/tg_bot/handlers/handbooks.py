import logging

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
from app.tg_bot.utilities.misc_utils import get_picture_filling
from app.tg_bot.states.fsm_state_data import FSMClimateForm
# from app.calculation.database_mode.substance import SubstanceDB
from app.calculation.database_mode.climate import Climate


log = logging.getLogger(__name__)


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
async def handbooks_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner, role: UserRole) -> None:
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
            'climate_guest',
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
