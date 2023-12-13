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
from app.tg_bot.utilities.misc_utils import get_temp_folder, get_csv_file, get_csv_bt_file
from app.tg_bot.states.fsm_state_data import FSMSteelForm
from app.calculation.fire_resistance.steel_calculation import SteelFR, SteelStrength


logger = logging.getLogger(__name__)
logger = logging.getLogger('matplotlib').setLevel(logging.ERROR)
logger = logging.getLogger('PIL.PngImagePlugin').setLevel(logging.ERROR)


fire_category_router = Router()


@fire_category_router.callback_query(F.data == 'fire_category')
async def fire_category_call(callback_data: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    await callback_data.message.bot.send_chat_action(
        chat_id=callback_data.message.chat.id,
        action=ChatAction.TYPING)

    text = i18n.fire_category.text()
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        steel_photo_id = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    await callback_data.message.answer_photo(
        photo=steel_photo_id,
        caption=text,
        has_spoiler=False,
        reply_markup=get_inline_cd_kb(1, 'category_build', 'category_room', 'category_outdoor_installation', 'general_menu', i18n=i18n))

    await callback_data.answer('')
    await callback_data.message.delete()
