import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.types.input_file import BufferedInputFile
from fluentogram import TranslatorRunner


logger = logging.getLogger(__name__)

admin_router = Router()
