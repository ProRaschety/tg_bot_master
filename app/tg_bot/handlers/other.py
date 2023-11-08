import logging
from aiogram import Router
from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb

logger = logging.getLogger(__name__)

other_router = Router()


@other_router.message()
async def echo_send(message: Message, i18n: TranslatorRunner):

    await message.answer(text=i18n.other_update.text(),
                         reply_markup=get_inline_url_kb(1, i18n=i18n, link_1="link_1-text"))
    print(message.from_user.id, message.from_user.first_name, message.text)
    await message.delete()
