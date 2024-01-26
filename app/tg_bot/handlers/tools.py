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


tools_router = Router()
