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
from app.tg_bot.filters.filter_role import IsComrade
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb
from app.tg_bot.utilities.misc_utils import get_temp_folder, get_csv_file, get_csv_bt_file, get_picture_filling, get_initial_data_table
from app.calculation.qra_mode.fire_risk_calculator import FireRisk

log = logging.getLogger(__name__)

fire_risk_router = Router()
fire_risk_router.message.filter(IsComrade())
fire_risk_router.callback_query.filter(IsComrade())


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


@fire_risk_router.callback_query(F.data == 'public')
async def public_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    info_build_public = {
        'fire_frequency': 0.04,
        'k_efs': 0.9,
        # 'probability_presence': 1,
        'time_presence': 2.0,
        'probability_evacuation': 0.999,
        'time_evacuation': 5.0,
        'time_blocking_paths': 9.5,
        'time_crowding': 1.0,
        'time_start_evacuation': 0.5,
        'k_alarm': 0.8,
        'k_evacuation': 0.8,
        'k_smoke': 0.8,
    }

    text = i18n.public.text()
    log.info(str(callback.data))
    frisk = FireRisk(type_obj=str(callback.data))
    data_out, headers, label = frisk.get_init_data(**info_build_public)
    media = get_initial_data_table(data=data_out, headers=headers, label=label)
    # media = get_picture_filling(
    #     file_path='temp_files/temp/fire_risk_logo.png')

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_fire_risks_calc', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'industrial')
async def industrial_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    info_build_industrial = {
        'area': 104,
        'fire_frequency': 2.2*10**-5,
        'working_days_per_year': 247,
        'time_presence': 12,
        'probability_evacuation': 0.999,
        'emergency escape': 0.03,
        'k_efs': 0.0,
        'k_alarm': 0.0,
        'k_evacuation': 0.0,
        'k_smoke': 0.0,
    }

    text = i18n.industrial.text()
    log.info(str(callback.data))
    frisk = FireRisk(type_obj=str(callback.data))
    data_out, headers, label = frisk.get_init_data(**info_build_industrial)
    media = get_initial_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_fire_risks_calc', i18n=i18n))
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
