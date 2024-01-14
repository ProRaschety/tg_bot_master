import logging
import json

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State
from aiogram.types import CallbackQuery, Message, FSInputFile, PhotoSize, BufferedInputFile, InputMediaPhoto

from fluentogram import TranslatorRunner

from app.tg_bot.filters.filter_role import IsOwner
from app.tg_bot.utilities.check_sub_admin import check_sub_admin
from app.tg_bot.states.fsm_state_data import FSMAdminForm
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb
from app.tg_bot.utilities.misc_utils import get_picture_filling
from app.tg_bot.models.role import UserRole


logger = logging.getLogger(__name__)

owner_router = Router()
owner_router.message.filter(IsOwner())
owner_router.callback_query.filter(IsOwner())
