import logging

import io
from pathlib import Path
import json
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message, BufferedInputFile, FSInputFile, InputMediaPhoto, InputFile, InputMediaDocument
from aiogram.utils.chat_action import ChatActionSender
from aiogram.enums import ChatAction

from fluentogram import TranslatorRunner

from app.infrastructure.database.database.db import DB
from app.tg_bot.models.role import UserRole
from app.tg_bot.filters.filter_role import IsComrade
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb
from app.tg_bot.utilities.misc_utils import get_temp_folder, get_csv_file, get_csv_bt_file, get_picture_filling, get_initial_data_table
from app.calculation.fire_hazard_category.fire_hazard_categories import FireCategoryBuild, FireCategoryOutInstall


logging.getLogger('matplotlib.font_manager').disabled = True

log = logging.getLogger(__name__)

fire_category_router = Router()
fire_category_router.message.filter(IsComrade())
fire_category_router.callback_query.filter(IsComrade())


@fire_category_router.callback_query(F.data.in_(['fire_category', 'back_fire_category']))
async def fire_category_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.fire_category.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_category_logo.png')
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'category_build', 'category_premises', 'category_outdoor_installation', 'general_menu', i18n=i18n))

    await callback_data.answer('')


@fire_category_router.callback_query(F.data == 'category_build')
async def category_build_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    info_area = [
        {'area': 2500, 'category': 'А', 'efs': True},
        {'area': 1, 'category': 'Б', 'efs': True},
        {'area': 0, 'category': 'В1', 'efs': True},
        {'area': 0, 'category': 'В2', 'efs': True},
        {'area': 300, 'category': 'В3', 'efs': True},
        {'area': 2000, 'category': 'В4'},
        {'area': 100, 'category': 'Г'},
        {'area': 1000, 'category': 'Д'}
    ]

    fc_build = FireCategoryBuild()

    data_out, headers, label = fc_build.get_init_data_table(
        *info_area)
    media = get_initial_data_table(data=data_out, headers=headers, label=label)
    fc_build_data = fc_build.get_category_build(*info_area)
    text = i18n.category_build.text(category_build=fc_build_data)

    # media = get_picture_filling(
    #     file_path='temp_files/temp/fire_category_logo.png')

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_fire_category', i18n=i18n))
    await callback.answer('')


@fire_category_router.callback_query(F.data == 'category_premises')
async def category_premises_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.category_premises.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_category_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_fire_category', i18n=i18n))
    await callback.answer('')


@fire_category_router.callback_query((F.data.in_(['category_outdoor_installation', 'back_outdoor_installation',])))
async def category_outdoor_installation_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.category_outdoor_installation.text()

    data = await state.get_data()
    data.setdefault("substance", "Пропилен"),
    data.setdefault("pressure_substance_kPa", "2500"),
    data.setdefault("temperature_substance_C", "60"),
    data.setdefault("type_container", "Сепаратор"),
    data.setdefault("volume_container", "50.0"),
    data.setdefault("valve_closing_time", "120")

    fc_out_inst = FireCategoryOutInstall()
    data_out, headers, label = fc_out_inst.get_init_data_table()
    media = get_initial_data_table(data=data_out, headers=headers, label=label)

    await state.update_data(data)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'run_category_outdoor_installation', 'back_fire_category', i18n=i18n))
    await callback.answer('')


@fire_category_router.callback_query((F.data.in_(['run_category_outdoor_installation'])))
async def run_category_outdoor_installation_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    data.setdefault("substance", "Пропилен"),
    data.setdefault("pressure_substance_kPa", "2500"),
    data.setdefault("temperature_substance_C", "60"),
    data.setdefault("type_container", "Сепаратор"),
    data.setdefault("volume_container", "50.0"),
    data.setdefault("valve_closing_time", "120")

    cat_out_inst = FireCategoryOutInstall()
    data_out, headers, label = cat_out_inst.get_init_data_table()

    media = get_initial_data_table(data=data_out, headers=headers, label=label)

    category_out_inst = cat_out_inst.get_fire_hazard_categories()

    text = i18n.run_category_outdoor_installation.text(
        category_out_inst=category_out_inst)

    await state.update_data(data)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_outdoor_installation', i18n=i18n))
    await callback.answer('')

# @fire_category_router.callback_query(F.data == 'back_fire_category')
# async def back_fire_category_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
#     text = i18n.fire_category.text()
#     media = get_picture_filling(
#         file_path='temp_files/temp/fire_category_logo.png')
#     await bot.edit_message_media(
#         chat_id=callback.message.chat.id,
#         message_id=callback.message.message_id,
#         media=InputMediaPhoto(media=BufferedInputFile(
#             file=media, filename="pic_filling"), caption=text),
#         reply_markup=get_inline_cd_kb(1, 'category_build', 'category_premises', 'category_outdoor_installation', 'general_menu', i18n=i18n))
#     await callback.answer('')
