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
from app.tg_bot.utilities.misc_utils import get_picture_filling, get_data_table
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb
from app.tg_bot.states.fsm_state_data import FSMFireAccidentForm
from app.calculation.physics.accident_parameters import AccidentParameters

log = logging.getLogger(__name__)

fire_accident_router = Router()
fire_accident_router.message.filter(IsGuest())
fire_accident_router.callback_query.filter(IsGuest())

kb_accidents = [1,
                'fire_pool',
                'fire_flash',
                'cloud_explosion',
                'horizontal_jet',
                'vertical_jet',
                'fire_ball',
                'bleve',]


@fire_accident_router.callback_query(F.data == 'back_typical_accidents')
async def back_typical_accidents_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.typical_accidents.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_accident_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*kb_accidents, i18n=i18n, param_back=True, back_data='back_fire_risks'))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'typical_accidents')
async def typical_accidents_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    data.setdefault("edit_typical_accidents", "0")
    text = i18n.typical_accidents.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_accident_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*kb_accidents, i18n=i18n, param_back=True, back_data='back_fire_risks'))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'fire_pool')
async def fire_pool_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    data.setdefault("accident_fire_pool_sub", "Бензин")
    data.setdefault("accident_fire_pool_temperature", "20")
    data.setdefault("accident_fire_pool_vel_wind", "0")
    data.setdefault("accident_fire_pool_pool_area", "314")

    text = i18n.fire_pool.text()
    f_pool = AccidentParameters(type_accident=callback.data)
    data_out, headers, label = f_pool.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    # media = get_picture_filling(file_path='temp_files/temp/fire_accident_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'fire_flash')
async def fire_flash_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    data.setdefault("accident_fire_flash_sub", "Бензин")
    data.setdefault("accident_fire_flash_temperature", "20")
    data.setdefault("accident_fire_flash_nkpr", "1.4")
    data.setdefault("accident_fire_flash_mass_fuel", "5")

    text = i18n.fire_flash.text()
    f_flash = AccidentParameters(type_accident=callback.data)
    data_out, headers, label = f_flash.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'cloud_explosion')
async def cloud_explosion_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    data.setdefault("accident_cloud_explosion_sub", "Метан")
    data.setdefault("accident_cloud_explosion_class_fuel", "4")
    data.setdefault("accident_cloud_explosion_class_space", "1")
    data.setdefault("accident_cloud_explosion_mass_fuel", "500")
    data.setdefault("accident_cloud_explosion_expl_cond",
                    "above_surface")  # on_surface

    text = i18n.cloud_explosion.text()

    cloud_exp = AccidentParameters(type_accident=callback.data)
    data_out, headers, label = cloud_exp.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'horizontal_jet')
async def horizontal_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.horizontal_jet.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_accident_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'vertical_jet')
async def vertical_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.vertical_jet.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_accident_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'fire_ball')
async def fire_ball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    data.setdefault("accident_fire_ball_sub", "Метан")
    data.setdefault("accident_fire_ball_center", "50")
    data.setdefault("accident_fire_ball_mass_fuel", "500")
    data.setdefault("accident_fire_ball_human_distance", "50")

    text = i18n.fire_ball.text()

    f_ball = AccidentParameters(type_accident=callback.data)
    data_out, headers, label = f_ball.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')


@fire_accident_router.callback_query(F.data == 'bleve')
async def bleve_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.bleve.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_accident_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')
