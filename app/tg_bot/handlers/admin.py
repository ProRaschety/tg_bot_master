import logging
import json

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State
from aiogram.types import CallbackQuery, Message, FSInputFile, PhotoSize, BufferedInputFile, InputMediaPhoto

from fluentogram import TranslatorRunner

from app.tg_bot.filters.filter_role import IsAdmin
from app.tg_bot.utilities.check_sub_admin import check_sub_admin
from app.tg_bot.states.fsm_state_data import FSMAdminForm
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb
from app.tg_bot.utilities.misc_utils import get_picture_filling
from app.tg_bot.models.role import UserRole

logger = logging.getLogger(__name__)

admin_router = Router()
admin_router.message.filter(IsAdmin())
admin_router.callback_query.filter(IsAdmin())


@admin_router.callback_query(F.data == 'admin_panel')
async def admin_panel_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    text = i18n.admin_panel()
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'steel_task',
                                      'wood_task',
                                      'concrete_task', i18n=i18n))
    await state.set_state(state=None)


@admin_router.callback_query(F.data == 'steel_task', StateFilter(default_state))
async def process_photo_file_id_admin(callback_data: CallbackQuery, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = 'Отправьте картинку для задачи с типом материала Сталь'
    await callback_data.answer(text=text)
    await state.set_state(FSMAdminForm.admin_set_pic_steel)


@admin_router.message(StateFilter(FSMAdminForm.admin_set_pic_steel), F.photo[-1].as_('largest_photo'))
async def get_photo_file_id_admin(message: Message, state: FSMContext, largest_photo: PhotoSize, i18n: TranslatorRunner) -> None:
    photo_id = largest_photo.file_id
    print(photo_id)
    with open(file='app/infrastructure/database/db_task_photo.json', mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        db_steel_photo_in["fire_resistance"]["steel_photo_id"] = steel_photo_id

    with open(file='app/infrastructure/database/db_task_photo.json', mode="w", encoding='utf-8') as file_w:
        json.dump(db_steel_photo_in, file_w, ensure_ascii=False, indent=4)

    text = 'Картинка получена'
    await message.answer(text=text)
    await state.clear()
