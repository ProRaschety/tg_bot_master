import logging

from dataclasses import asdict

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaPhoto

from fluentogram import TranslatorRunner

# from app.infrastructure.database.database.db import DB
from app.tg_bot.models.role import UserRole
from app.tg_bot.models.keyboard import InlineKeyboardModel

from app.tg_bot.filters.filter_role import IsGuest
from app.tg_bot.states.fsm_state_data import FSMEditForm
from app.tg_bot.utilities.tables import DataFrameBuilder
from app.tg_bot.utilities.misc_utils import get_dataframe_table, find_key_path, get_dict_value
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_keypad, get_inline_keyboard

from app.calculation.models.calculations import AccidentModel
# from app.infrastructure.database.models.substance import SubstanceModel


log = logging.getLogger(__name__)

fire_accident_fireflash_router = Router()
fire_accident_fireflash_router.message.filter(IsGuest())
fire_accident_fireflash_router.callback_query.filter(IsGuest())


@fire_accident_fireflash_router.callback_query(F.data.in_(['fire_flash', 'back_fire_flash']))
async def fire_flash_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_typical_accidents'
                                      )
    )

    context_data = await state.get_data()
    text = i18n.fire_flash.text()

    accident_model = AccidentModel(**context_data.get('accident_model'))
    dfb = DataFrameBuilder(i18n=i18n,  request='fire_flash',
                           model=accident_model)
    dataframe = dfb.action_request()

    media = get_dataframe_table(data=dataframe)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(
            1,
            *i18n.get('fire_flash_kb_guest').split('\n') if role in ['guest'] else i18n.get('fire_flash_kb').split('\n'),
            i18n=i18n, back_data='back_typical_accidents'
        )
    )
    await state.update_data(temporary_request='fire_flash')
    await callback.answer('')


@fire_accident_fireflash_router.callback_query(F.data == 'run_fire_flash')
async def run_fire_flash_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:

    text = i18n.calculation_progress.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_fire_flash'
                                      )
    )

    text = i18n.fire_flash.text()

    context_data = await state.get_data()

    accident_model = AccidentModel(**context_data.get('accident_model'))
    dfb = DataFrameBuilder(i18n=i18n,  request='run_fire_flash',
                           model=accident_model)
    dataframe = dfb.action_request()
    media = get_dataframe_table(data=dataframe, results=True, row_num=7)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_fire_flash'
                                      )
    )
    await callback.answer('')


@fire_accident_fireflash_router.callback_query(F.data.in_(['edit_fire_flash_guest']))
async def edit_fire_flash_guest_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.get('initial_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(
            1,
            *i18n.get('fire_flash_kb_guest').split('\n'),
            i18n=i18n, param_back=True, back_data='back_fire_flash'
        )
    )

    text = i18n.get('repeated_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(
            1,
            *i18n.get('fire_flash_kb_guest').split('\n'),
            i18n=i18n, param_back=True, back_data='back_fire_flash'
        )
    )
    await callback.answer('')


@fire_accident_fireflash_router.callback_query(F.data.in_(['edit_fire_flash']))
async def edit_fire_flash_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)

    context_data = await state.get_data()

    kb = InlineKeyboardModel(
        width=4, buttons='edit_fire_flash_kb', penultimate='run_fire_flash', ultimate='back_fire_flash', reference=None)

    context_data['keyboard_model'] = asdict(kb)

    text = ''
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_keyboard(keyboard=kb, i18n=i18n,
                                         )
    )
    await state.update_data(context_data)
    await callback.answer('')


@fire_accident_fireflash_router.callback_query(F.data.in_(['mass_vapor_fuel', 'lower_flammability_limit']))
async def edit_flash_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    context_data = await state.get_data()

    path_edited_parameter = find_key_path(
        dictionary=context_data, key=callback.data)

    editable_parameter = get_dict_value(
        dictionary=context_data, keys_list=path_edited_parameter)

    text = i18n.temporary_parameter.text(
        text=i18n.get('name_' + callback.data), value=editable_parameter)

    kb = InlineKeyboardModel(
        width=4, buttons='edit_fire_flash_kb', penultimate='run_fire_flash', ultimate='back_fire_flash')

    context_data['keyboard_model'] = asdict(kb)
    context_data['temporary_text'] = callback.data
    context_data['path_edited_parameter'] = path_edited_parameter

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_keypad(
            i18n=i18n, penult_button='ready'
        )
    )

    await state.update_data(context_data)
    await state.set_state(FSMEditForm.keypad_state)
