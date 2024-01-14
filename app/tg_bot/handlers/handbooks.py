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
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb, get_inline_sub_kb, SubCallbackFactory
from app.tg_bot.utilities.misc_utils import get_temp_folder, get_picture_filling
from app.tg_bot.states.fsm_state_data import FSMSubstanceForm
from app.calculation.database_mode.substance import SubstanceDB

log = logging.getLogger(__name__)
# logger = logging.getLogger(__name__)
# logger = logging.getLogger('matplotlib').setLevel(logging.ERROR)
# logger = logging.getLogger('PIL.PngImagePlugin').setLevel(logging.ERROR)


handbooks_router = Router()

HANDBOOKS_KB = ['substances', 'typical_flammable_load',
                'climate', 'frequencys', 'statistics', 'general_menu']


@handbooks_router.callback_query(F.data.in_(['handbooks', 'back_to_handbooks']), StateFilter(default_state))
async def handbooks_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    log.info('Запрос: Справочники')
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    text = i18n.handbooks.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, *HANDBOOKS_KB, i18n=i18n))


@handbooks_router.callback_query(F.data.in_(["climate"]), StateFilter(default_state))
async def climate_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, db: DB) -> None:
    log.info('Запрос: Справочник метеоданных')
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    text = i18n.climate.text()
    data = await db.climate.get_climate_record(user_id=callback.message.chat.id)
    log.info(f'Данные из Справочника метеоданных: {data}')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_to_handbooks', i18n=i18n))
