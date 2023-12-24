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
    file_pic = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await callback_data.message.answer_photo(
        photo=BufferedInputFile(
            file=file_pic, filename="pic_filling.png"),
        caption=text,
        has_spoiler=False,
        reply_markup=get_inline_cd_kb(1, 'category_build', 'category_room', 'category_outdoor_installation', 'general_menu', i18n=i18n))

    await callback_data.answer('')
    await callback_data.message.delete()
