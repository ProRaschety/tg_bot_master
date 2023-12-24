import logging
import io
from pathlib import Path
import json
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

from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb
from app.tg_bot.utilities.misc_utils import get_temp_folder, get_csv_file, get_csv_bt_file, get_picture_filling
from app.tg_bot.states.fsm_state_data import FSMSteelForm
from app.calculation.fire_resistance.steel_calculation import SteelFireResistance, SteelFireStrength, SteelFireProtection

logging.getLogger('matplotlib.font_manager').disabled = True
log = logging.getLogger(__name__)
# log = logging.getLogger('matplotlib').setLevel(logging.ERROR)
# log = logging.getLogger('PIL.PngImagePlugin').setLevel(logging.ERROR)


fire_res_router = Router()


@fire_res_router.callback_query(F.data == 'fire_resistance')
async def fire_resistance_call(callback_data: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    await callback_data.message.bot.send_chat_action(
        chat_id=callback_data.message.chat.id,
        action=ChatAction.TYPING)
    text = i18n.fire_resistance.text()
    file_pic = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await callback_data.message.answer_photo(
        photo=BufferedInputFile(
            file=file_pic, filename="pic_filling.png"),
        caption=text,
        has_spoiler=False,
        reply_markup=get_inline_cd_kb(1, 'steel_element', 'wood_element', 'concrete_element', 'general_menu', i18n=i18n))
    await callback_data.answer('')
    await callback_data.message.delete()


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
        reply_markup=get_inline_cd_kb(1, 'fire_protection',  'strength_calculation', 'thermal_calculation', 'back_type_material', i18n=i18n))
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
        reply_markup=get_inline_cd_kb(1, 'fire_protection',  'strength_calculation', 'thermal_calculation', 'back_type_material', i18n=i18n))

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
        reply_markup=get_inline_cd_kb(1, 'fire_protection',  'strength_calculation', 'thermal_calculation', 'back_type_material', i18n=i18n))
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
        reply_markup=get_inline_cd_kb(1, 'fire_protection',  'strength_calculation', 'thermal_calculation', 'back_type_material', i18n=i18n))
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


@fire_res_router.callback_query(F.data.in_(['strength_calculation', 'back_strength_element']))
async def strength_calculation_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.initial_data_steel.text()
    chat_id = str(callback.message.chat.id)

    with open('app\infrastructure\init_data\init_data_strenght_steel.json', encoding='utf-8') as file_op:
        init_strenght_in = json.load(file_op)
        if chat_id not in init_strenght_in:
            init_strenght_in[chat_id] = {"num_profile": "20Б1",
                                         "sketch": "Двутавр",
                                         "reg_document": "ГОСТ Р 57837",
                                         "num_sides_heated": "num_sides_heated_four",
                                         "len_elem": 5000.0,
                                         "fixation": 'sealing-sealing',
                                         "type_loading": "bend_element",
                                         "type_element": "Балка",
                                         "loading_method": 'distributed_load_steel',
                                         "ptm": 3.94,
                                         "e_n_kg_cm2": 2100000.0,
                                         "n_load": 1000.0,
                                         "type_steel_element": "C235",
                                         "quan_elem": 1,
                                         "t_critic_C": 500.0
                                         }

        with open('app\infrastructure\init_data\init_data_strenght_steel.json', 'w', encoding='utf-8') as file_w:
            json.dump(init_strenght_in, file_w,
                      ensure_ascii=False, indent=4)

    # with open('app\infrastructure\init_data\init_data_strenght_steel.json', encoding='utf-8') as file_op:
    #     init_strenght_in = json.load(file_op)

    #     name_profile = init_strenght_in[chat_id]["name_profile"]
    #     sketch = init_strenght_in[chat_id]["sketch"]
    #     reg_document = init_strenght_in[chat_id]["reg_document"]
    #     num_sides_heated = init_strenght_in[chat_id]["num_sides_heated"]
    #     len_elem = init_strenght_in[chat_id]["len_elem"]
    #     fixation = init_strenght_in[chat_id]["fixation"]
    #     type_loading = init_strenght_in[chat_id]["type_loading"]
    #     n_load = init_strenght_in[chat_id]["n_load"]
    #     type_steel_element = init_strenght_in[chat_id]["type_steel_element"]
    #     loading_method = init_strenght_in[chat_id]["loading_method"]

    # strength_calculation = SteelStrength(i18n=i18n, chat_id=chat_id,
    #                                      name_profile=name_profile,
    #                                      sketch=sketch,
    #                                      reg_document=reg_document,
    #                                      num_sides_heated=num_sides_heated,
    #                                      fixation=fixation,
    #                                      type_loading=type_loading,
    #                                      len_elem=len_elem,
    #                                      n_load=n_load,
    #                                      type_steel_element=type_steel_element,
    #                                      loading_method=loading_method)
    strength_calculation = SteelFireStrength(i18n=i18n, chat_id=chat_id)
    image_png = strength_calculation.get_initial_data_strength()

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=image_png, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'edit_init_data_strength',
                                      'run_strength_steel',
                                      'back_type_calc', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['run_strength_steel']))
async def run_strength_steel_call(callback: CallbackQuery, state: FSMContext, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)

    with open('app\infrastructure\init_data\init_data_strenght_steel.json', encoding='utf-8') as file_op:
        init_strenght_out = json.load(file_op)
    #     name_profile = init_strenght_out[chat_id]["name_profile"]
    #     sketch = init_strenght_out[chat_id]["sketch"]
    #     reg_document = init_strenght_out[chat_id]["reg_document"]
    #     num_sides_heated = init_strenght_out[chat_id]["num_sides_heated"]
    #     len_elem = init_strenght_out[chat_id]["len_elem"]
    #     fixation = init_strenght_out[chat_id]["fixation"]
        type_loading = init_strenght_out[chat_id]["type_loading"]
    #     n_load = init_strenght_out[chat_id]["n_load"]
    #     type_steel_element = init_strenght_out[chat_id]["type_steel_element"]
    #     loading_method = init_strenght_out[chat_id]["loading_method"]

    # strength_calculation = SteelStrength(i18n=i18n, chat_id=chat_id,
    #                                      name_profile=name_profile,
    #                                      sketch=sketch,
    #                                      reg_document=reg_document,
    #                                      num_sides_heated=num_sides_heated,
    #                                      fixation=fixation,
    #                                      type_loading=type_loading,
    #                                      len_elem=len_elem,
    #                                      n_load=n_load,
    #                                      type_steel_element=type_steel_element,
    #                                      loading_method=loading_method)

    strength_calculation = SteelFireStrength(i18n=i18n, chat_id=chat_id)
    image_png = strength_calculation.get_initial_data_strength()

    t_critic_C = strength_calculation.get_crit_temp_steel()

    init_strenght_out[chat_id]["t_critic_C"] = t_critic_C
    with open('app\infrastructure\init_data\init_data_strenght_steel.json', 'w', encoding='utf-8') as file_w:
        json.dump(init_strenght_out, file_w,
                  ensure_ascii=False, indent=4)

    if type_loading == 'compression_element':
        gamma_t, gamma_elasticity = strength_calculation.get_coef_strength()
        text = i18n.compression_element_result.text(
            gamma_t=gamma_t, gamma_elasticity=gamma_elasticity, t_critic=round(t_critic_C, 1))
    else:
        gamma = strength_calculation.get_coef_strength()
        text = i18n.stretch_or_bend_element_result.text(
            gamma=gamma, t_critic=round(t_critic_C, 1))

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=image_png, filename="initial_data"), caption=text),
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
    chat_id = callback.message.chat.id

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

    id_data = await state.get_data()
    id_data = await state.update_data(chat_id=chat_id, message_id=message_id)

    text = i18n.num_profile_inline_search.text()

    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text="Найти профиль", switch_inline_query_current_chat="")]])

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=markup)

    await state.set_state(FSMSteelForm.num_profile_inline_search_state)


@fire_res_router.inline_query(StateFilter(FSMSteelForm.num_profile_inline_search_state))
async def show_num_profile(inline_query: InlineQuery, state: FSMContext, i18n: TranslatorRunner):
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


@fire_res_router.message(StateFilter(FSMSteelForm.num_profile_inline_search_state))
async def num_profile_inline_search_input(message: Message, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(message.chat.id)
    id_data = await state.get_data()
    message_id = id_data.get('message_id')
    log.info(
        f"Номер сообщения: {message_id}")
    num_profile_search = message.text

    with open('app\infrastructure\init_data\init_data_strenght_steel.json', encoding='utf-8') as file_op:
        init_strenght_out = json.load(file_op)
    init_strenght_out[chat_id]["num_profile"] = num_profile_search
    with open('app\infrastructure\init_data\init_data_strenght_steel.json', 'w', encoding='utf-8') as file_w:
        json.dump(init_strenght_out, file_w,
                  ensure_ascii=False, indent=4)

    strength_calculation = SteelFireStrength(i18n=i18n, chat_id=chat_id)
    image_png = strength_calculation.get_initial_data_strength()
    text = i18n.initial_data_steel.text()
    await message.delete()
    await state.clear()
    await bot.edit_message_media(
        chat_id=message.chat.id,
        message_id=message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=image_png, filename="initial_data"), caption=text),
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
    chat_id = str(callback.message.chat.id)

    with open('app\infrastructure\init_data\init_data_strenght_steel.json', encoding='utf-8') as file_op:
        init_strenght_in = json.load(file_op)
        n_load = init_strenght_in[chat_id]['n_load']

    text = i18n.loads_steel_edit.text(n_load=n_load)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))

    await state.set_state(FSMSteelForm.n_load_edit_state)
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.n_load_edit_state), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero']))
async def n_load_edit_var_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
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
        if n_load_data.get('n_load_key') == None:
            await state.update_data(n_load_key="")
            n_load_data = await state.get_data()
            await state.update_data(n_load_key=call_data)
            n_load_data = await state.get_data()
            n_load_edit = n_load_data.get('n_load_key', 3600)
            text = i18n.loads_steel_edit.text(n_load=n_load_edit)
        else:
            n_load_1 = n_load_data.get('n_load_key')
            n_load_sum = str(n_load_1) + str(call_data)
            await state.update_data(n_load_key=n_load_sum)
            n_load_data = await state.get_data()
            n_load_edit = n_load_data.get('n_load_key', 3600)
            text = i18n.loads_steel_edit.text(n_load=n_load_edit)

    with open('app\infrastructure\init_data\init_data_strenght_steel.json', encoding='utf-8') as file_op:
        init_strenght_in = json.load(file_op)
    init_strenght_in[chat_id]['n_load'] = n_load_edit
    with open('app\infrastructure\init_data\init_data_strenght_steel.json', 'w', encoding='utf-8') as file_w:
        json.dump(init_strenght_in, file_w,
                  ensure_ascii=False, indent=4)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))


@fire_res_router.callback_query(StateFilter(FSMSteelForm.n_load_edit_state), F.data.in_(['point']))
async def n_load_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    n_load_data = await state.get_data()

    call_data = callback.data
    if call_data == "point":
        call_data = '.'

    if n_load_data.get('n_load_key') == None:
        await state.update_data(n_load_key="")
        n_load_data = await state.get_data()
        await state.update_data(n_load_key=call_data)
        n_load_data = await state.get_data()
        n_load_edit = n_load_data.get('n_load_key', 3600)
        text = i18n.loads_steel_edit.text(n_load=n_load_edit)
    else:
        n_load_1 = n_load_data.get('n_load_key')
        n_load_sum = str(n_load_1) + str(call_data)
        await state.update_data(n_load_key=n_load_sum)
        n_load_data = await state.get_data()
        n_load_edit = n_load_data.get('n_load_key', 3600)
        text = i18n.loads_steel_edit.text(n_load=n_load_edit)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))


@fire_res_router.callback_query(StateFilter(FSMSteelForm.n_load_edit_state), F.data.in_(['clear']))
async def n_load_edit_point_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    call_data = callback.data
    n_load_data = await state.get_data()

    await state.update_data(n_load_key="")
    n_load_data = await state.get_data()
    n_load_edit = n_load_data.get('n_load_key', 3600)
    text = i18n.loads_steel_edit.text(n_load=n_load_edit)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.n_load_edit_state), F.data.in_(['ready']))
async def n_load_edit_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    # call_data = callback.data
    # n_load_data = await state.get_data()
    # n_load = n_load_data.get('n_load_key', 3600)

    # with open('app\infrastructure\init_data\init_data_strenght_steel.json', encoding='utf-8') as file_op:
    #     init_strenght_in = json.load(file_op)
    #     name_profile = init_strenght_in[chat_id]["name_profile"]
    #     sketch = init_strenght_in[chat_id]["sketch"]
    #     reg_document = init_strenght_in[chat_id]["reg_document"]
    #     num_sides_heated = init_strenght_in[chat_id]["num_sides_heated"]
    #     fixation = init_strenght_in[chat_id]["fixation"]
    #     type_loading = init_strenght_in[chat_id]["type_loading"]
    #     len_elem = init_strenght_in[chat_id]["len_elem"]
    #     type_steel_element = init_strenght_in[chat_id]["type_steel_element"]
    #     loading_method = init_strenght_in[chat_id]["loading_method"]
    #     n_load = init_strenght_in[chat_id]["n_load"]

    # strength_calculation = SteelStrength(i18n=i18n, chat_id=chat_id,
    #                                      name_profile=name_profile,
    #                                      sketch=sketch,
    #                                      reg_document=reg_document,
    #                                      num_sides_heated=num_sides_heated,
    #                                      fixation=fixation,
    #                                      type_loading=type_loading,
    #                                      len_elem=len_elem,
    #                                      n_load=n_load,
    #                                      type_steel_element=type_steel_element,
    #                                      loading_method=loading_method)
    strength_calculation = SteelFireStrength(i18n=i18n, chat_id=chat_id)
    image_png = strength_calculation.get_initial_data_strength()

    # init_strenght_in[chat_id]['n_load'] = n_load

    # with open('app\infrastructure\init_data\init_data_strenght_steel.json', 'w', encoding='utf-8') as file_w:
    #     json.dump(init_strenght_in, file_w,
    #               ensure_ascii=False, indent=4)

    text = i18n.initial_data_steel.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=image_png, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'type_steel_element_edit',
                                      'sides_heated',
                                      'len_elem_edit',
                                      'type_of_load_edit',
                                      'loads_steel_edit',
                                      'type_loading_element',
                                      'fixation_steel',
                                      'back_strength_element', i18n=i18n))
    await state.clear()
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'sides_heated')
async def sides_heated_edit_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = callback.message.chat.id
    text = i18n.num_sides_heated.text()

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(2, 'num_sides_heated_three', 'num_sides_heated_four', 'stop_edit_strength', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['num_sides_heated_two', 'num_sides_heated_three', 'num_sides_heated_four']))
async def type_of_load_edit_in_call(callback: CallbackQuery, state: FSMContext, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    call_data = callback.data

    with open('app\infrastructure\init_data\init_data_strenght_steel.json', encoding='utf-8') as file_op:
        init_strenght_out = json.load(file_op)
    init_strenght_out[chat_id]["num_sides_heated"] = call_data
    with open('app\infrastructure\init_data\init_data_strenght_steel.json', 'w', encoding='utf-8') as file_w:
        json.dump(init_strenght_out, file_w,
                  ensure_ascii=False, indent=4)
    #     name_profile = init_strenght_out[chat_id]["name_profile"]
    #     sketch = init_strenght_out[chat_id]["sketch"]
    #     reg_document = init_strenght_out[chat_id]["reg_document"]
    #     len_elem = init_strenght_out[chat_id]["len_elem"]
    #     fixation = init_strenght_out[chat_id]["fixation"]
    #     type_loading = init_strenght_out[chat_id]["type_loading"]
    #     n_load = init_strenght_out[chat_id]["n_load"]
    #     type_steel_element = init_strenght_out[chat_id]["type_steel_element"]
    #     loading_method = init_strenght_out[chat_id]["loading_method"]

    # strength_calculation = SteelStrength(i18n=i18n, chat_id=chat_id,
    #                                      name_profile=name_profile,
    #                                      sketch=sketch,
    #                                      reg_document=reg_document,
    #                                      fixation=fixation,
    #                                      type_loading=type_loading,
    #                                      len_elem=len_elem,
    #                                      n_load=n_load,
    #                                      type_steel_element=type_steel_element,
    #                                      loading_method=loading_method,
    #                                      num_sides_heated=call_data)
    strength_calculation = SteelFireStrength(i18n=i18n, chat_id=chat_id)
    image_png = strength_calculation.get_initial_data_strength()

    text = i18n.initial_data_steel.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=image_png, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'type_steel_element_edit',
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
    chat_id = str(callback.message.chat.id)
    with open('app\infrastructure\init_data\init_data_strenght_steel.json', encoding='utf-8') as file_op:
        init_strenght_in = json.load(file_op)
        len_elem = init_strenght_in[chat_id]['len_elem']
    text = i18n.len_elem_edit.text(len_elem=len_elem)
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))
    await state.set_state(FSMSteelForm.len_elem_edit_state)
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.len_elem_edit_state), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero']))
async def len_elem_edit_var_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
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
        if len_elem_data.get('len_elem_key') == None:
            await state.update_data(len_elem_key="")
            len_elem_data = await state.get_data()
            await state.update_data(len_elem_key=call_data)
            len_elem_data = await state.get_data()
            len_elem_edit = len_elem_data.get('len_elem_key', 1000)
            text = i18n.len_elem_edit.text(len_elem=len_elem_edit)
        else:
            len_elem_1 = len_elem_data.get('len_elem_key')
            len_elem_sum = str(len_elem_1) + str(call_data)
            await state.update_data(len_elem_key=len_elem_sum)
            len_elem_data = await state.get_data()
            len_elem_edit = len_elem_data.get('len_elem_key', 1000)
            text = i18n.len_elem_edit.text(len_elem=len_elem_edit)

    with open('app\infrastructure\init_data\init_data_strenght_steel.json', encoding='utf-8') as file_op:
        init_strenght_in = json.load(file_op)
    init_strenght_in[chat_id]['len_elem'] = len_elem_edit
    with open('app\infrastructure\init_data\init_data_strenght_steel.json', 'w', encoding='utf-8') as file_w:
        json.dump(init_strenght_in, file_w,
                  ensure_ascii=False, indent=4)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))


@fire_res_router.callback_query(StateFilter(FSMSteelForm.len_elem_edit_state), F.data.in_(['point']))
async def len_elem_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    len_elem_data = await state.get_data()

    call_data = callback.data
    if call_data == "point":
        call_data = '.'

    if len_elem_data.get('len_elem_key') == None:
        await state.update_data(len_elem_key="")
        len_elem_data = await state.get_data()
        await state.update_data(len_elem_key=call_data)
        len_elem_data = await state.get_data()
        len_elem_edit = len_elem_data.get('len_elem_key', 3600)
        text = i18n.len_elem_edit.text(len_elem=len_elem_edit)
    else:
        len_elem_1 = len_elem_data.get('len_elem_key')
        len_elem_sum = str(len_elem_1) + str(call_data)
        await state.update_data(len_elem_key=len_elem_sum)
        len_elem_data = await state.get_data()
        len_elem_edit = len_elem_data.get('len_elem_key', 3600)
        text = i18n.len_elem_edit.text(len_elem=len_elem_edit)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))


@fire_res_router.callback_query(StateFilter(FSMSteelForm.len_elem_edit_state), F.data.in_(['clear']))
async def len_elem_edit_point_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    call_data = callback.data
    len_elem_data = await state.get_data()

    await state.update_data(len_elem_key="")
    len_elem_data = await state.get_data()
    len_elem_edit = len_elem_data.get('len_elem_key', 1000)
    text = i18n.len_elem_edit.text(len_elem=len_elem_edit)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.len_elem_edit_state), F.data.in_(['ready']))
async def len_elem_edit_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    strength_calculation = SteelFireStrength(i18n=i18n, chat_id=chat_id)
    image_png = strength_calculation.get_initial_data_strength()
    text = i18n.initial_data_steel.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=image_png, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'type_steel_element_edit',
                                      'sides_heated',
                                      'len_elem_edit',
                                      'type_of_load_edit',
                                      'loads_steel_edit',
                                      'type_loading_element',
                                      'fixation_steel',
                                      'back_strength_element', i18n=i18n))
    await state.clear()
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'type_of_load_edit')
async def type_of_load_edit_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = callback.message.chat.id
    text = i18n.type_of_load_edit.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(2, 'distributed_load_steel', 'concentrated_load_steel', 'stop_edit_strength', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['distributed_load_steel', 'concentrated_load_steel']))
async def type_of_load_edit_in_call(callback: CallbackQuery, state: FSMContext, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    call_data = callback.data
    with open('app\infrastructure\init_data\init_data_strenght_steel.json', encoding='utf-8') as file_op:
        init_strenght_out = json.load(file_op)
    init_strenght_out[chat_id]["loading_method"] = call_data
    with open('app\infrastructure\init_data\init_data_strenght_steel.json', 'w', encoding='utf-8') as file_w:
        json.dump(init_strenght_out, file_w,
                  ensure_ascii=False, indent=4)
    strength_calculation = SteelFireStrength(i18n=i18n, chat_id=chat_id)
    image_png = strength_calculation.get_initial_data_strength()
    text = i18n.initial_data_steel.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=image_png, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'type_steel_element_edit',
                                      'sides_heated',
                                      'len_elem_edit',
                                      'type_of_load_edit',
                                      'loads_steel_edit',
                                      'type_loading_element',
                                      'fixation_steel',
                                      'back_strength_element', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'fixation_steel')
async def fixation_steel_edit_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = callback.message.chat.id
    text = i18n.consolidation_steel.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'hinge-hinge', 'sealing-sealing', 'seal-hinge', 'console', 'stop_edit_strength', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['hinge-hinge', 'sealing-sealing', 'seal-hinge', 'console']))
async def fixation_steel_edit_in_call(callback: CallbackQuery, state: FSMContext, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    call_data = callback.data
    with open('app\infrastructure\init_data\init_data_strenght_steel.json', encoding='utf-8') as file_op:
        init_strenght_out = json.load(file_op)
    init_strenght_out[chat_id]["fixation"] = call_data
    with open('app\infrastructure\init_data\init_data_strenght_steel.json', 'w', encoding='utf-8') as file_w:
        json.dump(init_strenght_out, file_w,
                  ensure_ascii=False, indent=4)
    #     name_profile = init_strenght_out[chat_id]["name_profile"]
    #     sketch = init_strenght_out[chat_id]["sketch"]
    #     reg_document = init_strenght_out[chat_id]["reg_document"]
    #     num_sides_heated = init_strenght_out[chat_id]["num_sides_heated"]
    #     len_elem = init_strenght_out[chat_id]["len_elem"]
    #     type_loading = init_strenght_out[chat_id]["type_loading"]
    #     n_load = init_strenght_out[chat_id]["n_load"]
    #     type_steel_element = init_strenght_out[chat_id]["type_steel_element"]
    #     loading_method = init_strenght_out[chat_id]["loading_method"]

    # strength_calculation = SteelStrength(i18n=i18n, chat_id=chat_id,
    #                                      name_profile=name_profile,
    #                                      sketch=sketch,
    #                                      reg_document=reg_document,
    #                                      num_sides_heated=num_sides_heated,
    #                                      type_loading=type_loading,
    #                                      len_elem=len_elem,
    #                                      n_load=n_load,
    #                                      type_steel_element=type_steel_element,
    #                                      loading_method=loading_method,
    #                                      fixation=call_data)
    strength_calculation = SteelFireStrength(i18n=i18n, chat_id=chat_id)
    image_png = strength_calculation.get_initial_data_strength()

    text = i18n.initial_data_steel.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=image_png, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'type_steel_element_edit',
                                      'sides_heated',
                                      'len_elem_edit',
                                      'type_of_load_edit',
                                      'loads_steel_edit',
                                      'type_loading_element',
                                      'fixation_steel',
                                      'back_strength_element', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'type_steel_element_edit')
async def type_steel_element_edit_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = callback.message.chat.id
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
async def type_steel_element_in_call(callback: CallbackQuery, state: FSMContext, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    call_data = i18n.get(callback.data)

    with open('app\infrastructure\init_data\init_data_strenght_steel.json', encoding='utf-8') as file_op:
        init_strenght_out = json.load(file_op)
    init_strenght_out[chat_id]["type_steel_element"] = call_data
    with open('app\infrastructure\init_data\init_data_strenght_steel.json', 'w', encoding='utf-8') as file_w:
        json.dump(init_strenght_out, file_w,
                  ensure_ascii=False, indent=4)
    #     name_profile = init_strenght_out[chat_id]["name_profile"]
    #     sketch = init_strenght_out[chat_id]["sketch"]
    #     reg_document = init_strenght_out[chat_id]["reg_document"]
    #     num_sides_heated = init_strenght_out[chat_id]["num_sides_heated"]
    #     len_elem = init_strenght_out[chat_id]["len_elem"]
    #     fixation = init_strenght_out[chat_id]["fixation"]
    #     type_loading = init_strenght_out[chat_id]["type_loading"]
    #     n_load = init_strenght_out[chat_id]["n_load"]
    #     loading_method = init_strenght_out[chat_id]["loading_method"]

    # strength_calculation = SteelStrength(i18n=i18n, chat_id=chat_id,
    #                                      name_profile=name_profile,
    #                                      sketch=sketch,
    #                                      reg_document=reg_document,
    #                                      num_sides_heated=num_sides_heated,
    #                                      fixation=fixation,
    #                                      type_loading=type_loading,
    #                                      len_elem=len_elem,
    #                                      n_load=n_load,
    #                                      loading_method=loading_method,
    #                                      type_steel_element=call_data)
    strength_calculation = SteelFireStrength(i18n=i18n, chat_id=chat_id)
    image_png = strength_calculation.get_initial_data_strength()

    text = i18n.initial_data_steel.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=image_png, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'type_steel_element_edit',
                                      'sides_heated',
                                      'len_elem_edit',
                                      'type_of_load_edit',
                                      'loads_steel_edit',
                                      'type_loading_element',
                                      'fixation_steel',
                                      'back_strength_element', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'ibeam_element')
async def ibeam_element_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
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
async def channel_element_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
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


@fire_res_router.callback_query(F.data == 'type_loading_element')
async def type_loading_element_edit_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = callback.message.chat.id
    text = i18n.type_loading_element.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'stretching_element', 'compression_element', 'bend_element', 'stop_edit_strength', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['stretching_element', 'compression_element', 'bend_element']))
async def stretching_element_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    call_data = callback.data
    with open('app\infrastructure\init_data\init_data_strenght_steel.json', encoding='utf-8') as file_op:
        init_strenght_out = json.load(file_op)
    init_strenght_out[chat_id]["type_loading"] = call_data
    with open('app\infrastructure\init_data\init_data_strenght_steel.json', 'w', encoding='utf-8') as file_w:
        json.dump(init_strenght_out, file_w,
                  ensure_ascii=False, indent=4)
    #     name_profile = init_strenght_out[chat_id]["name_profile"]
    #     sketch = init_strenght_out[chat_id]["sketch"]
    #     reg_document = init_strenght_out[chat_id]["reg_document"]
    #     num_sides_heated = init_strenght_out[chat_id]["num_sides_heated"]
    #     len_elem = init_strenght_out[chat_id]["len_elem"]
    #     n_load = init_strenght_out[chat_id]["n_load"]
    #     type_steel_element = init_strenght_out[chat_id]["type_steel_element"]
    #     loading_method = init_strenght_out[chat_id]["loading_method"]
    #     fixation = init_strenght_out[chat_id]["fixation"]

    # strength_calculation = SteelStrength(i18n=i18n, chat_id=chat_id,
    #                                      name_profile=name_profile,
    #                                      sketch=sketch,
    #                                      reg_document=reg_document,
    #                                      num_sides_heated=num_sides_heated,
    #                                      type_loading=call_data,
    #                                      len_elem=len_elem,
    #                                      n_load=n_load,
    #                                      type_steel_element=type_steel_element,
    #                                      loading_method=loading_method,
    #                                      fixation=fixation)

    strength_calculation = SteelFireStrength(i18n=i18n, chat_id=chat_id)
    image_png = strength_calculation.get_initial_data_strength()
    text = i18n.initial_data_steel.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=image_png, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'type_steel_element_edit',
                                      'sides_heated',
                                      'len_elem_edit',
                                      'type_of_load_edit',
                                      'loads_steel_edit',
                                      'type_loading_element',
                                      'fixation_steel',
                                      'back_strength_element', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['export_data_strength']))
async def export_data_strength_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = callback.message.chat.id
    text = i18n.export_data_strength.text()

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'back_strength_element', 'back_type_calc', i18n=i18n))
    await callback.answer('')
# @fire_res_router.callback_query(F.data == 'export_data_strength')
# async def export_data_strength_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
#     # chat_id = str(callback.message.chat.id)
#     # await callback.message.bot.send_chat_action(
#     #     chat_id=callback.message.chat.id,
#     #     action=ChatAction.UPLOAD_DOCUMENT)
#     # with open('app\infrastructure\init_data\init_data_thermal_steel.json', encoding='utf-8') as file_op:
#     #     init_thermal_in = json.load(file_op)
#     #     mode = init_thermal_in[chat_id]["mode"]
#     #     ptm = init_thermal_in[chat_id]["ptm"]
#     #     t_critic_C = init_thermal_in[chat_id]["t_critic_C"]
#     #     s_0 = init_thermal_in[chat_id]["s_0"]
#     #     s_1 = init_thermal_in[chat_id]["s_1"]
#     #     T_0 = init_thermal_in[chat_id]["T_0"]
#     #     a_convection = init_thermal_in[chat_id]["a_convection"]
#     #     density_steel = init_thermal_in[chat_id]["density_steel"]
#     #     heat_capacity = init_thermal_in[chat_id]["heat_capacity"]
#     #     heat_capacity_change = init_thermal_in[chat_id]["heat_capacity_change"]

#     # t_res = SteelFireResistance(chat_id=chat_id, mode=mode, ptm=ptm, t_critic=t_critic_C, s_0=s_0, s_1=s_1, T_0=T_0, a_convection=a_convection,
#     #                 density_steel=density_steel, heat_capacity=heat_capacity, heat_capacity_change=heat_capacity_change)
#     # text = i18n.export_data_steel.text()
#     # data = t_res.get_data_steel_heating()
#     # file_csv = get_csv_bt_file(data=data)

#     # await bot.edit_message_media(
#     #     chat_id=callback.message.chat.id,
#     #     message_id=callback.message.message_id,
#     #     media=InputMediaDocument(media=BufferedInputFile(
#     #         file=file_csv, filename="data_thermal.csv"), caption=text),
#     #     reply_markup=get_inline_cd_kb(1, 'plot_thermal', 'protocol_thermal', 'forward_type_calc', i18n=i18n))
#     await callback.answer('')


"""



Теплотехнический расчет




"""


@fire_res_router.callback_query(F.data.in_(['thermal_calculation', 'forward_type_calc']))
async def thermal_calculation_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    user_name = str(callback.message.chat.username)
    user_first_name = str(callback.message.chat.first_name)
    user_last_name = str(callback.message.chat.last_name)
    with open('app\infrastructure\init_data\init_data_thermal_steel.json', encoding='utf-8') as file_op:
        init_thermal_in = json.load(file_op)
        if chat_id not in init_thermal_in:
            init_thermal_in[chat_id] = {"user_name": user_name,
                                        "user_first_name": user_first_name,
                                        "user_last_name": user_last_name,
                                        "mode": "Стандартный",
                                        "ptm": 4.8,
                                        "t_critic_C": 500,
                                        "a_convection": 29,
                                        "s_0": 0.850,
                                        "s_1": 0.625,
                                        "T_0": 293,
                                        "xmax": 90,
                                        "density_steel": 7800,
                                        "heat_capacity": 310,
                                        "heat_capacity_change": 0.469,
                                        "time_fsr": 0}
            with open('app\infrastructure\init_data\init_data_thermal_steel.json', 'w', encoding='utf-8') as file_w:
                json.dump(init_thermal_in, file_w,
                          ensure_ascii=False, indent=4)
        mode = init_thermal_in[chat_id]["mode"]
        ptm = init_thermal_in[chat_id]["ptm"]
        s_0 = init_thermal_in[chat_id]["s_0"]
        s_1 = init_thermal_in[chat_id]["s_1"]
        T_0 = init_thermal_in[chat_id]["T_0"]
        a_convection = init_thermal_in[chat_id]["a_convection"]
        density_steel = init_thermal_in[chat_id]["density_steel"]
        heat_capacity = init_thermal_in[chat_id]["heat_capacity"]
        heat_capacity_change = init_thermal_in[chat_id]["heat_capacity_change"]
        t_critic_C = init_thermal_in[chat_id]["t_critic_C"]

    text = i18n.initial_data_steel.text()
    t_res = SteelFireResistance(i18n=i18n, chat_id=chat_id, mode=mode, ptm=ptm, t_critic=t_critic_C, s_0=s_0, s_1=s_1, T_0=T_0, a_convection=a_convection,
                                density_steel=density_steel, heat_capacity=heat_capacity, heat_capacity_change=heat_capacity_change)
    image_png = t_res.get_initial_data_thermal()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=image_png, filename="initial_data_thermal"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_init_data_thermal', 'run_thermal_steel', 'back_type_calc', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['run_thermal_steel', 'plot_thermal']))
async def run_thermal_calculation_call(callback: CallbackQuery, state: FSMContext, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    with open('app\infrastructure\init_data\init_data_thermal_steel.json', encoding='utf-8') as file_op:
        init_thermal_in = json.load(file_op)
        mode = init_thermal_in[chat_id]["mode"]
        ptm = init_thermal_in[chat_id]["ptm"]
        t_critic_C = init_thermal_in[chat_id]["t_critic_C"]
        s_0 = init_thermal_in[chat_id]["s_0"]
        s_1 = init_thermal_in[chat_id]["s_1"]
        T_0 = init_thermal_in[chat_id]["T_0"]
        a_convection = init_thermal_in[chat_id]["a_convection"]
        density_steel = init_thermal_in[chat_id]["density_steel"]
        heat_capacity = init_thermal_in[chat_id]["heat_capacity"]
        heat_capacity_change = init_thermal_in[chat_id]["heat_capacity_change"]

    t_res = SteelFireResistance(i18n=i18n, chat_id=chat_id, mode=mode, ptm=ptm, t_critic=t_critic_C, s_0=s_0, s_1=s_1, T_0=T_0, a_convection=a_convection,
                                density_steel=density_steel, heat_capacity=heat_capacity, heat_capacity_change=heat_capacity_change)

    plot_thermal_png = t_res.get_plot_steel()
    time_fsr = t_res.get_steel_fsr()
    init_thermal_in[chat_id]["time_fsr"] = time_fsr
    with open('app\infrastructure\init_data\init_data_thermal_steel.json', 'w', encoding='utf-8') as file_w:
        json.dump(init_thermal_in, file_w,
                  ensure_ascii=False, indent=4)
    text = i18n.thermal_calculation.text(time_fsr=round(time_fsr, 2))
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=plot_thermal_png, filename="plot_thermal_png"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'strength_calculation', 'protocol_thermal', 'export_data_steel',  'forward_type_calc', 'back_type_calc', i18n=i18n))
    await state.clear()
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'stop_edit_thermal_calc', ~StateFilter(default_state))
async def stop_edit_thermal_calc_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, 'run_thermal_steel', 'edit_init_data_thermal', 'back_type_calc', i18n=i18n))
    await state.clear()
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'back_thermal_calc')
async def back_thermal_calc_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = callback.message.chat.id

    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, 'edit_init_data_thermal', 'run_thermal_steel', 'back_type_calc', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'edit_init_data_thermal')
async def edit_init_data_thermal_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = callback.message.chat.id

    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, 'mode_edit', 'ptm_edit', 't_critic_edit', 'back_thermal_calc', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'mode_edit')
async def mode_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = callback.message.chat.id

    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, 'mode_standard', 'mode_hydrocarbon', 'mode_external', 'mode_smoldering', 'stop_edit_thermal_calc', i18n=i18n))
    await state.set_state(FSMSteelForm.mode_edit_state)
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'ptm_edit')
async def ptm_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)

    with open('app\infrastructure\init_data\init_data_thermal_steel.json', encoding='utf-8') as file_op:
        init_thermal_in = json.load(file_op)
        ptm = init_thermal_in[chat_id]['ptm']

    text = i18n.ptm_edit.text(ptm=round(ptm, 2))

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))

    await state.set_state(FSMSteelForm.ptm_edit_state)
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.ptm_edit_state), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero']))
async def ptm_edit_var_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
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
        if ptm_data.get('ptm_key') == None:
            await state.update_data(ptm_key="")
            ptm_data = await state.get_data()
            await state.update_data(ptm_key=call_data)
            ptm_data = await state.get_data()
            ptm_edit = ptm_data.get('ptm_key', 4.8)
            text = i18n.ptm_edit.text(ptm=ptm_edit)
        else:
            ptm_1 = ptm_data.get('ptm_key')
            ptm_sum = str(ptm_1) + str(call_data)
            await state.update_data(ptm_key=ptm_sum)
            ptm_data = await state.get_data()
            ptm_edit = ptm_data.get('ptm_key', 4.8)
            text = i18n.ptm_edit.text(ptm=ptm_edit)

    with open('app\infrastructure\init_data\init_data_thermal_steel.json', encoding='utf-8') as file_op:
        init_thermal_in = json.load(file_op)
    init_thermal_in[chat_id]['ptm'] = ptm_edit
    with open('app\infrastructure\init_data\init_data_thermal_steel.json', 'w', encoding='utf-8') as file_w:
        json.dump(init_thermal_in, file_w, ensure_ascii=False, indent=4)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))


@fire_res_router.callback_query(StateFilter(FSMSteelForm.ptm_edit_state), F.data.in_(['point']))
async def ptm_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    ptm_data = await state.get_data()

    call_data = callback.data
    if call_data == "point":
        call_data = '.'

    if ptm_data.get('ptm_key') == None:
        await state.update_data(ptm_key="")
        ptm_data = await state.get_data()
        await state.update_data(ptm_key=call_data)
        ptm_data = await state.get_data()
        ptm_edit = ptm_data.get('ptm_key', 4.8)
        text = i18n.ptm_edit.text(ptm=ptm_edit)
    else:
        ptm_1 = ptm_data.get('ptm_key')
        ptm_sum = str(ptm_1) + str(call_data)
        await state.update_data(ptm_key=ptm_sum)
        ptm_data = await state.get_data()
        ptm_edit = ptm_data.get('ptm_key', 4.8)
        text = i18n.ptm_edit.text(ptm=ptm_edit)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))


@fire_res_router.callback_query(StateFilter(FSMSteelForm.ptm_edit_state), F.data.in_(['clear']))
async def ptm_edit_point_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    call_data = callback.data
    ptm_data = await state.get_data()

    await state.update_data(ptm_key="")
    ptm_data = await state.get_data()
    ptm_edit = ptm_data.get('ptm_key', 4.8)
    text = i18n.ptm_edit.text(ptm=ptm_edit)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.ptm_edit_state), F.data.in_(['ready']))
async def ptm_edit_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    with open('app\infrastructure\init_data\init_data_thermal_steel.json', encoding='utf-8') as file_op:
        init_thermal_in = json.load(file_op)
        ptm = init_thermal_in[chat_id]["ptm"]
        mode = init_thermal_in[chat_id]["mode"]
        t_critic_C = init_thermal_in[chat_id]["t_critic_C"]
        s_0 = init_thermal_in[chat_id]["s_0"]
        s_1 = init_thermal_in[chat_id]["s_1"]
        T_0 = init_thermal_in[chat_id]["T_0"]
        a_convection = init_thermal_in[chat_id]["a_convection"]
        density_steel = init_thermal_in[chat_id]["density_steel"]
        heat_capacity = init_thermal_in[chat_id]["heat_capacity"]
        heat_capacity_change = init_thermal_in[chat_id]["heat_capacity_change"]

    t_res = SteelFireResistance(i18n=i18n, chat_id=chat_id, mode=mode, ptm=ptm, t_critic=t_critic_C, s_0=s_0, s_1=s_1, T_0=T_0, a_convection=a_convection,
                                density_steel=density_steel, heat_capacity=heat_capacity, heat_capacity_change=heat_capacity_change)
    text = i18n.initial_data_steel.text()
    image_png = t_res.get_initial_data_thermal()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=image_png, filename="initial_data_thermal"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'mode_edit', 'ptm_edit', 't_critic_edit', 'back_thermal_calc', i18n=i18n))
    await state.clear()
    await callback.answer('')


@fire_res_router.callback_query(F.data == 't_critic_edit')
async def t_critic_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    with open('app\infrastructure\init_data\init_data_thermal_steel.json', encoding='utf-8') as file_op:
        init_thermal_in = json.load(file_op)
        t_critic_C = init_thermal_in[chat_id]['t_critic_C']
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
    chat_id = str(callback.message.chat.id)

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
        if t_data.get('t_key') == None:
            await state.update_data(t_key="")
            t_data = await state.get_data()
            await state.update_data(t_key=call_data)
            t_data = await state.get_data()
            t_edit = t_data.get('t_key', 500)
            text = i18n.t_critic_edit.text(t_critic=t_edit)
        else:
            t_1 = t_data.get('t_key')
            t_sum = str(t_1) + str(call_data)
            await state.update_data(t_key=t_sum)
            t_data = await state.get_data()
            t_edit = t_data.get('t_key', 500)
            text = i18n.t_critic_edit.text(t_critic=t_edit)
    elif call_data == "clear":
        await state.update_data(t_key="")
        t_data = await state.get_data()
        t_edit = t_data.get('t_key', 500)
        text = i18n.t_critic_edit.text(t_critic=t_edit)

    with open('app\infrastructure\init_data\init_data_thermal_steel.json', encoding='utf-8') as file_op:
        init_thermal_in = json.load(file_op)
    init_thermal_in[chat_id]['t_critic_C'] = t_edit
    with open('app\infrastructure\init_data\init_data_thermal_steel.json', 'w', encoding='utf-8') as file_w:
        json.dump(init_thermal_in, file_w, ensure_ascii=False, indent=4)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.t_critic_edit_state), F.data.in_(['ready']))
async def t_critic_edit_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    with open('app\infrastructure\init_data\init_data_thermal_steel.json', encoding='utf-8') as file_op:
        init_thermal_in = json.load(file_op)
        ptm = init_thermal_in[chat_id]["ptm"]
        mode = init_thermal_in[chat_id]["mode"]
        t_critic_C = init_thermal_in[chat_id]["t_critic_C"]
        s_0 = init_thermal_in[chat_id]["s_0"]
        s_1 = init_thermal_in[chat_id]["s_1"]
        T_0 = init_thermal_in[chat_id]["T_0"]
        a_convection = init_thermal_in[chat_id]["a_convection"]
        density_steel = init_thermal_in[chat_id]["density_steel"]
        heat_capacity = init_thermal_in[chat_id]["heat_capacity"]
        heat_capacity_change = init_thermal_in[chat_id]["heat_capacity_change"]

    t_res = SteelFireResistance(i18n=i18n, chat_id=chat_id, mode=mode, ptm=ptm, t_critic=t_critic_C, s_0=s_0, s_1=s_1, T_0=T_0, a_convection=a_convection,
                                density_steel=density_steel, heat_capacity=heat_capacity, heat_capacity_change=heat_capacity_change)
    text = i18n.initial_data_steel.text()

    image_png = t_res.get_initial_data_thermal()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=image_png, filename="initial_data_thermal"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'mode_edit', 'ptm_edit', 't_critic_edit', 'back_thermal_calc', i18n=i18n))
    await state.clear()
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.mode_edit_state), F.data.in_(['mode_standard', 'mode_hydrocarbon', 'mode_external', 'mode_smoldering']))
async def mode_edit_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    mode = str(i18n.get(callback.data))
    with open('app\infrastructure\init_data\init_data_thermal_steel.json', encoding='utf-8') as file_op:
        init_thermal_in = json.load(file_op)
        init_thermal_in[chat_id]['mode'] = mode
        ptm = init_thermal_in[chat_id]['ptm']
        t_critic_C = init_thermal_in[chat_id]["t_critic_C"]
        s_0 = init_thermal_in[chat_id]["s_0"]
        s_1 = init_thermal_in[chat_id]["s_1"]
        T_0 = init_thermal_in[chat_id]["T_0"]
        a_convection = init_thermal_in[chat_id]["a_convection"]
        density_steel = init_thermal_in[chat_id]["density_steel"]
        heat_capacity = init_thermal_in[chat_id]["heat_capacity"]
        heat_capacity_change = init_thermal_in[chat_id]["heat_capacity_change"]

    with open('app\infrastructure\init_data\init_data_thermal_steel.json', 'w', encoding='utf-8') as file_w:
        json.dump(init_thermal_in, file_w, ensure_ascii=False, indent=4)

    t_res = SteelFireResistance(i18n=i18n, chat_id=chat_id, mode=mode, ptm=ptm, t_critic=t_critic_C, s_0=s_0, s_1=s_1, T_0=T_0, a_convection=a_convection,
                                density_steel=density_steel, heat_capacity=heat_capacity, heat_capacity_change=heat_capacity_change)
    text = i18n.edit_init_data_thermal.text()

    image_png = t_res.get_initial_data_thermal()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=image_png, filename="initial_data_thermal"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'mode_edit', 'ptm_edit', 't_critic_edit', 'back_thermal_calc', i18n=i18n))
    await state.clear()
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'protocol_thermal')
async def protocol_thermal_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.protocol_thermal.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'export_data_steel', 'forward_type_calc',  i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'export_data_steel')
async def export_data_steel_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    with open('app\infrastructure\init_data\init_data_thermal_steel.json', encoding='utf-8') as file_op:
        init_thermal_in = json.load(file_op)
        mode = init_thermal_in[chat_id]["mode"]
        ptm = init_thermal_in[chat_id]["ptm"]
        t_critic_C = init_thermal_in[chat_id]["t_critic_C"]
        s_0 = init_thermal_in[chat_id]["s_0"]
        s_1 = init_thermal_in[chat_id]["s_1"]
        T_0 = init_thermal_in[chat_id]["T_0"]
        a_convection = init_thermal_in[chat_id]["a_convection"]
        density_steel = init_thermal_in[chat_id]["density_steel"]
        heat_capacity = init_thermal_in[chat_id]["heat_capacity"]
        heat_capacity_change = init_thermal_in[chat_id]["heat_capacity_change"]

    t_res = SteelFireResistance(i18n=i18n, chat_id=chat_id, mode=mode, ptm=ptm, t_critic=t_critic_C, s_0=s_0, s_1=s_1, T_0=T_0, a_convection=a_convection,
                                density_steel=density_steel, heat_capacity=heat_capacity, heat_capacity_change=heat_capacity_change)
    text = i18n.export_data_steel.text()
    data = t_res.get_data_steel_heating()
    file_csv = get_csv_bt_file(data=data)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaDocument(media=BufferedInputFile(
            file=file_csv, filename="data_thermal.csv"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'plot_thermal', 'forward_type_calc', i18n=i18n))
    await callback.answer('')
