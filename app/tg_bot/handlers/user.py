import logging
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from app.tg_bot.utilities.getting_data_base import quantity_keys_get

logger = logging.getLogger(__name__)

user_router = Router()


@user_router.message(CommandStart())
# async def process_start_command(
#     message: Message,
#     state: FSMContext,
#     i18n: TranslatorRunner
# ) -> None:
#
#     if not (username := message.from_user.full_name):
#         username = message.from_user.username
#     await message.answer(text=i18n.start.hello(username=username))
#     await message.answer(text=i18n.hello(), reply_markup=get_inline_kb(2, 'one-btn', 'two-btn', i18n=i18n))
async def process_start_command(message: Message, state: FSMContext, i18n: TranslatorRunner) -> None:
    await message.answer(text=i18n.start.menu(), reply_markup=get_inline_cd_kb(1,
                                                                               'calculators',
                                                                                'fire_resistance',
                                                                                'fire_pool',
                                                                                'fire_flash',
                                                                                'cloud_explosion',
                                                                                'horizontal_jet',
                                                                                'vertical_jet',
                                                                                'fire_ball',
                                                                                'bleve',
                                                                                i18n=i18n))


@user_router.message(Command(commands=["contacts"]))
async def process_get_admin_contacts(message: Message, i18n: TranslatorRunner) -> None:
    await message.answer(text=i18n.contacts.admin(),
                         reply_markup=get_inline_url_kb(1, i18n=i18n, link_1="link_1-text"))


@user_router.message(Command(commands=["data_base"]))
async def process_get_data_base(message: Message, i18n: TranslatorRunner) -> None:
    quantity_keys = quantity_keys_get()
    await message.answer(text=i18n.data_base(quantity_keys=quantity_keys),
                         reply_markup=get_inline_cd_kb(1,
                                                       'one_nine',
                                                       'EN_alphabet',
                                                       'alfa_omega',
                                                       'RUS_alphabet',
                                                       'general_menu',
                                                       i18n=i18n))


@user_router.callback_query(F.data == 'general_menu')
async def general_menu_call(callback_data: CallbackQuery, i18n: TranslatorRunner) -> None:
    await callback_data.message.answer(text=i18n.general_menu.text(),
                                       reply_markup=get_inline_cd_kb(1,
                                                                     'calculators',
                                                                     'fire_resistance',
                                                                     'fire_pool',
                                                                     'fire_flash',
                                                                     'cloud_explosion',
                                                                     'horizontal_jet',
                                                                     'vertical_jet',
                                                                     'fire_ball',
                                                                     'bleve',
                                                                     i18n=i18n))
