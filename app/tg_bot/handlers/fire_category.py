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

from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb
from app.tg_bot.utilities.misc_utils import get_temp_folder, get_csv_file, get_csv_bt_file, get_picture_filling

logging.getLogger('matplotlib.font_manager').disabled = True
log = logging.getLogger(__name__)


fire_category_router = Router()


@fire_category_router.callback_query(F.data.in_(['fire_category', 'back_fire_category']))
async def fire_category_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.fire_category.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_category_logo.png')
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'category_build', 'category_room', 'category_outdoor_installation', 'general_menu', i18n=i18n))

    await callback_data.answer('')


@fire_category_router.callback_query(F.data == 'category_build')
async def category_build_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.category_build.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_category_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_fire_category', i18n=i18n))
    await callback.answer('')


@fire_category_router.callback_query(F.data == 'category_room')
async def category_room_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.category_room.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_category_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_fire_category', i18n=i18n))
    await callback.answer('')


@fire_category_router.callback_query(F.data == 'category_outdoor_installation')
async def category_outdoor_installation_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.category_outdoor_installation.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_category_out_inst.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_fire_category', i18n=i18n))
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
#         reply_markup=get_inline_cd_kb(1, 'category_build', 'category_room', 'category_outdoor_installation', 'general_menu', i18n=i18n))
#     await callback.answer('')
