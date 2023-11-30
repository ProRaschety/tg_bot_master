import logging

from aiogram import Router, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import CallbackQuery, Message

from fluentogram import TranslatorRunner

from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb


logger = logging.getLogger(__name__)

user_router = Router()


@user_router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext, i18n: TranslatorRunner) -> None:
    await message.answer(text=i18n.start.menu(), reply_markup=get_inline_cd_kb(1,
                                                                               'calculators',
                                                                               'fire_resistance',
                                                                               'fire_risks',
                                                                               i18n=i18n))
    await state.clear()


@user_router.message(Command(commands=["cansel"]), StateFilter(default_state))
async def process_cancel_command(message: Message, i18n: TranslatorRunner) -> None:

    await message.answer(text=i18n.cansel.input())


@user_router.message(Command(commands=["cansel"]), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, i18n: TranslatorRunner, state: FSMContext) -> None:

    await message.answer(text=i18n.cansel.state())
    await state.clear()
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
async def general_menu_call(callback_data: CallbackQuery, state: FSMContext, i18n: TranslatorRunner) -> None:
    await callback_data.message.answer(text=i18n.general_menu.text(),
                                       reply_markup=get_inline_cd_kb(1,
                                                                     'calculators',
                                                                     'fire_resistance',
                                                                     'fire_risks',
                                                                     i18n=i18n))
    await callback_data.answer('')
    await callback_data.message.delete()
