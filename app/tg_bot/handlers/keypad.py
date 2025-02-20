import logging

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaPhoto

from fluentogram import TranslatorRunner

from app.tg_bot.models.keyboard import InlineKeyboardModel
from app.tg_bot.filters.filter_role import IsSubscriber
from app.tg_bot.states.fsm_state_data import FSMEditForm

from app.tg_bot.utilities.tables import DataFrameBuilder
from app.tg_bot.utilities.misc_utils import get_dataframe_table
from app.tg_bot.utilities.misc_utils import compute_value_with_eval, check_string, count_zeros_and_digits, result_formatting, count_digits_before_dot, custom_round, modify_dict_value
from app.tg_bot.keyboards.kb_builder import get_keypad, get_inline_keyboard

from app.calculation.models.calculations import AccidentModel, RoomModel, from_dict
from app.infrastructure.database.models.substance import FlammableMaterialModel, SubstanceModel


# from pprint import pprint

log = logging.getLogger(__name__)

keypad_router = Router()
keypad_router.message.filter(IsSubscriber())
keypad_router.callback_query.filter(IsSubscriber())


@keypad_router.callback_query(StateFilter(FSMEditForm.keypad_state), F.data.in_(['all_clean']))
async def all_clean_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner,) -> None:
    context_data = await state.get_data()
    # elif callback.data == 'all_clean':
    await state.update_data(temporary_parameter="")
    edit_d = await state.get_data()
    temporary_parameter = edit_d.get('temporary_parameter', '')

    form_result = ''
    text = i18n.temporary_parameter_st.text(
        text=i18n.get('name_' + context_data.get('temporary_text')), input_string=temporary_parameter, value=form_result)
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_keypad(i18n=i18n,
                                ), request_timeout=1
    )
    form_result = ''
    text = i18n.temporary_parameter_th.text(
        text=i18n.get('name_' + context_data.get('temporary_text')), input_string=temporary_parameter, value=form_result)
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_keypad(i18n=i18n,
                                ), request_timeout=1
    )


@keypad_router.callback_query(StateFilter(FSMEditForm.keypad_state), F.data.in_(['clean']))
async def clean_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner,) -> None:
    context_data = await state.get_data()
    temporary_parameter = context_data.get('temporary_parameter', '')
    if len(temporary_parameter) > 0:
        # исключаем последний символ
        new_temporary_parameter = temporary_parameter[:-1]
        form_result = ''
        text = i18n.temporary_parameter_st.text(
            text=i18n.get('name_' + context_data.get('temporary_text')), input_string=temporary_parameter, value=form_result)
        await bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            caption=text,
            reply_markup=get_keypad(i18n=i18n,
                                    ), request_timeout=1
        )
        await state.update_data(temporary_parameter=new_temporary_parameter
                                )

    else:
        # await state.update_data(temporary_parameter="")
        context_data = await state.get_data()
        temporary_parameter = context_data.get('temporary_parameter', '')
        form_result = ''
        text = i18n.temporary_parameter_nd.text(
            text=i18n.get('name_' + context_data.get('temporary_text')), input_string=temporary_parameter, value=form_result)
        await bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            caption=text,
            reply_markup=get_keypad(i18n=i18n,
                                    ), request_timeout=1
        )
        await state.update_data(temporary_parameter="")

        form_result = ''
        text = i18n.temporary_parameter_rd.text(
            text=i18n.get('name_' + context_data.get('temporary_text')), input_string=temporary_parameter, value=form_result)
        await bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            caption=text,
            reply_markup=get_keypad(i18n=i18n,
                                    ), request_timeout=1
        )


@keypad_router.callback_query(StateFilter(FSMEditForm.keypad_state), F.data.in_(['equals']))
async def equals_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner,) -> None:
    context_data = await state.get_data()
    # if callback.data == 'equals':
    edit_d = await state.get_data()
    temporary_parameter = edit_d.get('temporary_parameter', '')

    result = round(compute_value_with_eval(
        expression=temporary_parameter), 15)

    check_str = check_string(temporary_parameter)

    edit_param_formatting = result_formatting(
        input_string=temporary_parameter, formatting=check_str, result=result)

    equals_result = result_formatting(formatting=True, result=result)

    text = i18n.temporary_parameter_st.text(
        text=i18n.get('name_' + context_data.get('temporary_text')), input_string=edit_param_formatting, value=equals_result)
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_keypad(i18n=i18n,
                                ), request_timeout=1
    )

    text = i18n.temporary_parameter_nd.text(
        text=i18n.get('name_' + context_data.get('temporary_text')), input_string=edit_param_formatting, value=equals_result)
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_keypad(i18n=i18n,
                                ), request_timeout=1
    )

    # count = count_decimal_digits(number=result)
    count_digits = count_digits_before_dot(number=result)
    count_zero, count_to_next_zero = count_zeros_and_digits(number=result)
    rou_int = 2 if count_digits >= 2 else count_zero + 1
    adj_result = round(result, rou_int)

    # print(f'Проверка значимых чисел после запятой: {count}')
    # print(f'Количество цифр до запятой: {count_digits}')
    # print(f'Количество 0 после запятой: {count_zero}')
    # print(f'Количество цифр после 0: {count_to_next_zero}')
    # print(
    #     f'result: {result}, adj_result: {adj_result}, rou_int: {rou_int}')

    await state.update_data(temporary_parameter=str(adj_result))


@keypad_router.callback_query(StateFilter(FSMEditForm.keypad_state), F.data.in_([
    'open_parenthesis', 'closing_parenthesis',
    'one', 'two', 'three', 'pow', 'pow_square',
    'four', 'five', 'six', 'divide', 'multiply',
    'seven', 'eight', 'nine', 'minus', 'plus',
    'zero', 'point', 'dooble_zero', 'square_root',
]))
async def temporary_parameter_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner,) -> None:
    """Хендлер-калькулятор.
    Хендлер работает только в состоянии keypad_state и присваивает значение в требуемый ключ словаря.
    Функция eval() будет использоваться для получения значения по введенному выражению"""
    # log.info(f'Request keypad handler from: {callback.data} ')

    context_data = await state.get_data()
    edit_param_1 = context_data.get('temporary_parameter', '')
    edit_sum = edit_param_1 + i18n.get(callback.data)

    await state.update_data(temporary_parameter=edit_sum)
    context_data = await state.get_data()
    temporary_parameter = context_data.get('temporary_parameter', '')

    form_result = ''
    text = i18n.temporary_parameter_th.text(
        text=i18n.get('name_' + context_data.get('temporary_text')), input_string=temporary_parameter, value=form_result)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_keypad(i18n=i18n,
                                ), request_timeout=1
    )
    await callback.answer('')


@keypad_router.callback_query(StateFilter(FSMEditForm.keypad_state), F.data.in_(['ready']))
async def ready_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner,) -> None:
    context_data = await state.get_data()
    log.info(
        f"Request keypad handler: {context_data.get('temporary_request')}")
    kb = InlineKeyboardModel(**context_data['keyboard_model'])
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_keyboard(keyboard=kb, i18n=i18n,
                                         )
    )

    # pprint(context_data)
    value = context_data.get('temporary_parameter')

    result = compute_value_with_eval(expression=value)
    adj_result = custom_round(number=result)
    equals_result = result_formatting(formatting=True, result=adj_result)

    path_edited_parameter = context_data.get('path_edited_parameter')

    context_data_modify = modify_dict_value(
        dictionary=context_data, keys_list=path_edited_parameter, value=equals_result)

    await state.update_data(context_data_modify)
    context_data = await state.get_data()
    temporary_model = context_data.get('temporary_model')
    request = context_data.get('temporary_request')

    requests = {
        'fire_flash': AccidentModel,
        'fire_pool': AccidentModel,
        'cloud_explosion': AccidentModel,
        'fire_ball': AccidentModel,
        'accident_bleve': AccidentModel,
        'horizontal_jet': AccidentModel,
        'vertical_jet': AccidentModel,
        # 'category_premises': RoomModel,
        'standard_flammable_load': FlammableMaterialModel,
        'handbooks': SubstanceModel,
    }

    if request == 'category_premises':
        model = from_dict(data=context_data.get(temporary_model))
    else:
        model = requests[request](**context_data.get(temporary_model))

    dfb = DataFrameBuilder(i18n=i18n,  request=request, model=model)

    dataframe = dfb.action_request()

    if request == 'category_premises':
        line_numbers = [4, 9, 14]
        media = get_dataframe_table(
            data=dataframe, results=True, line_numbers=line_numbers)
    else:
        media = get_dataframe_table(data=dataframe)

    kb = InlineKeyboardModel(**context_data['keyboard_model'])

    text = i18n.temporary_parameter.text(
        text=i18n.get('name_' + context_data.get('temporary_text')), value=equals_result)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename='pic_filling'), caption=text),
        reply_markup=get_inline_keyboard(keyboard=kb, i18n=i18n,
                                         )
    )

    await state.update_data(temporary_parameter='')
    # await state.update_data(temporary_request='')
    await state.update_data(temporary_text='')
    await state.set_state(state=None)
