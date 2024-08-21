import logging

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
# , InlineQueryResultArticle, InputTextMessageContent
# from aiogram.types import InlineQuery
from aiogram.types import CallbackQuery, Message, BufferedInputFile, InputMediaPhoto, InputMediaAnimation, InputMediaDocument, FSInputFile

from fluentogram import TranslatorRunner

# from app.infrastructure.database.database.db import DB
from app.calculation.utilities.misc_utils import update_number_picture

from app.tg_bot.models.role import UserRole
from app.tg_bot.filters.filter_role import IsGuest
from app.tg_bot.utilities.misc_utils import get_picture_filling
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb
from app.tg_bot.states.fsm_state_data import FSMOtherForm


log = logging.getLogger(__name__)

other_tools_router = Router()
other_tools_router.message.filter(IsGuest())
other_tools_router.callback_query.filter(IsGuest())

SFilterOther = [FSMOtherForm.accept_document_state]


@other_tools_router.callback_query(F.data.in_(['other_tools', 'back_other_tools']))
async def other_tools_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.set_state(state=None)
    text = i18n.fds_tools.text()
    # media = FSInputFile(r'temp_files/temp/fds_tools_logo.mp4')
    media = BufferedInputFile(
        file=get_picture_filling(file_path='temp_files/temp/logo_other_tools.png'), filename="pic_filling")

    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        # media=InputMediaAnimation(media=media, caption=text),
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('other_tools_kb').split('\n'),
                                      i18n=i18n, back_data='general_menu'
                                      )
    )


@other_tools_router.callback_query(F.data == 'update_number_pic')
async def update_number_picture_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback_data.message.chat.id)
    message_id = callback_data.message.message_id
    await state.update_data(chat_id=chat_id, update_number_picture_mes_id=message_id)
    text = i18n.update_number_picture.text()
    # media = get_picture_filling(file_path='temp_files/temp/fds_tools_dencity.png')
    media = BufferedInputFile(
        file=get_picture_filling(file_path='temp_files/temp/update_number_picture.png'), filename="pic_filling")

    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        # media=InputMediaAnimation(media=media, caption=text),
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(1, i18n=i18n, back_data='back_other_tools'))
    await state.set_state(FSMOtherForm.accept_document_state)


@other_tools_router.message(StateFilter(FSMOtherForm.accept_document_state))
async def input_update_number_picture_document(message: Message, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    update_number_pic = message.document.file_id
    await state.update_data(update_number_picture_doc=update_number_pic)
    await message.delete()
    data = await state.get_data()
    message_id = data.get('update_number_picture_mes_id')
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, i18n=i18n, param_back=True, back_data='back_other_tools'))

    path = rf"temp_files/temp_data/{str(message.chat.id) + '_update_number_picture'}.docx"
    await bot.download(file=update_number_pic, destination=path)
    text = i18n.request_stop.text()
    await bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, i18n=i18n, param_back=True, back_data='back_other_tools'))

    count = update_number_picture(
        doc_path=path, figure_first_count=1)

    # rf"temp_files/temp_data/{str(message.chat.id) + '_update_number_picture'}.docx"
    file_data = FSInputFile(rf"{path}", filename='update_number_picture.docx')

    text = i18n.update_number_picture_stop.text(count=count)
    await bot.edit_message_media(
        chat_id=message.chat.id,
        message_id=message_id,
        media=InputMediaDocument(media=file_data, caption=text),
        reply_markup=get_inline_cd_kb(1, i18n=i18n, param_back=True, back_data='back_other_tools'))

    await state.set_state(state=None)
