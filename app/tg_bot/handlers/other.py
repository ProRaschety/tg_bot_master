import logging
from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb

log = logging.getLogger(__name__)

other_router = Router()


@other_router.message(StateFilter(default_state))
async def echo_send(message: Message, state: FSMContext, i18n: TranslatorRunner):

    await message.answer(text=i18n.other_update.text(),
                         reply_markup=get_inline_url_kb(1, i18n=i18n, link_1="link_1-text"))
    log.info(
        f"Сборщик сообщений: id={message.from_user.id}, name={message.from_user.first_name}, text={message.text}")
    await message.delete()
