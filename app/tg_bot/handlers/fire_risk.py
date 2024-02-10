import logging
import json

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.types import CallbackQuery, Message, BufferedInputFile, FSInputFile, InputMediaPhoto, InputFile, InputMediaDocument
from aiogram.utils.chat_action import ChatActionSender
from aiogram.enums import ChatAction

from fluentogram import TranslatorRunner

from app.infrastructure.database.database.db import DB
from app.tg_bot.filters.filter_role import IsComrade, IsSubscriber
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb
from app.tg_bot.utilities.misc_utils import get_temp_folder, get_csv_file, get_csv_bt_file, get_picture_filling, get_data_table
from app.calculation.qra_mode.fire_risk_calculator import FireRisk

log = logging.getLogger(__name__)

fire_risk_router = Router()
fire_risk_router.message.filter(IsSubscriber())
fire_risk_router.callback_query.filter(IsSubscriber())


@fire_risk_router.callback_query(F.data == 'fire_risks')
async def fire_risks_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.fire_risks.text()
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'fire_risks_calculator', 'typical_accidents', 'general_menu', i18n=i18n))
    await callback_data.answer('')


@fire_risk_router.callback_query(F.data == 'back_fire_risks')
async def back_fire_risks_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.fire_risks.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'fire_risks_calculator',
                                      'typical_accidents',
                                      'general_menu', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'back_typical_accidents')
async def back_typical_accidents_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.fire_risks.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'fire_pool',
                                      'fire_flash',
                                      'cloud_explosion',
                                      'horizontal_jet',
                                      'vertical_jet',
                                      'fire_ball',
                                      'bleve',
                                      'back_fire_risks', i18n=i18n))

    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'typical_accidents')
async def typical_accidents_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.fire_risks.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'fire_pool',
                                      'fire_flash',
                                      'cloud_explosion',
                                      'horizontal_jet',
                                      'vertical_jet',
                                      'fire_ball',
                                      'bleve',
                                      'back_fire_risks', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['fire_risks_calculator', 'back_fire_risks_calc']))
async def fire_risks_calculator_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.fire_risks_calculator.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'public', 'industrial', 'back_fire_risks', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['public', 'back_public']))
async def public_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    data.setdefault("fire_freq_pub", "0.04")
    data.setdefault("k_efs_pub", "0.9")
    data.setdefault("time_presence_pub", "2.0")
    data.setdefault("probity_evacuation_pub", "0.999")
    data.setdefault("time_evacuation_pub", "5.0")
    data.setdefault("time_blocking_paths_pub", "10")
    data.setdefault("time_crowding_pub", "1.0")
    data.setdefault("time_start_evacuation_pub", "1.0")
    data.setdefault("k_alarm_pub", "0.8")
    data.setdefault("k_evacuation_pub", "0.8")
    data.setdefault("k_smoke_pub", "0.8")

    text = i18n.public.text()
    log.info(str(callback.data))
    frisk = FireRisk(type_obj='public')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    # media = get_picture_filling(
    #     file_path='temp_files/temp/fire_risk_logo.png')

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'run_public', 'back_fire_risks_calc', i18n=i18n))
    await state.update_data(data)
    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'run_public')
async def run_public_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    data.setdefault("fire_freq_pub", "0.04")
    data.setdefault("k_efs_pub", "0.9")
    data.setdefault("time_presence_pub", "2.0")
    data.setdefault("probity_evacuation_pub", "0.999")
    data.setdefault("time_evacuation_pub", "5.0")
    data.setdefault("time_blocking_paths_pub", "10")
    data.setdefault("time_crowding_pub", "1.0")
    data.setdefault("time_start_evacuation_pub", "1.0")
    data.setdefault("k_alarm_pub", "0.8")
    data.setdefault("k_evacuation_pub", "0.8")
    data.setdefault("k_smoke_pub", "0.8")

    text = i18n.public.text()
    log.info(str(callback.data))
    frisk = FireRisk(type_obj='public')
    data_out, headers, label = frisk.get_result_data(**data)
    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=9)
    # media = get_picture_filling(
    #     file_path='temp_files/temp/fire_risk_logo.png')

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_public', i18n=i18n))
    await state.update_data(data)
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['industrial', 'back_industrial']))
async def industrial_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    data.setdefault("area_ind", "100.0")
    data.setdefault("fire_freq_ind", "0.04")
    data.setdefault("k_efs_ind", "0.9")
    data.setdefault("time_presence_ind", "2.0")
    data.setdefault("probity_evacuation_ind", "0.999")
    data.setdefault("time_evacuation_ind", "5.0")
    data.setdefault("time_blocking_paths_ind", "10")
    data.setdefault("time_crowding_ind", "1.0")
    data.setdefault("time_start_evacuation_ind", "1.0")
    data.setdefault("k_alarm_ind", "0.8")
    data.setdefault("k_evacuation_ind", "0.8")
    data.setdefault("k_smoke_ind", "0.8")
    data.setdefault("working_days_per_year_ind", "0.8")
    data.setdefault("emergency_escape_ind", "0.001")

    text = i18n.industrial.text()
    log.info(str(callback.data))
    frisk = FireRisk(type_obj='industrial')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'run_industrial', 'back_fire_risks_calc', i18n=i18n))
    await state.update_data(data)
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['run_industrial']))
async def run_industrial_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    data.setdefault("area_ind", "100.0")
    data.setdefault("fire_freq_ind", "0.04")
    data.setdefault("k_efs_ind", "0.9")
    data.setdefault("time_presence_ind", "2.0")
    data.setdefault("probity_evacuation_ind", "0.999")
    data.setdefault("time_evacuation_ind", "5.0")
    data.setdefault("time_blocking_paths_ind", "10")
    data.setdefault("time_crowding_ind", "1.0")
    data.setdefault("time_start_evacuation_ind", "1.0")
    data.setdefault("k_alarm_ind", "0.8")
    data.setdefault("k_evacuation_ind", "0.8")
    data.setdefault("k_smoke_ind", "0.8")
    data.setdefault("working_days_per_year_ind", "0.8")
    data.setdefault("emergency_escape_ind", "0.001")

    text = i18n.industrial.text()
    log.info(str(callback.data))
    frisk = FireRisk(type_obj='industrial')
    data_out, headers, label = frisk.get_result_data(**data)
    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=5)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_industrial', i18n=i18n))
    await state.update_data(data)
    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'fire_pool')
async def fire_pool_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.fire_pool.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'fire_flash')
async def fire_flash_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.fire_flash.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'cloud_explosion')
async def cloud_explosion_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.cloud_explosion.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'horizontal_jet')
async def horizontal_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.horizontal_jet.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'vertical_jet')
async def vertical_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.vertical_jet.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'fire_ball')
async def fire_ball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.fire_ball.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'bleve')
async def bleve_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.bleve.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')
