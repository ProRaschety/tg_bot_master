import logging
import io
import ormsgpack
import json

from dataclasses import dataclass, asdict, astuple

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
# , InlineQueryResultArticle, InputTextMessageContent
# from aiogram.types import InlineQuery
from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaPhoto

from fluentogram import TranslatorRunner

# from app.infrastructure.database.database.db import DB
from app.tg_bot.models.tables import DataFrameModel
from app.tg_bot.models.role import UserRole
from app.tg_bot.filters.filter_role import IsGuest, IsSubscriber
from app.tg_bot.states.fsm_state_data import FSMFireAccidentForm, FSMEditForm

from app.tg_bot.utilities.misc_utils import get_picture_filling
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_keypad

from pprint import pprint

log = logging.getLogger(__name__)

keypad_router = Router()
keypad_router.message.filter(IsSubscriber())
keypad_router.callback_query.filter(IsSubscriber())

keypad_filter = []


@keypad_router.callback_query(StateFilter(FSMEditForm.keypad_state), F.data.in_(
    ['all_clean', 'clean', 'open_parenthesis', 'closing_parenthesis',
     'one', 'two', 'three', 'pow', 'pow_square',
     'four', 'five', 'six', 'divide', 'multiply',
     'seven', 'eight', 'nine', 'minus', 'plus',
     'zero', 'point', 'dooble_zero', 'equals',
     'ready']))
async def editable_parameter_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner,) -> None:
    """Хендлер-калькулятор.
    Хендлер работает только в состоянии keypad_state и присваивает значение в требуемый ключ словаря.
    Функция eval() будет использоваться для получения значения по введенному выражению"""
    log.info(f'Request keypad handler from: {callback.data} ')
    # log.info(f'Keypad handler: {callback} ')
    # pprint(callback, width=4)
    user_state = await state.get_state()
    print(type(user_state))
    context_data = await state.get_data()

    required_key = context_data.get('editable_parameter')

    if callback.data == 'ready':
        value = context_data.get('editable_parameter')
        log.info(f'value in ready: {value}')
        # if value != '' and value != '.' and (float(value)) > 0:
        #     await state.update_data()
        # else:
        #     await state.update_data(accmodel.update(pool_area=10))

        # ready_value = context_data.get(required_key)
        editable_parameter = context_data.get('editable_parameter', '')

        media = get_picture_filling(i18n.get('path_start'))
        text = i18n.fire_pool.text()
        await bot.edit_message_media(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            media=InputMediaPhoto(media=BufferedInputFile(
                file=media, filename='pic_filling'), caption=text),
            reply_markup=get_inline_cd_kb(
                i18n=i18n, param_back=True, back_data='general_menu'
            )
        )
        await state.update_data(editable_parameter='')
        await state.set_state(state=None)

    elif callback.data == 'clean':
        editable_parameter = context_data.get('editable_parameter', '')
        # print(f'clean (data): {editable_parameter}')
        if len(editable_parameter) > 0:
            # исключаем последний символ
            new_editable_parameter = editable_parameter[:-1]
            # print(new_editable_parameter)
            text = i18n.editable_parameter.text(
                text='Введите необходимое значение', value=new_editable_parameter)
            await bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                caption=text,
                reply_markup=get_keypad(i18n=i18n, penult_button='ready'
                                        )
            )
            await state.update_data(editable_parameter=new_editable_parameter
                                    )

        else:
            # print(len(editable_parameter))
            # await state.update_data(editable_parameter="")
            context_data = await state.get_data()
            editable_parameter = context_data.get('editable_parameter', '')
            # print(f'clean 0 (data): {editable_parameter}')
            text = i18n.editable_parameter.text(
                text='Введите необходимое значениЕ', value=editable_parameter)
            await bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                caption=text,
                reply_markup=get_keypad(i18n=i18n, penult_button='ready'
                                        )
            )
            await state.update_data(editable_parameter="")

            text = i18n.editable_parameter.text(
                text='Введите необходимое значение', value=editable_parameter)
            await bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                caption=text,
                reply_markup=get_keypad(i18n=i18n, penult_button='ready'
                                        )
            )

    elif callback.data == 'all_clean':
        await state.update_data(editable_parameter="")
        edit_d = await state.get_data()
        editable_parameter = edit_d.get('editable_parameter', '')
        text = i18n.editable_parameter.text(
            text='Введите необходимое значениЕ', value=editable_parameter)
        await bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            caption=text,
            reply_markup=get_keypad(i18n=i18n, penult_button='ready'
                                    )
        )
        text = i18n.editable_parameter.text(
            text='Введите необходимое значение', value=editable_parameter)
        await bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            caption=text,
            reply_markup=get_keypad(i18n=i18n, penult_button='ready'
                                    )
        )

    else:
        context_data = await state.get_data()
        edit_param_1 = context_data.get('editable_parameter', '')
        edit_sum = edit_param_1 + i18n.get(callback.data)
        await state.update_data(editable_parameter=edit_sum)
        context_data = await state.get_data()
        editable_parameter = context_data.get('editable_parameter', '')
        text = i18n.editable_parameter.text(
            text='Введите необходимое значение', value=editable_parameter
        )
        await bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            caption=text,
            reply_markup=get_keypad(i18n=i18n, penult_button='ready'
                                    )
        )


# @keypad_router.callback_query(F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'dooble_zero', 'point', 'clean']))
# async def editable_parameter_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
#     user_state = await state.get_state()
#     if user_state == FSMFireAccidentForm.edit_fire_pool_area_state:
#         fire_pool_param = i18n.get("name_fire_pool_area")
#     elif user_state == FSMFireAccidentForm.edit_fire_pool_distance_state:
#         fire_pool_param = i18n.get("name_fire_pool_distance")
#     elif user_state == FSMFireAccidentForm.edit_fire_pool_wind_state:
#         fire_pool_param = i18n.get("name_fire_pool_wind")

#     edit_data = await state.get_data()

#     if callback.data == 'clean':
#         editable_parameter = edit_data.get('editable_parameter', '')
#         if len(editable_parameter) > 0:
#             # исключаем последний символ
#             new_editable_parameter = editable_parameter[:-1]
#             text = i18n.editable_parameter.text(
#                 text=fire_pool_param, value=new_editable_parameter)
#         else:
#             text = i18n.editable_parameter.text(
#                 text=fire_pool_param, value=editable_parameter)

#     elif callback.data == 'all_clean':
#         await state.update_data(editable_parameter="")
#         edit_d = await state.get_data()
#         editable_parameter = edit_d.get('editable_parameter', '')
#         text = i18n.editable_parameter.text(
#             text=fire_pool_param, value=editable_parameter)

#     else:
#         edit_param_1 = edit_data.get('editable_parameter', '')
#         edit_sum = edit_param_1 + i18n.get(callback.data)
#         await state.update_data(editable_parameter=edit_sum)
#         edit_data = await state.get_data()
#         editable_parameter = edit_data.get('editable_parameter', '')
#         text = i18n.editable_parameter.text(
#             text=fire_pool_param, value=editable_parameter
#         )

#     await bot.edit_message_caption(
#         chat_id=callback.message.chat.id,
#         message_id=callback.message.message_id,
#         caption=text,
#         reply_markup=get_inline_cd_kb(
#             3,
#             *i18n.get('calculator_buttons').split('\n'),
#             i18n=i18n
#         )
#     )


# @keypad_router.callback_query(F.data.in_(['ready']))
# async def editable_parameter_ready(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
#     user_state = await state.get_state()
#     context_data = await state.get_data()
#     accmodel = context_data.get('fire_pool_model')

#     value = context_data.get("editable_parameter")

#     if user_state == FSMFireAccidentForm.edit_fire_pool_area_state:
#         if value != '' and value != '.' and (float(value)) > 0:
#             await state.update_data(accmodel.update(pool_area=value))
#         else:
#             await state.update_data(accmodel.update(pool_area=10))

#     elif user_state == FSMFireAccidentForm.edit_fire_pool_distance_state:
#         if value != '' and value != '.' and (float(value)) > 0:
#             await state.update_data(accmodel.update(distance=value))
#         else:
#             await state.update_data(accmodel.update(distance=10))

#     elif user_state == FSMFireAccidentForm.edit_fire_pool_wind_state:
#         if value != '' and value != '.' and (float(value)) > 0:
#             # await state.update_data(accident_fire_pool_wind=value)
#             await state.update_data(accmodel.update(velocity_wind=value))
#         else:
#             await state.update_data(accmodel.update(velocity_wind=0))

#     await state.update_data(context_data)
#     context_data = await state.get_data()

#     media = get_picture_filling(i18n.get('path_start'))
#     text = i18n.fire_pool.text()
#     await bot.edit_message_media(
#         chat_id=callback.message.chat.id,
#         message_id=callback.message.message_id,
#         media=InputMediaPhoto(media=BufferedInputFile(
#             file=media, filename="pic_filling"), caption=text),
#         reply_markup=get_inline_cd_kb(
#             4,
#             *i18n.get('edit_fire_pool_kb').split('\n'),
#             i18n=i18n
#         )
#     )

#     await state.update_data(editable_parameter='')
#     await state.set_state(state=None)
