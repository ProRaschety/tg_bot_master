import logging

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import CallbackQuery, Message, BufferedInputFile, InputMediaPhoto

from fluentogram import TranslatorRunner

from app.infrastructure.database.database.db import DB
from app.tg_bot.utilities.check_sub_admin import check_sub_admin
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb
from app.tg_bot.utilities.misc_utils import get_picture_filling


log = logging.getLogger(__name__)

user_router = Router()


@user_router.message(CommandStart())
async def process_start_command(message: Message, bot: Bot, state: FSMContext, i18n: TranslatorRunner, db: DB) -> None:
    user_id = message.chat.id
    if await check_sub_admin(bot=bot, user_id=user_id):
        await db.users.add(user_id=user_id, language=message.from_user.language_code, is_admin=True)
    else:
        await db.users.add(user_id=user_id, language=message.from_user.language_code)

    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    text = i18n.start.menu()
    await message.answer_photo(
        photo=BufferedInputFile(file=media, filename="pic_filling.png"),
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      # 'calculators',
                                      'fire_resistance',
                                      'fire_risks',
                                      'fire_category',
                                      i18n=i18n))
    await state.set_state(state=None)


@user_router.message(Command(commands=["cansel"]), StateFilter(default_state))
async def process_cancel_command(message: Message, i18n: TranslatorRunner) -> None:

    await message.answer(text=i18n.cansel.input())


@user_router.message(Command(commands=["cansel"]), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, i18n: TranslatorRunner, state: FSMContext) -> None:

    await message.answer(text=i18n.cansel.state())
    await state.set_state(state=None)
    await message.delete()


@user_router.message(Command(commands=["contacts"]))
async def process_get_admin_contacts(message: Message, i18n: TranslatorRunner) -> None:

    await message.answer(text=i18n.contacts.admin(),
                         reply_markup=get_inline_url_kb(1, i18n=i18n, link_1="link_1-text"))


@user_router.message(Command(commands=["help"]))
async def process_get_admin_contacts(message: Message, i18n: TranslatorRunner) -> None:
    await message.answer(text=i18n.contacts.admin(),
                         reply_markup=get_inline_url_kb(1, i18n=i18n, link_1="link_1-text"))


@user_router.message(Command(commands=["bot_wiki"]))
async def process_get_admin_contacts(message: Message, i18n: TranslatorRunner) -> None:
    await message.answer(text=i18n.contacts.admin(),
                         reply_markup=get_inline_url_kb(1, i18n=i18n, link_1="link_1-text"))


@user_router.callback_query(F.data == 'general_menu')
async def general_menu_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    text = i18n.general_menu.text()

    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      #  'calculators',
                                      'fire_resistance',
                                      'fire_risks',
                                      'fire_category',
                                      i18n=i18n))
    await state.set_state(state=None)
    await callback_data.answer('')
