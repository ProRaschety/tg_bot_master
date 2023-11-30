import logging

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message, FSInputFile, InputMediaPhoto, InputFile
from aiogram.utils.chat_action import ChatActionSender
from aiogram.enums import ChatAction

from fluentogram import TranslatorRunner

from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb
from app.tg_bot.utilities.misc_utils import get_temp_folder
from app.tg_bot.states.fsm_state_data import FSMSteelForm
from app.calculation.fire_resistance.steel_calculation import SteelFR

import json

logger = logging.getLogger(__name__)
logger = logging.getLogger('matplotlib').setLevel(logging.ERROR)
logger = logging.getLogger('PIL.PngImagePlugin').setLevel(logging.ERROR)


fire_res_router = Router()


@fire_res_router.callback_query(F.data == 'fire_resistance')
async def fire_resistance_call(callback_data: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    await callback_data.message.bot.send_chat_action(
        chat_id=callback_data.message.chat.id,
        action=ChatAction.TYPING)

    text = i18n.fire_resistance.text()
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        steel_photo_id = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    await callback_data.message.answer_photo(
        photo=steel_photo_id,
        caption=text,
        has_spoiler=False,
        reply_markup=get_inline_cd_kb(1, 'steel_element', 'wood_element', 'concrete_element', 'general_menu', i18n=i18n))

    await callback_data.answer('')
    await callback_data.message.delete()


@fire_res_router.callback_query(F.data == 'stop_edit_thermal_calc', ~StateFilter(default_state))
async def stop_edit_thermal_calc_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, 'edit_init_data_thermal', 'run_thermal_steel', 'back_type_calc', i18n=i18n))
    await state.clear()
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'back_type_material')
async def back_type_material_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.fire_resistance.text()
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        media = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(1, 'steel_element', 'wood_element', 'concrete_element', 'general_menu', i18n=i18n))

    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['back_type_calc', 'forward_type_calc']))
async def back_type_calc_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.type_of_calculation_steel.text()
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        media = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(1, 'fire_protection',  'strength_calculation', 'thermal_calculation', 'back_type_material', i18n=i18n))

    await callback.answer('')


@fire_res_router.callback_query(F.data == 'back_thermal_calc')
async def back_thermal_calc_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = callback.message.chat.id

    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, 'edit_init_data_thermal', 'run_thermal_steel', 'back_type_calc', i18n=i18n))
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'steel_element')
async def steel_element_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.type_of_calculation_steel.text()
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        media = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(1, 'fire_protection',  'strength_calculation', 'thermal_calculation', 'back_type_material', i18n=i18n))

    await callback.answer('')


@fire_res_router.callback_query(F.data == 'wood_element')
async def wood_element_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        steel_photo_id = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    text = i18n.type_of_calculation_wood.text()

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=steel_photo_id, caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_type_material', i18n=i18n))

    await callback.answer('')


@fire_res_router.callback_query(F.data == 'concrete_element')
async def concrete_element_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        steel_photo_id = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    text = i18n.type_of_calculation_concrete.text()

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=steel_photo_id, caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_type_material', i18n=i18n))

    await callback.answer('')


@fire_res_router.callback_query(F.data == 'fire_protection')
async def fire_protection_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        steel_photo_id = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    text = i18n.fire_protection.text()

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=steel_photo_id, caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_type_calc', i18n=i18n))

    await callback.answer('')


@fire_res_router.callback_query(F.data == 'strength_calculation')
async def strength_calculation_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        media = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    # chat_id = callback.message.chat.id
    # nm = SteelFR(chat_id=chat_id, mode='Углеводородный')
    # name_dir = nm.get_initial_data_strength()
    # media = FSInputFile(str(name_dir))

    text = i18n.strength_calculation.text()

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(2, 'back_type_calc', i18n=i18n))
    # reply_markup=get_inline_cd_kb(2, 'edit_init_data_strength', 'run_strength_steel', 'back_type_calc', i18n=i18n))

    await callback.answer('')


@fire_res_router.callback_query(F.data == 'thermal_calculation')
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
                                        "t_critic": 500,
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
        t_critic = init_thermal_in[chat_id]["t_critic"]
        s_0 = init_thermal_in[chat_id]["s_0"]
        s_1 = init_thermal_in[chat_id]["s_1"]
        T_0 = init_thermal_in[chat_id]["T_0"]
        a_convection = init_thermal_in[chat_id]["a_convection"]
        density_steel = init_thermal_in[chat_id]["density_steel"]
        heat_capacity = init_thermal_in[chat_id]["heat_capacity"]
        heat_capacity_change = init_thermal_in[chat_id]["heat_capacity_change"]

    t_res = SteelFR(chat_id=chat_id, mode=mode, ptm=ptm, t_critic=t_critic, s_0=s_0, s_1=s_1, T_0=T_0, a_convection=a_convection,
                    density_steel=density_steel, heat_capacity=heat_capacity, heat_capacity_change=heat_capacity_change)
    name_dir = t_res.get_initial_data_thermal()
    media = FSInputFile(str(name_dir))

    text = i18n.initial_data_steel.text()

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(2, 'edit_init_data_thermal', 'run_thermal_steel', 'back_type_calc', i18n=i18n))

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

    text = i18n.ptm_edit.text(ptm=ptm)

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
    call_data = callback.data
    ptm_data = await state.get_data()
    ptm_edit = ptm_data.get('ptm_key', 4.8)

    with open('app\infrastructure\init_data\init_data_thermal_steel.json', encoding='utf-8') as file_op:
        init_thermal_in = json.load(file_op)
        # ptm = init_thermal_in[chat_id]["ptm"]
        ptm = ptm_edit
        mode = init_thermal_in[chat_id]["mode"]
        t_critic = init_thermal_in[chat_id]["t_critic"]
        s_0 = init_thermal_in[chat_id]["s_0"]
        s_1 = init_thermal_in[chat_id]["s_1"]
        T_0 = init_thermal_in[chat_id]["T_0"]
        a_convection = init_thermal_in[chat_id]["a_convection"]
        density_steel = init_thermal_in[chat_id]["density_steel"]
        heat_capacity = init_thermal_in[chat_id]["heat_capacity"]
        heat_capacity_change = init_thermal_in[chat_id]["heat_capacity_change"]

    init_thermal_in[chat_id]['ptm'] = ptm
    with open('app\infrastructure\init_data\init_data_thermal_steel.json', 'w', encoding='utf-8') as file_w:
        json.dump(init_thermal_in, file_w, ensure_ascii=False, indent=4)

    t_res = SteelFR(chat_id=chat_id, mode=mode, ptm=ptm, t_critic=t_critic, s_0=s_0, s_1=s_1, T_0=T_0, a_convection=a_convection,
                    density_steel=density_steel, heat_capacity=heat_capacity, heat_capacity_change=heat_capacity_change)
    name_dir = t_res.get_initial_data_thermal()
    media = FSInputFile(str(name_dir))

    text = i18n.initial_data_steel.text()

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(2, 'edit_init_data_thermal', 'run_thermal_steel', 'back_type_calc', i18n=i18n))
    await state.clear()
    await callback.answer('')


@fire_res_router.callback_query(F.data == 't_critic_edit')
async def t_critic_edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)

    with open('app\infrastructure\init_data\init_data_thermal_steel.json', encoding='utf-8') as file_op:
        init_thermal_in = json.load(file_op)
        t_critic = init_thermal_in[chat_id]['t_critic']

    text = i18n.t_critic_edit.text(t_critic=t_critic)

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
    init_thermal_in[chat_id]['t_critic'] = t_edit
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
        t_critic = init_thermal_in[chat_id]["t_critic"]
        s_0 = init_thermal_in[chat_id]["s_0"]
        s_1 = init_thermal_in[chat_id]["s_1"]
        T_0 = init_thermal_in[chat_id]["T_0"]
        a_convection = init_thermal_in[chat_id]["a_convection"]
        density_steel = init_thermal_in[chat_id]["density_steel"]
        heat_capacity = init_thermal_in[chat_id]["heat_capacity"]
        heat_capacity_change = init_thermal_in[chat_id]["heat_capacity_change"]

    # with open('app\infrastructure\init_data\init_data_thermal_steel.json', 'w', encoding='utf-8') as file_w:
    #     json.dump(init_thermal_in, file_w, ensure_ascii=False, indent=4)

    t_res = SteelFR(chat_id=chat_id, mode=mode, ptm=ptm, t_critic=t_critic, s_0=s_0, s_1=s_1, T_0=T_0, a_convection=a_convection,
                    density_steel=density_steel, heat_capacity=heat_capacity, heat_capacity_change=heat_capacity_change)
    name_dir = t_res.get_initial_data_thermal()
    media = FSInputFile(str(name_dir))

    text = i18n.initial_data_steel.text()

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(2, 'edit_init_data_thermal', 'run_thermal_steel', 'back_type_calc', i18n=i18n))
    await state.clear()
    await callback.answer('')


@fire_res_router.callback_query(StateFilter(FSMSteelForm.mode_edit_state), F.data.in_(['mode_standard', 'mode_hydrocarbon', 'mode_external', 'mode_smoldering']))
async def mode_edit_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    mode = str(i18n.get(callback.data))

    # нужно сохранить выбор режима и внести в БД
    with open('app\infrastructure\init_data\init_data_thermal_steel.json', encoding='utf-8') as file_op:
        init_thermal_in = json.load(file_op)
        init_thermal_in[chat_id]['mode'] = mode
        ptm = init_thermal_in[chat_id]['ptm']
        t_critic = init_thermal_in[chat_id]["t_critic"]
        s_0 = init_thermal_in[chat_id]["s_0"]
        s_1 = init_thermal_in[chat_id]["s_1"]
        T_0 = init_thermal_in[chat_id]["T_0"]
        a_convection = init_thermal_in[chat_id]["a_convection"]
        density_steel = init_thermal_in[chat_id]["density_steel"]
        heat_capacity = init_thermal_in[chat_id]["heat_capacity"]
        heat_capacity_change = init_thermal_in[chat_id]["heat_capacity_change"]

    with open('app\infrastructure\init_data\init_data_thermal_steel.json', 'w', encoding='utf-8') as file_w:
        json.dump(init_thermal_in, file_w, ensure_ascii=False, indent=4)

    t_res = SteelFR(chat_id=chat_id, mode=mode, ptm=ptm, t_critic=t_critic, s_0=s_0, s_1=s_1, T_0=T_0, a_convection=a_convection,
                    density_steel=density_steel, heat_capacity=heat_capacity, heat_capacity_change=heat_capacity_change)
    name_dir = t_res.get_initial_data_thermal()
    media = FSInputFile(str(name_dir))

    text = i18n.edit_init_data_thermal.text()

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(2, 'edit_init_data_thermal', 'run_thermal_steel', 'back_type_calc', i18n=i18n))
    await state.clear()
    await callback.answer('')


@fire_res_router.callback_query(F.data.in_(['run_thermal_steel']))
async def run_thermal_calculation_call(callback: CallbackQuery, state: FSMContext, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    with open('app\infrastructure\init_data\init_data_thermal_steel.json', encoding='utf-8') as file_op:
        init_thermal_in = json.load(file_op)
        mode = init_thermal_in[chat_id]["mode"]
        ptm = init_thermal_in[chat_id]["ptm"]
        t_critic = init_thermal_in[chat_id]["t_critic"]
        s_0 = init_thermal_in[chat_id]["s_0"]
        s_1 = init_thermal_in[chat_id]["s_1"]
        T_0 = init_thermal_in[chat_id]["T_0"]
        a_convection = init_thermal_in[chat_id]["a_convection"]
        density_steel = init_thermal_in[chat_id]["density_steel"]
        heat_capacity = init_thermal_in[chat_id]["heat_capacity"]
        heat_capacity_change = init_thermal_in[chat_id]["heat_capacity_change"]

    t_res = SteelFR(chat_id=chat_id, mode=mode, ptm=ptm, t_critic=t_critic, s_0=s_0, s_1=s_1, T_0=T_0, a_convection=a_convection,
                    density_steel=density_steel, heat_capacity=heat_capacity, heat_capacity_change=heat_capacity_change)

    name_dir = t_res.get_plot_steel()

    time_fsr = t_res.get_steel_fsr()

    init_thermal_in[chat_id]["time_fsr"] = time_fsr
    with open('app\infrastructure\init_data\init_data_thermal_steel.json', 'w', encoding='utf-8') as file_w:
        json.dump(init_thermal_in, file_w,
                  ensure_ascii=False, indent=4)

    media = FSInputFile(str(name_dir))
    text = i18n.thermal_calculation.text(time_fsr=round(time_fsr, 1))

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(1, 'protocol_thermal', 'forward_type_calc', i18n=i18n))
    await state.clear()
    await callback.answer('')


@fire_res_router.callback_query(F.data == 'plot_thermal')
async def plot_thermal_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    directory = get_temp_folder()
    name_plot = "_".join(['fig_steel_fr', str(chat_id), '.png'])
    name_dir = '/'.join([directory, name_plot])
    media = FSInputFile(str(name_dir))
    text = i18n.plot_thermal.text()

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(1, 'protocol_thermal', 'forward_type_calc', i18n=i18n))

    await callback.answer('')


@fire_res_router.callback_query(F.data == 'protocol_thermal')
async def protocol_thermal_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        steel_photo_id = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    text = i18n.protocol_thermal.text()

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=steel_photo_id, caption=text),
        reply_markup=get_inline_cd_kb(1, 'plot_thermal', 'export_data_steel', 'forward_type_calc', i18n=i18n))

    await callback.answer('')


@fire_res_router.callback_query(F.data == 'export_data_steel')
async def export_data_steel_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    with open(file="app/infrastructure/data_base/db_task_photo.json", mode="r", encoding='utf-8') as file_op:
        db_steel_photo_in = json.load(file_op)
        steel_photo_id = db_steel_photo_in["fire_resistance"][0]["steel_photo_id"]

    text = i18n.export_data_steel.text()

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=steel_photo_id, caption=text),
        reply_markup=get_inline_cd_kb(1, 'plot_thermal', 'protocol_thermal', 'forward_type_calc', i18n=i18n))

    await callback.answer('')
