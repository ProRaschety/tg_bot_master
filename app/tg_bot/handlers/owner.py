import logging
# import json

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import CallbackQuery, Message, FSInputFile, PhotoSize, BufferedInputFile, InputMediaPhoto

from fluentogram import TranslatorRunner

from app.infrastructure.database.database.db import DB
from app.infrastructure.database.models.users import UsersModel
from app.tg_bot.filters.filter_role import IsOwner
# from app.tg_bot.utilities.check_sub_admin import check_sub_admin
# from app.tg_bot.states.fsm_state_data import FSMAdminForm
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb  # , get_inline_url_kb
from app.tg_bot.utilities.misc_utils import get_picture_filling
from app.tg_bot.models.role import UserRole


log = logging.getLogger(__name__)

owner_router = Router()
owner_router.message.filter(IsOwner())
owner_router.callback_query.filter(IsOwner())


class FSMOwnerForm(StatesGroup):
    promocode_state = State()


@owner_router.callback_query(F.data == 'owner_panel')
async def owner_panel_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    text = i18n.owner_panel()
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'get_users', 'get_promocode', 'set_promocode', 'clear_promocodes', i18n=i18n))
    await state.set_state(state=None)


@owner_router.callback_query(F.data == 'get_users')
async def get_users_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole, db: DB) -> None:
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    user_record: UsersModel = await db.users.get_user_record(user_id=callback.message.chat.id)
    text = i18n.owner_panel.text(id=user_record.user_id, created=user_record.created,
                                 role=str(user_record.role), promocode=str(user_record.promocode))
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'get_promocode', 'set_promocode', 'clear_promocodes', 'owner_panel', i18n=i18n))
    await state.set_state(state=None)


@owner_router.callback_query(F.data == 'clear_promocodes')
async def clear_promocodes_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole, db: DB) -> None:
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await db.promocode.delete()
    text = i18n.clear_promocodes.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'get_promocode', 'set_promocode', 'owner_panel', i18n=i18n))
    await state.set_state(state=None)


@owner_router.callback_query(F.data == 'set_promocode')
async def set_promocode_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole, db: DB) -> None:
    message_id = callback.message.message_id
    await state.update_data(mes_promo_owner_id=message_id)
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    text = i18n.set_promocode.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'cansel_enter_promo', i18n=i18n))
    await state.set_state(state=FSMOwnerForm.promocode_state)


@owner_router.message(StateFilter(FSMOwnerForm.promocode_state))
async def promo_code_input(message: Message, bot: Bot, state: FSMContext, i18n: TranslatorRunner, db: DB) -> None:
    data = await state.get_data()
    message_id = data.get('mes_promo_owner_id')
    promocode = message.text
    text = i18n.add_promocode.text(promocode=promocode)
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await db.promocode.add_promocode(promocode=promocode)
    await state.set_state(state=None)
    await message.delete()
    await bot.edit_message_media(
        chat_id=message.chat.id,
        message_id=message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'get_promocode', 'clear_promocodes', 'owner_panel', i18n=i18n))
