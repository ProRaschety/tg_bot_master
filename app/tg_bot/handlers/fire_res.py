import logging
import io
import json

from pathlib import Path
from datetime import datetime
from fluentogram import TranslatorRunner

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.types import CallbackQuery, Message, BufferedInputFile, FSInputFile, InputMediaPhoto, InputFile, InputMediaDocument
from aiogram.utils.chat_action import ChatActionSender
from aiogram.enums import ChatAction

from app.tg_bot.filters.filter_role import IsComrade
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb
from app.tg_bot.utilities.misc_utils import get_temp_folder, get_csv_file, get_csv_bt_file, get_picture_filling, get_initial_data_table
from app.tg_bot.states.fsm_state_data import FSMSteelForm
from app.calculation.fire_resistance.steel_calculation import SteelFireResistance, SteelFireStrength, SteelFireProtection


logging.getLogger('matplotlib.font_manager').disabled = False

log = logging.getLogger(__name__)


fire_res_router = Router()
fire_res_router.message.filter(IsComrade())
fire_res_router.callback_query.filter(IsComrade())


@fire_res_router.callback_query(F.data == 'fire_resistance')
async def fire_resistance_call(callback_data: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    await callback_data.message.bot.send_chat_action(
        chat_id=callback_data.message.chat.id,
        action=ChatAction.TYPING)
    text = i18n.fire_resistance.text()
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'steel_element', 'wood_element', 'concrete_element', 'general_menu', i18n=i18n))

    await callback_data.answer('')


@fire_res_router.callback_query(F.data == 'back_type_material')
async def back_type_material_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.fire_resistance.text()
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'steel_element', 'wood_element', 'concrete_element', 'general_menu', i18n=i18n))

    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['back_type_calc']), ~StateFilter(default_state))
async def back_type_calc_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.type_of_calculation_steel.text()
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'strength_calculation', 'thermal_calculation', 'back_type_material', i18n=i18n))
    await state.clear()
    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['back_type_calc']), StateFilter(default_state))
async def back_type_calc_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.type_of_calculation_steel.text()
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'strength_calculation', 'thermal_calculation', 'back_type_material', i18n=i18n))

    await callback.answer('')


@fire_res_router.callback_query(F.data == 'back_steel_element')
async def back_thermal_calc_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = callback.message.chat.id
    text = i18n.type_of_calculation_steel.text()
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'strength_calculation', 'thermal_calculation', 'back_type_material', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'steel_element')
async def steel_element_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.type_of_calculation_steel.text()
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'strength_calculation', 'thermal_calculation', 'back_type_material', i18n=i18n))  # 'fire_protection',
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'wood_element')
async def wood_element_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.type_of_calculation_wood.text()
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_type_material', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'concrete_element')
async def concrete_element_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.type_of_calculation_concrete.text()
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_type_material', i18n=i18n))
    await callback.answer('')


"""

Пакетный расчет

"""


@fire_res_router.callback_query(F.data.in_(['fire_protection']))
async def fire_protection_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.set_state(FSMSteelForm.add_steel_element_state)
    chat_id = str(callback.message.chat.id)
    text = i18n.fire_protection.text()
    protection_calculation = SteelFireProtection(i18n=i18n, chat_id=chat_id)
    data = protection_calculation.get_init_data_table()
    image_png = protection_calculation.get_initial_data_protection(data=data)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=image_png, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_init_data_protection', 'add_element_steel', 'clear_table_protection_steel', 'back_type_calc', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.add_steel_element_state), F.data == 'clear_table_protection_steel')
async def clear_table_protection_steel_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    text = i18n.clear_table_protection_steel.text()
    protection_calculation = SteelFireProtection(i18n=i18n, chat_id=chat_id)
    data = protection_calculation.clear_table_protection()
    image_png = protection_calculation.get_initial_data_protection(data=data)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=image_png, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_init_data_protection', 'add_element_steel', 'clear_table_protection_steel', 'back_type_calc', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.add_steel_element_state), F.data == 'add_element_steel')
async def add_element_steel_inline_search_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    message_id = callback.message.message_id
    steel_protection_data = await state.get_data()
    await state.update_data(chat_id=chat_id, message_id=message_id)
    await state.update_data(id=None, num_profile=None,
                            type_steel_element=None,
                            num_sides_heated=None,
                            ptm=None,
                            len_elem=None,
                            area_surface_elem_m2=None,
                            n_load=None,
                            t_critic_C=None,
                            time_fsr=None)
    text = i18n.num_profile_inline_search.text()
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text="Найти профиль", switch_inline_query_current_chat="")]])
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=markup)


@fire_res_router.inline_query(StateFilter(FSMSteelForm.add_steel_element_state))
async def show_add_element_steel(inline_query: InlineQuery, state: FSMContext, i18n: TranslatorRunner):
    id_data = await state.get_data()
    chat_id = id_data.get('chat_id')
    q_keys = SteelFireStrength(i18n=i18n, chat_id=chat_id)
    list_sub = q_keys.get_list_num_profile()
    results = []
    for name in list_sub:
        if inline_query.query in str(name):
            results.append(InlineQueryResultArticle(id=str(name), title=f'{name}',
                                                    input_message_content=InputTextMessageContent(message_text=f'{name}')))
    await inline_query.answer(results=results[:20], cache_time=0, is_personal=True)


@fire_res_router.message(StateFilter(FSMSteelForm.add_steel_element_state))
async def add_steel_element_state_input(message: Message, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(message.chat.id)
    id_data = await state.get_data()
    message_id = id_data.get('message_id')
    add_elem_search = message.text
    steel_protection_data = await state.update_data(num_profile=add_elem_search)
    add_elem = steel_protection_data.get('num_profile')
    protection_calculation = SteelFireProtection(i18n=i18n, chat_id=chat_id)
    data = protection_calculation.get_init_data_other_table(element=add_elem)
    image_png = protection_calculation.get_initial_data_protection(data=data)
    text = i18n.initial_data_steel.text()
    await message.delete()
    # await state.clear()
    await bot.edit_message_media(
        chat_id=message.chat.id,
        message_id=message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=image_png, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'edit_init_data_protection',
                                      'add_element_steel',
                                      'clear_table_protection_steel',
                                      'back_type_calc', i18n=i18n))


"""

Прочностной расчет

"""

STRENGTH_CALC_KB = ['edit_init_data_strength',
                    'run_strength_steel', 'back_type_calc']


@fire_res_router.callback_query(F.data.in_(['strength_calculation', 'back_strength_element']))
async def strength_calculation_call(callback: CallbackQuery, bot: Bot, state: FSMContext,  i18n: TranslatorRunner) -> None:
    text = i18n.initial_data_steel.text()
    data = await state.get_data()
    data.setdefault("num_profile", "20Б1"),
    data.setdefault("sketch", "Двутавр"),
    data.setdefault("reg_document", "ГОСТ Р 57837"),
    data.setdefault("num_sides_heated", "num_sides_heated_four"),
    data.setdefault("len_elem", "5000.0"),
    data.setdefault("fixation", "sealing-sealing"),
    data.setdefault("type_loading", "bend_element"),
    data.setdefault("loading_method", "distributed_load_steel"),
    data.setdefault("ptm", "3.94"),
    data.setdefault("n_load", "1000.0"),
    data.setdefault("type_steel_element", "C235"),
    data.setdefault("t_critic_C", "500.0")
    strength_calculation = SteelFireStrength(i18n=i18n, data=data)
    data_out, headers, label = strength_calculation.get_init_data_table()
    media = get_initial_data_table(data=data_out, headers=headers, label=label)
    await state.update_data(data)
    # log.info(f'DataRedis_Strenght: {data}')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1, *STRENGTH_CALC_KB, i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['run_strength_steel']))
async def run_strength_steel_call(callback: CallbackQuery, state: FSMContext, bot: Bot, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    strength_calculation = SteelFireStrength(i18n=i18n, data=data)
    data_out, headers, label = strength_calculation.get_init_data_table()
    media = get_initial_data_table(data=data_out, headers=headers, label=label)
    t_critic_C = strength_calculation.get_crit_temp_steel()
    type_loading = data.get('type_loading', 'compression_element')
    if type_loading == 'compression_element':
        gamma_t, gamma_elasticity = strength_calculation.get_coef_strength()
        text = i18n.compression_element_result.text(
            gamma_t=gamma_t, gamma_elasticity=gamma_elasticity, t_critic=round(t_critic_C, 1))
    else:
        gamma = strength_calculation.get_coef_strength()
        text = i18n.stretch_or_bend_element_result.text(
            gamma=gamma, t_critic=round(t_critic_C, 1))
    await state.update_data(t_critic_C=t_critic_C)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'thermal_calculation', 'protocol_strength', 'back_strength_element', 'back_type_calc', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'protocol_strength')
async def protocol_strength_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.protocol_strength.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'export_data_strength', 'back_strength_element', 'back_type_calc',  i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['edit_init_data_strength', 'stop_edit_strength']))
async def edit_init_data_strength_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1,
                                      'type_steel_element_edit',
                                      'num_profile',
                                      'sides_heated',
                                      'len_elem_edit',
                                      'type_of_load_edit',
                                      'loads_steel_edit',
                                      'type_loading_element',
                                      'fixation_steel',
                                      'back_strength_element', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'num_profile')
async def num_profile_inline_search_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    message_id = callback.message.message_id
    await state.update_data(chat_id=chat_id, message_id=message_id)
    text = i18n.num_profile_inline_search.text()
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text="Выбрать профиль 🔎", switch_inline_query_current_chat="")]])
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=markup)
    await state.set_state(FSMSteelForm.num_profile_inline_search_state)


@fire_res_router.inline_query(StateFilter(FSMSteelForm.num_profile_inline_search_state))
async def show_num_profile(inline_query: InlineQuery, state: FSMContext, i18n: TranslatorRunner):
    data = await state.get_data()
    q_keys = SteelFireStrength(i18n=i18n, data=data)
    list_sub = q_keys.get_list_num_profile()
    results = []
    for name in list_sub:
        if inline_query.query in str(name):
            results.append(InlineQueryResultArticle(id=str(name), title=f'{name}',
                                                    input_message_content=InputTextMessageContent(message_text=f'{name}')))
    await inline_query.answer(results=results[:50], cache_time=0, is_personal=True)


@fire_res_router.message(StateFilter(FSMSteelForm.num_profile_inline_search_state))
async def num_profile_inline_search_input(message: Message, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.update_data(num_profile=message.text)
    data = await state.get_data()
    message_id = data.get('message_id')
    strength_calculation = SteelFireStrength(i18n=i18n, data=data)
    data_out, headers, label = strength_calculation.get_init_data_table()
    media = get_initial_data_table(data=data_out, headers=headers, label=label)
    ptm = strength_calculation.get_reduced_thickness()
    await state.update_data(ptm=ptm)
    text = i18n.initial_data_steel.text()
    await message.delete()
    await state.set_state(state=None)
    await bot.edit_message_media(
        chat_id=message.chat.id,
        message_id=message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'type_steel_element_edit',
                                      'num_profile',
                                      'sides_heated',
                                      'len_elem_edit',
                                      'type_of_load_edit',
                                      'loads_steel_edit',
                                      'type_loading_element',
                                      'fixation_steel',
                                      'back_strength_element', i18n=i18n))


@fire_res_router.callback_query(F.data == 'loads_steel_edit')
async def loads_steel_edit_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    text = i18n.loads_steel_edit.text(n_load=data.get('n_load'))
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))
    await state.set_state(FSMSteelForm.n_load_edit_state)
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.n_load_edit_state), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero']))
async def n_load_edit_var_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    n_load_data = await state.get_data()
    call_data = callback.data
    if call_data == "one":
        call_data = 1
    elif call_data == "two":
        call_data = 2
    elif call_data == "three":
        call_data = 3
    elif call_data == "four":
        call_data = 4
    elif call_data == "five":
        call_data = 5
    elif call_data == "six":
        call_data = 6
    elif call_data == "seven":
        call_data = 7
    elif call_data == "eight":
        call_data = 8
    elif call_data == "nine":
        call_data = 9
    elif call_data == "zero":
        call_data = 0

    if call_data != 'clear':
        if n_load_data.get('n_load') == None:
            await state.update_data(n_load="")
            n_load_data = await state.get_data()
            await state.update_data(n_load=call_data)
            n_load_data = await state.get_data()
            n_load_edit = n_load_data.get('n_load', 3600)
            text = i18n.loads_steel_edit.text(n_load=n_load_edit)
        else:
            n_load_1 = n_load_data.get('n_load')
            n_load_sum = str(n_load_1) + str(call_data)
            await state.update_data(n_load=n_load_sum)
            n_load_data = await state.get_data()
            n_load_edit = n_load_data.get('n_load', 3600)
            text = i18n.loads_steel_edit.text(n_load=n_load_edit)
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))


@fire_res_router.callback_query(StateFilter(FSMSteelForm.n_load_edit_state), F.data.in_(['point']))
async def n_load_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    n_load_data = await state.get_data()
    call_data = callback.data
    if call_data == "point":
        call_data = '.'

    if n_load_data.get('n_load') == None:
        await state.update_data(n_load="")
        n_load_data = await state.get_data()
        await state.update_data(n_load=call_data)
        n_load_data = await state.get_data()
        n_load_edit = n_load_data.get('n_load', 3600)
        await state.update_data(n_load=n_load_edit)
        text = i18n.loads_steel_edit.text(n_load=n_load_edit)
    else:
        n_load_1 = n_load_data.get('n_load')
        n_load_sum = str(n_load_1) + str(call_data)
        await state.update_data(n_load=n_load_sum)
        n_load_data = await state.get_data()
        n_load_edit = n_load_data.get('n_load', 3600)
        await state.update_data(n_load=n_load_edit)
        text = i18n.loads_steel_edit.text(n_load=n_load_edit)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))


@fire_res_router.callback_query(StateFilter(FSMSteelForm.n_load_edit_state), F.data.in_(['clear']))
async def n_load_edit_point_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.update_data(n_load="")
    n_load_data = await state.get_data()
    n_load_edit = n_load_data.get('n_load', 3600)
    text = i18n.loads_steel_edit.text(n_load=n_load_edit)
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.n_load_edit_state), F.data.in_(['ready']))
async def n_load_edit_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    strength_calculation = SteelFireStrength(i18n=i18n, data=data)
    data_out, headers, label = strength_calculation.get_init_data_table()
    media = get_initial_data_table(data=data_out, headers=headers, label=label)
    # image_png = strength_calculation.get_initial_data_strength()
    text = i18n.initial_data_steel.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'type_steel_element_edit',
                                      'num_profile',
                                      'sides_heated',
                                      'len_elem_edit',
                                      'type_of_load_edit',
                                      'loads_steel_edit',
                                      'type_loading_element',
                                      'fixation_steel',
                                      'back_strength_element', i18n=i18n))
    await state.set_state(state=None)
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'sides_heated')
async def sides_heated_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.num_sides_heated.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fsr_num_sides_ibeam.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="sides_ibeam"), caption=text),
        reply_markup=get_inline_cd_kb(2, 'num_sides_heated_four', 'num_sides_heated_three',  'stop_edit_strength', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['num_sides_heated_two', 'num_sides_heated_three', 'num_sides_heated_four']))
async def type_of_load_edit_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.update_data(num_sides_heated=callback.data)
    data = await state.get_data()
    strength_calculation = SteelFireStrength(i18n=i18n, data=data)
    ptm = str(strength_calculation.get_reduced_thickness())
    data_out, headers, label = strength_calculation.get_init_data_table()
    media = get_initial_data_table(data=data_out, headers=headers, label=label)
    text = i18n.initial_data_steel.text()
    await state.update_data(ptm=ptm)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'type_steel_element_edit',
                                      'num_profile',
                                      'sides_heated',
                                      'len_elem_edit',
                                      'type_of_load_edit',
                                      'loads_steel_edit',
                                      'type_loading_element',
                                      'fixation_steel',
                                      'back_strength_element', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'len_elem_edit')
async def len_elem_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    text = i18n.len_elem_edit.text(len_elem=data.get('len_elem'))
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))
    await state.set_state(FSMSteelForm.len_elem_edit_state)
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.len_elem_edit_state), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero']))
async def len_elem_edit_var_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    len_elem_data = await state.get_data()

    call_data = callback.data
    if call_data == "one":
        call_data = 1
    elif call_data == "two":
        call_data = 2
    elif call_data == "three":
        call_data = 3
    elif call_data == "four":
        call_data = 4
    elif call_data == "five":
        call_data = 5
    elif call_data == "six":
        call_data = 6
    elif call_data == "seven":
        call_data = 7
    elif call_data == "eight":
        call_data = 8
    elif call_data == "nine":
        call_data = 9
    elif call_data == "zero":
        call_data = 0

    if call_data != 'clear':
        if len_elem_data.get('len_elem') == None:
            await state.update_data(len_elem="")
            len_elem_data = await state.get_data()
            await state.update_data(len_elem=call_data)
            len_elem_data = await state.get_data()
            len_elem_edit = len_elem_data.get('len_elem', 1000)

            text = i18n.len_elem_edit.text(len_elem=len_elem_edit)
        else:
            len_elem_1 = len_elem_data.get('len_elem')
            len_elem_sum = str(len_elem_1) + str(call_data)
            await state.update_data(len_elem=len_elem_sum)
            len_elem_data = await state.get_data()
            len_elem_edit = len_elem_data.get('len_elem', 1000)

            text = i18n.len_elem_edit.text(len_elem=len_elem_edit)
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))


@fire_res_router.callback_query(StateFilter(FSMSteelForm.len_elem_edit_state), F.data.in_(['point']))
async def len_elem_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    len_elem_data = await state.get_data()

    call_data = callback.data
    if call_data == "point":
        call_data = '.'

    if len_elem_data.get('len_elem') == None:
        await state.update_data(len_elem="")
        len_elem_data = await state.get_data()
        await state.update_data(len_elem=call_data)
        len_elem_data = await state.get_data()
        len_elem_edit = len_elem_data.get('len_elem', 3600)
        text = i18n.len_elem_edit.text(len_elem=len_elem_edit)
    else:
        len_elem_1 = len_elem_data.get('len_elem')
        len_elem_sum = str(len_elem_1) + str(call_data)
        await state.update_data(len_elem=len_elem_sum)
        len_elem_data = await state.get_data()
        len_elem_edit = len_elem_data.get('len_elem', 3600)
        text = i18n.len_elem_edit.text(len_elem=len_elem_edit)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))


@fire_res_router.callback_query(StateFilter(FSMSteelForm.len_elem_edit_state), F.data.in_(['clear']))
async def len_elem_edit_point_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    call_data = callback.data
    len_elem_data = await state.get_data()
    await state.update_data(len_elem="")
    len_elem_data = await state.get_data()
    len_elem_edit = len_elem_data.get('len_elem', 1000)
    text = i18n.len_elem_edit.text(len_elem=len_elem_edit)
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.len_elem_edit_state), F.data.in_(['ready']))
async def len_elem_edit_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    strength_calculation = SteelFireStrength(i18n=i18n, data=data)
    data_out, headers, label = strength_calculation.get_init_data_table()
    media = get_initial_data_table(data=data_out, headers=headers, label=label)
    # image_png = strength_calculation.get_initial_data_strength()
    text = i18n.initial_data_steel.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'type_steel_element_edit',
                                      'num_profile',
                                      'sides_heated',
                                      'len_elem_edit',
                                      'type_of_load_edit',
                                      'loads_steel_edit',
                                      'type_loading_element',
                                      'fixation_steel',
                                      'back_strength_element', i18n=i18n))
    await state.set_state(state=None)
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'type_of_load_edit')
async def type_of_load_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.type_of_load_edit.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(2, 'distributed_load_steel', 'concentrated_load_steel', 'stop_edit_strength', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['distributed_load_steel', 'concentrated_load_steel']))
async def type_of_load_edit_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.update_data(loading_method=callback.data)
    data = await state.get_data()
    strength_calculation = SteelFireStrength(i18n=i18n, data=data)
    data_out, headers, label = strength_calculation.get_init_data_table()
    # media = get_initial_data_table(data=data_out, headers=headers, label=label)
    # image_png = strength_calculation.get_initial_data_strength()
    text = i18n.initial_data_steel.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'type_steel_element_edit',
                                      'num_profile',
                                      'sides_heated',
                                      'len_elem_edit',
                                      'type_of_load_edit',
                                      'loads_steel_edit',
                                      'type_loading_element',
                                      'fixation_steel',
                                      'back_strength_element', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'fixation_steel')
async def fixation_steel_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.consolidation_steel.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'hinge-hinge', 'sealing-sealing', 'seal-hinge', 'console', 'stop_edit_strength', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['hinge-hinge', 'sealing-sealing', 'seal-hinge', 'console']))
async def fixation_steel_edit_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.update_data(fixation=callback.data)
    data = await state.get_data()
    strength_calculation = SteelFireStrength(i18n=i18n, data=data)
    data_out, headers, label = strength_calculation.get_init_data_table()
    media = get_initial_data_table(data=data_out, headers=headers, label=label)
    # image_png = strength_calculation.get_initial_data_strength()
    text = i18n.initial_data_steel.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'type_steel_element_edit',
                                      'num_profile',
                                      'sides_heated',
                                      'len_elem_edit',
                                      'type_of_load_edit',
                                      'loads_steel_edit',
                                      'type_loading_element',
                                      'fixation_steel',
                                      'back_strength_element', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'type_steel_element_edit')
async def type_steel_element_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.type_steel_element_edit.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'C235', 'C255', 'C355', 'C390', 'C355P', 'C390P', 'stop_edit_strength', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['C235', 'C245', 'C255', 'C345',
                                            'C355', 'C375', 'C390', 'C440',
                                            'C550', 'C590', 'C355P', 'C390P']))
async def type_steel_element_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    call_data = i18n.get(callback.data)
    await state.update_data(type_steel_element=call_data)
    data = await state.get_data()
    strength_calculation = SteelFireStrength(i18n=i18n, data=data)
    data_out, headers, label = strength_calculation.get_init_data_table()
    media = get_initial_data_table(data=data_out, headers=headers, label=label)
    # image_png = strength_calculation.get_initial_data_strength()
    text = i18n.initial_data_steel.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'type_steel_element_edit',
                                      'num_profile',
                                      'sides_heated',
                                      'len_elem_edit',
                                      'type_of_load_edit',
                                      'loads_steel_edit',
                                      'type_loading_element',
                                      'fixation_steel',
                                      'back_strength_element', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'type_loading_element')
async def type_loading_element_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.type_loading_element.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'stretching_element', 'compression_element', 'bend_element', 'stop_edit_strength', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['stretching_element', 'compression_element', 'bend_element']))
async def stretching_element_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.update_data(type_loading=callback.data)
    data = await state.get_data()
    strength_calculation = SteelFireStrength(i18n=i18n, data=data)
    data_out, headers, label = strength_calculation.get_init_data_table()
    media = get_initial_data_table(data=data_out, headers=headers, label=label)
    # image_png = strength_calculation.get_initial_data_strength()
    text = i18n.initial_data_steel.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'type_steel_element_edit',
                                      'num_profile',
                                      'sides_heated',
                                      'len_elem_edit',
                                      'type_of_load_edit',
                                      'loads_steel_edit',
                                      'type_loading_element',
                                      'fixation_steel',
                                      'back_strength_element', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['export_data_strength']))
async def export_data_strength_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.export_data_strength.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'back_strength_element', 'back_type_calc', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'ibeam_element')
async def ibeam_element_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    # хендлер возвращает картинку с исходными данными для прочностного расчета для двутавра №20
    chat_id = str(callback.message.chat.id)
    text = i18n.initial_data_steel.text()

    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        media = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(2,
                                      'back_strength_element', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'channel_element')
async def channel_element_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    # хендлер возвращает картинку с исходными данными для прочностного расчета для двутавра №20
    text = i18n.initial_data_steel.text()
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        media = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(2,
                                      'back_strength_element', i18n=i18n))
    await callback.answer('')


"""

Теплотехнический расчет


"""

THERMAL_CALC_KB = ['edit_init_data_thermal',
                   'run_thermal_steel', 'back_type_calc']


@fire_res_router.callback_query(F.data.in_(['thermal_calculation', 'forward_type_calc']))
async def thermal_calculation_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    data.setdefault("mode", "Стандартный"),
    data.setdefault("s_0", "0.85"),
    data.setdefault("s_1", "0.625"),
    data.setdefault("T_0", "293.0"),
    data.setdefault("a_convection", "29.0"),
    data.setdefault("density_steel", "7800.0"),
    data.setdefault("heat_capacity", "310.0"),
    data.setdefault("ptm", "3.94"),
    data.setdefault("heat_capacity_change", "0.469"),
    data.setdefault("t_critic_C", "500.0")
    text = i18n.initial_data_steel.text()
    t_res = SteelFireResistance(i18n=i18n, data=data)
    data_out, headers, label = t_res.get_initial_data_thermal()
    media = get_initial_data_table(data=data_out, headers=headers, label=label)
    await state.update_data(data)
    # log.info(f'DataRedis_Thermal: {data}')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="initial_data_thermal"), caption=text),
        reply_markup=get_inline_cd_kb(1, *THERMAL_CALC_KB, i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['run_thermal_steel', 'plot_thermal']))
async def run_thermal_calculation_call(callback: CallbackQuery, state: FSMContext, bot: Bot, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    t_res = SteelFireResistance(i18n=i18n, data=data)
    t_fsr, plot_thermal_png = t_res.get_plot_steel()
    text = i18n.thermal_calculation.text(time_fsr=round(t_fsr/60, 2))
    await state.update_data(time_fsr=t_fsr/60)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=plot_thermal_png, filename="plot_thermal_png"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'strength_calculation', 'protocol_thermal', 'export_data_steel',  'forward_type_calc', 'back_type_calc', i18n=i18n))
    await state.set_state(state=None)
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'stop_edit_thermal_calc', ~StateFilter(default_state))
async def stop_edit_thermal_calc_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, *THERMAL_CALC_KB, i18n=i18n))
    await state.set_state(state=None)
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'back_thermal_calc')
async def back_thermal_calc_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1,  *THERMAL_CALC_KB, i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'edit_init_data_thermal')
async def edit_init_data_thermal_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, 'mode_edit', 'ptm_edit', 't_critic_edit', 'back_thermal_calc', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'mode_edit')
async def mode_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, 'mode_standard', 'mode_hydrocarbon', 'mode_external', 'mode_smoldering', 'stop_edit_thermal_calc', i18n=i18n))
    await state.set_state(FSMSteelForm.mode_edit_state)
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'ptm_edit')
async def ptm_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    ptm = data.get("ptm", 4.8)
    text = i18n.ptm_edit.text(ptm=round(float(ptm), 2))
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))
    await state.set_state(FSMSteelForm.ptm_edit_state)
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.ptm_edit_state), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero']))
async def ptm_edit_var_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    ptm_data = await state.get_data()
    call_data = callback.data
    if call_data == "one":
        call_data = 1
    elif call_data == "two":
        call_data = 2
    elif call_data == "three":
        call_data = 3
    elif call_data == "four":
        call_data = 4
    elif call_data == "five":
        call_data = 5
    elif call_data == "six":
        call_data = 6
    elif call_data == "seven":
        call_data = 7
    elif call_data == "eight":
        call_data = 8
    elif call_data == "nine":
        call_data = 9
    elif call_data == "zero":
        call_data = 0
    if call_data != 'clear':
        if ptm_data.get('ptm') == None:
            await state.update_data(ptm="")
            ptm_data = await state.get_data()
            await state.update_data(ptm=call_data)
            ptm_data = await state.get_data()
            ptm_edit = ptm_data.get('ptm', 4.8)
            text = i18n.ptm_edit.text(ptm=ptm_edit)
        else:
            ptm_1 = ptm_data.get('ptm')
            ptm_sum = str(ptm_1) + str(call_data)
            await state.update_data(ptm=ptm_sum)
            ptm_data = await state.get_data()
            ptm_edit = ptm_data.get('ptm', 4.8)
            text = i18n.ptm_edit.text(ptm=ptm_edit)
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))


@fire_res_router.callback_query(StateFilter(FSMSteelForm.ptm_edit_state), F.data.in_(['point']))
async def ptm_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    ptm_data = await state.get_data()
    call_data = callback.data
    if call_data == "point":
        call_data = '.'

    if ptm_data.get('ptm') == None:
        await state.update_data(ptm="")
        ptm_data = await state.get_data()
        await state.update_data(ptm=call_data)
        ptm_data = await state.get_data()
        ptm_edit = ptm_data.get('ptm', 4.8)
        text = i18n.ptm_edit.text(ptm=ptm_edit)
    else:
        ptm_1 = ptm_data.get('ptm')
        ptm_sum = str(ptm_1) + str(call_data)
        await state.update_data(ptm=ptm_sum)
        ptm_data = await state.get_data()
        ptm_edit = ptm_data.get('ptm', 4.8)
        text = i18n.ptm_edit.text(ptm=ptm_edit)
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))


@fire_res_router.callback_query(StateFilter(FSMSteelForm.ptm_edit_state), F.data.in_(['clear']))
async def ptm_edit_point_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    ptm_data = await state.get_data()
    await state.update_data(ptm="")
    ptm_data = await state.get_data()
    ptm_edit = ptm_data.get('ptm', 4.8)
    text = i18n.ptm_edit.text(ptm=ptm_edit)
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.ptm_edit_state), F.data.in_(['ready']))
async def ptm_edit_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    t_res = SteelFireResistance(i18n=i18n, data=data)
    text = i18n.initial_data_steel.text()
    data_out, headers, label = t_res.get_initial_data_thermal()
    media = get_initial_data_table(data=data_out, headers=headers, label=label)
    # image_png = t_res.get_initial_data_thermal()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="initial_data_thermal"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'mode_edit', 'ptm_edit', 't_critic_edit', 'back_thermal_calc', i18n=i18n))
    await state.set_state(state=None)
    await callback.answer('')


@fire_res_router.callback_query(F.data == 't_critic_edit')
async def t_critic_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    t_critic_C = data.get("t_critic_C", 500.0)
    text = i18n.t_critic_edit.text(t_critic=round(float(t_critic_C), 1))
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))
    await state.set_state(FSMSteelForm.t_critic_edit_state)
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.t_critic_edit_state), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear']))
async def t_critic_edit_var_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    t_data = await state.get_data()
    call_data = callback.data
    if call_data == "one":
        call_data = 1
    elif call_data == "two":
        call_data = 2
    elif call_data == "three":
        call_data = 3
    elif call_data == "four":
        call_data = 4
    elif call_data == "five":
        call_data = 5
    elif call_data == "six":
        call_data = 6
    elif call_data == "seven":
        call_data = 7
    elif call_data == "eight":
        call_data = 8
    elif call_data == "nine":
        call_data = 9
    elif call_data == "zero":
        call_data = 0
    elif call_data == "point":
        call_data = "."

    if call_data != 'clear':
        if t_data.get('t_critic_C') == None:
            await state.update_data(t_critic_C="")
            t_data = await state.get_data()
            await state.update_data(t_critic_C=call_data)
            t_data = await state.get_data()
            t_edit = t_data.get('t_critic_C', 500)
            text = i18n.t_critic_edit.text(t_critic=t_edit)
        else:
            t_1 = t_data.get('t_critic_C')
            t_sum = str(t_1) + str(call_data)
            await state.update_data(t_critic_C=t_sum)
            t_data = await state.get_data()
            t_edit = t_data.get('t_critic_C', 500)
            text = i18n.t_critic_edit.text(t_critic=t_edit)
    elif call_data == "clear":
        await state.update_data(t_critic_C="")
        t_data = await state.get_data()
        t_edit = t_data.get('t_critic_C', 500)
        text = i18n.t_critic_edit.text(t_critic=t_edit)
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.t_critic_edit_state), F.data.in_(['ready']))
async def t_critic_edit_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    t_res = SteelFireResistance(i18n=i18n, data=data)
    text = i18n.initial_data_steel.text()
    data_out, headers, label = t_res.get_initial_data_thermal()
    media = get_initial_data_table(data=data_out, headers=headers, label=label)
    # image_png = t_res.get_initial_data_thermal()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="initial_data_thermal"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'mode_edit', 'ptm_edit', 't_critic_edit', 'back_thermal_calc', i18n=i18n))
    await state.set_state(state=None)
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.mode_edit_state), F.data.in_(['mode_standard', 'mode_hydrocarbon', 'mode_external', 'mode_smoldering']))
async def mode_edit_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.update_data(mode=str(i18n.get(callback.data)))
    data = await state.get_data()
    text = i18n.initial_data_steel.text()
    t_res = SteelFireResistance(i18n=i18n, data=data)
    data_out, headers, label = t_res.get_initial_data_thermal()
    media = get_initial_data_table(data=data_out, headers=headers, label=label)
    # image_png = t_res.get_initial_data_thermal()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="initial_data_thermal"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'mode_edit', 'ptm_edit', 't_critic_edit', 'back_thermal_calc', i18n=i18n))
    await state.set_state(state=None)
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'protocol_thermal')
async def protocol_thermal_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.protocol_thermal.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'export_data_steel', 'forward_type_calc',  i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'export_data_steel')
async def export_data_steel_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    t_res = SteelFireResistance(i18n=i18n, data=data)
    text = i18n.export_data_steel.text()
    data_exp = t_res.get_data_steel_heating()
    file_csv = get_csv_bt_file(data=data_exp)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaDocument(media=BufferedInputFile(
            file=file_csv, filename="data_thermal.csv"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'plot_thermal', 'forward_type_calc', i18n=i18n))
    await callback.answer('')
