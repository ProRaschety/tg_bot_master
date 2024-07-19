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

from app.tg_bot.utilities import tables
from app.tg_bot.utilities.misc_utils import get_data_table, get_plot_graph, get_dataframe_table
from app.tg_bot.utilities.misc_utils import compute_value_with_eval, check_string, count_decimal_digits, count_zeros_after_decimal, count_zeros_and_digits, result_formatting, count_digits_before_dot, custom_round
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_keypad, get_inline_keyboard

from app.infrastructure.database.models.calculations import AccidentModel

from pprint import pprint

log = logging.getLogger(__name__)

keypad_router = Router()
keypad_router.message.filter(IsSubscriber())
keypad_router.callback_query.filter(IsSubscriber())

keypad_filter = [FSMEditForm.keypad_state]


@keypad_router.callback_query(StateFilter(*keypad_filter), F.data.in_([
    'all_clean', 'clean', 'open_parenthesis', 'closing_parenthesis',
    'one', 'two', 'three', 'pow', 'pow_square',
    'four', 'five', 'six', 'divide', 'multiply',
    'seven', 'eight', 'nine', 'minus', 'plus',
    'zero', 'point', 'dooble_zero', 'square_root', 'equals'
]))
async def editable_parameter_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner,) -> None:
    """Хендлер-калькулятор.
    Хендлер работает только в состоянии keypad_state и присваивает значение в требуемый ключ словаря.
    Функция eval() будет использоваться для получения значения по введенному выражению"""
    log.info(f'Request keypad handler from: {callback.data} ')
    # log.info(f'Keypad handler: {callback} ')
    user_state = await state.get_state()
    pprint(f'editable_parameter_call: {user_state.lower()}')
    context_data = await state.get_data()

    if callback.data == 'equals':
        edit_d = await state.get_data()
        editable_parameter = edit_d.get('editable_parameter', '')

        result = round(compute_value_with_eval(
            expression=editable_parameter), 15)

        check_str = check_string(editable_parameter)

        edit_param_formatting = result_formatting(
            input_string=editable_parameter, formatting=check_str, result=result)

        equals_result = result_formatting(formatting=True, result=result)

        # equals_result = "{:.2e}".format(result) if result < 0.001 else (            "{:.4f}".format(result) if result > 0.01 else "{:.2f}".format(result))
        # editable_parameter = "{:,.3e}".format(editable_param) if result < -100 else ("{:,.3e}".format(editable_param) if result > 10000 else "{:.3f}".format(editable_param))

        text = i18n.editable_parameter_st.text(
            text=edit_param_formatting, input_string=edit_param_formatting, value=equals_result)
        await bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            caption=text,
            reply_markup=get_keypad(i18n=i18n, param_back=True, back_data='general_menu'
                                    ), request_timeout=1
        )

        text = i18n.editable_parameter_nd.text(
            text=edit_param_formatting, input_string=edit_param_formatting, value=equals_result)
        await bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            caption=text,
            reply_markup=get_keypad(i18n=i18n, param_back=True, back_data='general_menu'
                                    ), request_timeout=1
        )

        count = count_decimal_digits(number=result)
        count_digits = count_digits_before_dot(number=result)
        count_zero, count_to_next_zero = count_zeros_and_digits(number=result)
        rou_int = 2 if count_digits >= 2 else count_zero + 1
        adj_result = round(result, rou_int)

        print(f'Проверка значимых чисел после запятой: {count}')
        print(f'Количество цифр до запятой: {count_digits}')
        print(f'Количество 0 после запятой: {count_zero}')
        print(f'Количество цифр после 0: {count_to_next_zero}')
        print(
            f'result: {result}, adj_result: {adj_result}, rou_int: {rou_int}')

        await state.update_data(editable_parameter=str(adj_result))

    elif callback.data == 'clean':
        editable_parameter = context_data.get('editable_parameter', '')
        if len(editable_parameter) > 0:
            # исключаем последний символ
            new_editable_parameter = editable_parameter[:-1]
            form_result = ''
            text = i18n.editable_parameter_st.text(
                text=editable_parameter, input_string=editable_parameter, value=form_result)
            await bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                caption=text,
                reply_markup=get_keypad(i18n=i18n, param_back=True, back_data='general_menu'
                                        ), request_timeout=1
            )
            await state.update_data(editable_parameter=new_editable_parameter
                                    )

        else:
            # await state.update_data(editable_parameter="")
            context_data = await state.get_data()
            editable_parameter = context_data.get('editable_parameter', '')
            form_result = ''
            text = i18n.editable_parameter_nd.text(
                text=editable_parameter, input_string=editable_parameter, value=form_result)
            await bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                caption=text,
                reply_markup=get_keypad(i18n=i18n, param_back=True, back_data='general_menu'
                                        ), request_timeout=1
            )
            await state.update_data(editable_parameter="")

            form_result = ''
            text = i18n.editable_parameter_rd.text(
                text=editable_parameter, input_string=editable_parameter, value=form_result)
            await bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                caption=text,
                reply_markup=get_keypad(i18n=i18n, param_back=True, back_data='general_menu'
                                        ), request_timeout=1
            )

    elif callback.data == 'all_clean':
        await state.update_data(editable_parameter="")
        edit_d = await state.get_data()
        editable_parameter = edit_d.get('editable_parameter', '')
        form_result = ''
        text = i18n.editable_parameter_st.text(
            text=editable_parameter, input_string=editable_parameter, value=form_result)
        await bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            caption=text,
            reply_markup=get_keypad(i18n=i18n, param_back=True, back_data='general_menu'
                                    ), request_timeout=1
        )
        form_result = ''
        text = i18n.editable_parameter_th.text(
            text=editable_parameter, input_string=editable_parameter, value=form_result)
        await bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            caption=text,
            reply_markup=get_keypad(i18n=i18n, param_back=True, back_data='general_menu'
                                    ), request_timeout=1
        )

    else:
        context_data = await state.get_data()
        edit_param_1 = context_data.get('editable_parameter', '')
        edit_sum = edit_param_1 + i18n.get(callback.data)
        await state.update_data(editable_parameter=edit_sum)
        context_data = await state.get_data()
        editable_parameter = context_data.get('editable_parameter', '')
        form_result = ''
        text = i18n.editable_parameter_th.text(
            text=editable_parameter, input_string=editable_parameter, value=form_result)
        await bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            caption=text,
            reply_markup=get_keypad(i18n=i18n, param_back=True, back_data='general_menu'
                                    ), request_timeout=1
        )
        await callback.answer('')


@keypad_router.callback_query(StateFilter(*keypad_filter), F.data.in_(['ready']))
async def ready_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner,) -> None:
    log.info(f'Request keypad handler from: {callback.data} ')

    context_data = await state.get_data()
    value = context_data.get('editable_parameter')

    result = compute_value_with_eval(expression=value)
    adj_result = custom_round(number=result)
    equals_result = result_formatting(formatting=True, result=adj_result)

    # user_state = await state.get_state()
    # if user_state == FSMEditForm.keypad_state:
    #     log.info(f'FSMState: {FSMEditForm.keypad_state} ')
    #     await state.update_data()

    # else:
    #     log.info(f'FSMState: unknown')

    # if value != '' and value != '.' and (float(value)) > 0:
    #     await state.update_data()
    # else:
    #     await state.update_data(accmodel.update(pool_area=10))

    # media = get_picture_filling(i18n.get('path_start'))
    # form_result = "{:,.2e}".format(result) if result < -100 else (
    #     "{:,.2e}".format(result) if result > 10000 else "{:,.2f}".format(result))
    # text = f'INPUT: {form_result}'
    text = 'Готово'
    # kb = {
    #     'width': '4',
    #     'buttons': 'edit_fire_flash_kb',
    #     'penult_button': 'run_fire_flash',
    #     'back_data': 'back_fire_flash'
    # }
    accmodel = AccidentModel(**context_data.get('accident_model'))
    dataframe = tables.get_dataframe(
        request='fire_flash', i18n=i18n, accmodel=accmodel)
    media = get_dataframe_table(data=dataframe)

    kb = context_data['keyboard_section']
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename='pic_filling'), caption=text),
        reply_markup=get_inline_cd_kb(
            int(kb['width']),
            *i18n.get(kb['buttons']).split('\n'),
            i18n=i18n,
            penult_button=kb['penult_button'],
            back_data='general_menu'
        ),
    )

    # await bot.edit_message_media(
    #     chat_id=callback.message.chat.id,
    #     message_id=callback.message.message_id,
    #     media=InputMediaPhoto(media=BufferedInputFile(
    #         file=media, filename='pic_filling'), caption=text),
    #     reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_typical_accidents'
    #                                   )
    # )

    await state.update_data(editable_parameter='')
    await state.set_state(state=None)
