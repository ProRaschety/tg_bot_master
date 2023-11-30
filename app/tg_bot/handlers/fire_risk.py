import logging

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import CallbackQuery, Message, FSInputFile, InputMediaPhoto, InputFile
from aiogram.utils.chat_action import ChatActionSender
from aiogram.enums import ChatAction

from fluentogram import TranslatorRunner

from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb

import json

logger = logging.getLogger(__name__)

fire_risk_router = Router()


@fire_risk_router.callback_query(F.data == 'fire_risks')
async def fire_risks_call(callback_data: CallbackQuery, i18n: TranslatorRunner) -> None:
    await callback_data.message.bot.send_chat_action(
        chat_id=callback_data.message.chat.id,
        action=ChatAction.UPLOAD_PHOTO)

    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        steel_photo_id = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    text = i18n.fire_risks.text()

    await callback_data.message.answer_photo(
        photo=steel_photo_id,
        caption=text,
        has_spoiler=False,
        reply_markup=get_inline_cd_kb(1, 'fire_risks_calculator', 'typical_accidents', 'general_menu', i18n=i18n))

    await callback_data.answer('')


@fire_risk_router.callback_query(F.data == 'back_fire_risks')
async def back_fire_risks_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:

    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        media = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    text = i18n.fire_risks.text()

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'fire_risks_calculator',
                                      'typical_accidents',
                                      'general_menu', i18n=i18n))

    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'back_typical_accidents')
async def back_typical_accidents_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:

    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        media = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    text = i18n.fire_risks.text()

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
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
async def typical_accidents_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:

    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        media = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    text = i18n.fire_risks.text()

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
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


@fire_risk_router.callback_query(F.data == 'fire_risks_calculator')
async def fire_pool_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.fire_risks_calculator.text()
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        media = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_fire_risks', i18n=i18n))

    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'fire_pool')
async def fire_pool_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.fire_pool.text()
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        media = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_fire_risks', 'general_menu', i18n=i18n))

    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'fire_flash')
async def fire_flash_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.fire_flash.text()
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        media = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_fire_risks', 'general_menu', i18n=i18n))

    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'cloud_explosion')
async def cloud_explosion_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.cloud_explosion.text()
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        media = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_fire_risks', 'general_menu', i18n=i18n))

    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'horizontal_jet')
async def horizontal_jet_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.horizontal_jet.text()
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        media = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_fire_risks', 'general_menu', i18n=i18n))

    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'vertical_jet')
async def vertical_jet_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.vertical_jet.text()
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        media = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_fire_risks', 'general_menu', i18n=i18n))

    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'fire_ball')
async def fire_ball_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.fire_ball.text()
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        media = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_fire_risks', 'general_menu', i18n=i18n))

    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'bleve')
async def bleve_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.bleve.text()
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        media = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_fire_risks', 'general_menu', i18n=i18n))

    await callback.answer('')
