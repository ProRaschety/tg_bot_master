import logging
import itertools

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
# , InlineQueryResultArticle, InputTextMessageContent
# from aiogram.types import InlineQuery
from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaPhoto

from fluentogram import TranslatorRunner

# from app.infrastructure.database.database.db import DB
from app.tg_bot.models.role import UserRole
from app.tg_bot.filters.filter_role import IsGuest
from app.tg_bot.utilities.misc_utils import get_picture_filling, get_data_table
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb
from app.tg_bot.states.fsm_state_data import FSMFireRiskForm
from app.calculation.qra_mode.fire_risk_calculator import FireRisk

log = logging.getLogger(__name__)

fire_risk_router = Router()
fire_risk_router.message.filter(IsGuest())
fire_risk_router.callback_query.filter(IsGuest())

SFilter_pub = [FSMFireRiskForm.edit_time_presence_pub,
               FSMFireRiskForm.edit_probity_evac_pub, FSMFireRiskForm.edit_fire_freq_pub]

kb_pub = [4, 'fire_freq_pub', 'time_presence_pub', 'probity_evac_pub',
          'k_efs_pub', 'k_alarm_pub', 'k_evacuation_pub', 'k_smoke_pub']


SFilter_ind = [
    # FSMFireRiskForm.edit_fire_freq_ind,
    FSMFireRiskForm.edit_time_presence_ind,
    FSMFireRiskForm.edit_probity_evac_ind, FSMFireRiskForm.edit_area_ind, FSMFireRiskForm.edit_work_days_ind,
    FSMFireRiskForm.edit_time_blocking_paths_ind, FSMFireRiskForm.edit_time_start_evacuation_ind, FSMFireRiskForm.edit_time_evacuation_ind]

# kb_ind = [4, 'fire_freq_ind', 'time_presence_ind', 'working_days_per_year_ind',
#           'time_start_evacuation_ind', 'time_blocking_paths_ind', 'time_evacuation_ind', 'probity_evac_ind', 'emergency_escape_ind',
#           'k_efs_ind', 'k_alarm_ind', 'k_evacuation_ind', 'k_smoke_ind']


@fire_risk_router.callback_query(F.data == 'fire_risks')
async def fire_risks_call(callback_data: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.fire_risks.text()
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'fire_model', 'fire_risks_calculator', 'typical_accidents', 'general_menu', i18n=i18n))
    await callback_data.answer('')


@fire_risk_router.callback_query(F.data == 'back_fire_risks')
async def back_fire_risks_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.fire_risks.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'fire_model',
                                      'fire_risks_calculator',
                                      'typical_accidents',
                                      'general_menu', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['fire_risks_calculator', 'back_fire_risks_calc']))
async def fire_risks_calculator_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.fire_risks_calculator.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'public', 'industrial', 'back_fire_risks', i18n=i18n))
    await callback.answer('')

"""______________________Общественные_здания______________________"""


@fire_risk_router.callback_query(F.data.in_(['public', 'back_public']))
async def public_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    state_data = await state.get_state()
    data = await state.get_data()
    data.setdefault("edit_public_param", "0")
    data.setdefault("area_pub", "10")
    data.setdefault("fire_freq_pub", "0.04")
    data.setdefault("time_presence_pub", "2.0")
    data.setdefault("probity_evacuation_pub", "0.999")
    data.setdefault("time_evacuation_pub", "5.0")
    data.setdefault("time_blocking_paths_pub", "10")
    data.setdefault("time_crowding_pub", "1.0")
    data.setdefault("time_start_evacuation_pub", "1.0")
    data.setdefault("k_efs_pub", "0.9")
    data.setdefault("k_alarm_pub", "0.8")
    data.setdefault("k_evacuation_pub", "0.8")
    data.setdefault("k_smoke_pub", "0.8")

    text = i18n.public.text()

    if state_data == FSMFireRiskForm.edit_probity_evac_pub:
        frisk = FireRisk(type_obj='public', prob_evac=True)
    else:
        frisk = FireRisk(type_obj='public')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        # reply_markup=get_inline_cd_kb(1, 'edit_public', 'run_public', 'back_fire_risks_calc', i18n=i18n))
        reply_markup=get_inline_cd_kb(1, 'edit_public', 'run_public', i18n=i18n, param_back=True, back_data='back_fire_risks_calc', check_role=True, role=role))
    await state.update_data(data)
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['run_public', 'run_public_guest']))
async def run_public_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'edit_public', i18n=i18n, param_back=True, back_data='back_fire_risks_calc', check_role=True, role=role))

    state_data = await state.get_state()
    data = await state.get_data()
    data.setdefault("fire_freq_pub", "0.04")
    data.setdefault("k_efs_pub", "0.9")
    data.setdefault("time_presence_pub", "2.0")
    data.setdefault("probity_evacuation_pub", "0.999")
    data.setdefault("time_evacuation_pub", "5.0")
    data.setdefault("time_blocking_paths_pub", "10")
    data.setdefault("time_crowding_pub", "1.0")
    data.setdefault("time_start_evacuation_pub", "1.0")
    data.setdefault("k_alarm_pub", "0.8")
    data.setdefault("k_evacuation_pub", "0.8")
    data.setdefault("k_smoke_pub", "0.8")

    if state_data == FSMFireRiskForm.edit_probity_evac_pub:
        frisk = FireRisk(type_obj='public', prob_evac=True)
    else:
        frisk = FireRisk(type_obj='public')
    data_out, headers, label, ind_risk = frisk.get_result_data(**data)
    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=9)
    if ind_risk > 0.000001:
        text = i18n.public_excess.text()
    else:
        text = i18n.public_not_exceed.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        # reply_markup=get_inline_cd_kb(1, 'edit_public', 'back_fire_risks_calc', i18n=i18n))
        reply_markup=get_inline_cd_kb(1, 'edit_public', i18n=i18n, param_back=True, back_data='back_fire_risks_calc', check_role=True, role=role))
    await state.update_data(data)
    await state.set_state(state=None)


@fire_risk_router.callback_query(F.data.in_(['edit_public', 'edit_public_guest', 'stop_edit_public']))
async def edit_public_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(*kb_pub, i18n=i18n, param_back=True, back_data='back_public', check_role=True, role=role))


@fire_risk_router.callback_query(F.data.in_(['fire_freq_pub', 'time_presence_pub', 'probity_evac_pub']))
async def edit_pub_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    if callback.data == 'fire_freq_pub':
        await state.set_state(FSMFireRiskForm.edit_fire_freq_pub)
    elif callback.data == 'time_presence_pub':
        await state.set_state(FSMFireRiskForm.edit_time_presence_pub)
    elif callback.data == 'probity_evac_pub':
        await state.set_state(FSMFireRiskForm.edit_probity_evac_pub)

    data = await state.get_data()
    state_data = await state.get_state()

    if state_data == FSMFireRiskForm.edit_time_presence_pub:
        text = i18n.edit_public.text(public_param=i18n.get(
            "name_time_presence_pub"), edit_public=data.get("time_presence_pub", 0))
    elif state_data == FSMFireRiskForm.edit_probity_evac_pub:
        text = i18n.edit_public.text(public_param=i18n.get(
            "name_probity_evac_pub"), edit_public=data.get("probity_evacuation_pub", 0))
    elif state_data == FSMFireRiskForm.edit_fire_freq_pub:
        text = i18n.edit_public.text(public_param=i18n.get(
            "name_fire_freq_pub"), edit_public=data.get("fire_freq_pub", 0))
    else:
        text = i18n.edit_public.text(
            public_param='Тут будет текст', edit_area=data.get("edit_public_param", 0))
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(StateFilter(*SFilter_pub),
                                 F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'dooble_zero', 'point', 'clear']))
async def edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    if state_data == FSMFireRiskForm.edit_time_presence_pub:
        public_param = i18n.get("name_time_presence_pub")
    elif state_data == FSMFireRiskForm.edit_probity_evac_pub:
        public_param = i18n.get("name_probity_evac_pub")
    elif state_data == FSMFireRiskForm.edit_fire_freq_pub:
        public_param = i18n.get("name_fire_freq_pub")

    edit_data = await state.get_data()
    if callback.data == 'clear':
        await state.update_data(edit_public_param="")
        edit_d = await state.get_data()
        edit_data = edit_d.get('edit_public_param', 1)
        text = i18n.edit_public.text(
            public_param=public_param, edit_public=edit_data)

    else:
        edit_param_1 = edit_data.get('edit_public_param')
        edit_sum = edit_param_1 + i18n.get(callback.data)
        await state.update_data(edit_public_param=edit_sum)
        edit_data = await state.get_data()
        edit_param = edit_data.get('edit_public_param', 0)
        text = i18n.edit_public.text(
            public_param=public_param, edit_public=edit_param)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready', i18n=i18n))


@fire_risk_router.callback_query(StateFilter(*SFilter_pub), F.data.in_(['ready']))
async def edit_public_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    data = await state.get_data()
    value = data.get("edit_public_param")
    if state_data == FSMFireRiskForm.edit_time_presence_pub:
        if value != '' and value != '.':
            await state.update_data(time_presence_pub=value)
        else:
            await state.update_data(time_presence_pub=0)
    elif state_data == FSMFireRiskForm.edit_probity_evac_pub:
        if value != '' and value != '.' and (float(value)) < 1:
            await state.update_data(probity_evacuation_pub=value)
        else:
            await state.update_data(probity_evacuation_pub=0.999)
    elif state_data == FSMFireRiskForm.edit_fire_freq_pub:
        if value != '' and value != '.':
            await state.update_data(fire_freq_pub=value)
        else:
            await state.update_data(fire_freq_pub=0.04)
    else:
        await state.update_data(edit_public_param=value)
    data = await state.get_data()
    text = i18n.public.text()
    if state_data == FSMFireRiskForm.edit_probity_evac_pub:
        frisk = FireRisk(type_obj='public', prob_evac=True)
    else:
        frisk = FireRisk(type_obj='public')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*kb_pub, i18n=i18n, param_back=True, back_data='back_public'))
    await state.update_data(edit_public_param='')
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_efs_pub']))
async def k_efs_pub_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, 'k_efs_pub_true', 'k_efs_pub_false', 'stop_edit_public', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_alarm_pub']))
async def k_alarm_pub_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, 'k_alarm_pub_true', 'k_alarm_pub_false', 'stop_edit_public', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_evacuation_pub']))
async def k_evacuation_pub_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, 'k_evacuation_pub_true', 'k_evacuation_pub_false', 'stop_edit_public', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_smoke_pub']))
async def k_smoke_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, 'k_smoke_pub_true', 'k_smoke_pub_false', 'stop_edit_public', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_efs_pub_true', 'k_efs_pub_false']))
async def k_efs_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    call_data = callback.data
    # data = await state.get_data()
    if call_data == 'k_efs_pub_true':
        await state.update_data(k_efs_pub=0.9)
    elif call_data == 'k_efs_pub_false':
        await state.update_data(k_efs_pub=0.0)
    data = await state.get_data()
    text = i18n.public.text()
    if state_data == FSMFireRiskForm.edit_probity_evac_pub:
        frisk = FireRisk(type_obj='public', prob_evac=True)
    else:
        frisk = FireRisk(type_obj='public')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*kb_pub, i18n=i18n, param_back=True, back_data='back_public'))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_alarm_pub_true', 'k_alarm_pub_false']))
async def k_alarm_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    call_data = callback.data
    # data = await state.get_data()
    if call_data == 'k_alarm_pub_true':
        await state.update_data(k_alarm_pub=0.8)
    elif call_data == 'k_alarm_pub_false':
        await state.update_data(k_alarm_pub=0.0)
    data = await state.get_data()
    text = i18n.public.text()
    if state_data == FSMFireRiskForm.edit_probity_evac_pub:
        frisk = FireRisk(type_obj='public', prob_evac=True)
    else:
        frisk = FireRisk(type_obj='public')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*kb_pub, i18n=i18n, param_back=True, back_data='back_public'))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_evacuation_pub_true', 'k_evacuation_pub_false']))
async def k_evacuation_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    call_data = callback.data
    # data = await state.get_data()
    if call_data == 'k_evacuation_pub_true':
        await state.update_data(k_evacuation_pub=0.8)
    elif call_data == 'k_evacuation_pub_false':
        await state.update_data(k_evacuation_pub=0.0)
    data = await state.get_data()
    text = i18n.public.text()
    if state_data == FSMFireRiskForm.edit_probity_evac_pub:
        frisk = FireRisk(type_obj='public', prob_evac=True)
    else:
        frisk = FireRisk(type_obj='public')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*kb_pub, i18n=i18n, param_back=True, back_data='back_public'))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_smoke_pub_true', 'k_smoke_pub_false']))
async def k_smoke_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    call_data = callback.data
    # data = await state.get_data()
    if call_data == 'k_smoke_pub_true':
        await state.update_data(k_smoke_pub=0.8)
    elif call_data == 'k_smoke_pub_false':
        await state.update_data(k_smoke_pub=0.0)
    data = await state.get_data()
    text = i18n.public.text()
    if state_data == FSMFireRiskForm.edit_probity_evac_pub:
        frisk = FireRisk(type_obj='public', prob_evac=True)
    else:
        frisk = FireRisk(type_obj='public')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*kb_pub, i18n=i18n, param_back=True, back_data='back_public'))
    await callback.answer('')


"""______________________Производственные_здания______________________"""


@fire_risk_router.callback_query(F.data.in_(['industrial', 'industrial_from_table', 'back_industrial']))
async def industrial_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'edit_industrial', 'run_industrial', i18n=i18n, param_back=True, back_data='back_fire_risks_calc'))

    state_data = await state.get_state()
    data = await state.get_data()
    data.setdefault("edit_industrial_param", "0")
    # data.setdefault("area_ind", "100.0")
    data.setdefault("edit_area_to_frequency", "1")
    data.setdefault("fire_freq_ind", "0.04")
    data.setdefault("k_efs_ind", "0.9")
    data.setdefault("time_presence_ind", "2.0")
    data.setdefault("probity_evacuation_ind", "0.999")
    data.setdefault("time_evacuation_ind", "300")
    data.setdefault("time_blocking_paths_ind", "600")
    data.setdefault("time_start_evacuation_ind", "30")
    data.setdefault("k_alarm_ind", "0.8")
    data.setdefault("k_evacuation_ind", "0.8")
    data.setdefault("k_smoke_ind", "0.8")
    data.setdefault("working_days_per_year_ind", "247")
    data.setdefault("emergency_escape_ind", "0.001")
    data.setdefault("fire_frequency_industrial", "0.04")

    text = i18n.industrial.text()
    # frisk = FireRisk(type_obj='industrial')
    if state_data == FSMFireRiskForm.edit_probity_evac_ind:
        frisk = FireRisk(type_obj='industrial', prob_evac=True)
    else:
        frisk = FireRisk(type_obj='industrial')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_industrial', 'run_industrial', i18n=i18n, param_back=True, back_data='back_fire_risks_calc'))
    await state.update_data(data)


@fire_risk_router.callback_query(F.data.in_(['edit_industrial', 'edit_industrial_guest', 'stop_edit_industrial']))
async def edit_industrial_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(4,
                                      *i18n.get('fire_risk_kb_ind').split('\n'),
                                      i18n=i18n, param_back=True, back_data='back_industrial'))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_efs_ind']))
async def k_efs_ind_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, 'k_efs_ind_true', 'k_efs_ind_true_095', 'k_efs_ind_false', 'stop_edit_industrial', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_alarm_ind']))
async def k_alarm_ind_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, 'k_alarm_ind_true', 'k_alarm_ind_false', 'stop_edit_industrial', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_evacuation_ind']))
async def k_evacuation_ind_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, 'k_evacuation_ind_true', 'k_evacuation_ind_false', 'stop_edit_industrial', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_smoke_ind']))
async def k_smoke_ind_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, 'k_smoke_ind_true', 'k_smoke_ind_false', 'stop_edit_industrial', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['emergency_escape_ind']))
async def emergency_escape_ind_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, 'emergency_escape_ind_true', 'emergency_escape_ind_false', 'stop_edit_industrial', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_efs_ind_true', 'k_efs_ind_true_095', 'k_efs_ind_false']))
async def k_efs_ind_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    call_data = callback.data
    # data = await state.get_data()
    if call_data == 'k_efs_ind_true':
        await state.update_data(k_efs_ind=0.9)
    elif call_data == 'k_efs_ind_true_095':
        await state.update_data(k_efs_ind=0.95)
    elif call_data == 'k_efs_ind_false':
        await state.update_data(k_efs_ind=0.0)
    data = await state.get_data()
    text = i18n.industrial.text()
    frisk = FireRisk(type_obj='industrial')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(4,
                                      *i18n.get('fire_risk_kb_ind').split('\n'),
                                      i18n=i18n, param_back=True, back_data='back_industrial'))

    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_alarm_ind_true', 'k_alarm_ind_false']))
async def k_alarm_ind_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    call_data = callback.data
    # data = await state.get_data()
    if call_data == 'k_alarm_ind_true':
        await state.update_data(k_alarm_ind=0.8)
    elif call_data == 'k_alarm_ind_false':
        await state.update_data(k_alarm_ind=0.0)
    data = await state.get_data()
    text = i18n.industrial.text()
    frisk = FireRisk(type_obj='industrial')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(4,
                                      *i18n.get('fire_risk_kb_ind').split('\n'),
                                      i18n=i18n, param_back=True, back_data='back_industrial'))

    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_evacuation_ind_true', 'k_evacuation_ind_false']))
async def k_evacuation_ind_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    call_data = callback.data
    # data = await state.get_data()
    if call_data == 'k_evacuation_ind_true':
        await state.update_data(k_evacuation_ind=0.8)
    elif call_data == 'k_evacuation_ind_false':
        await state.update_data(k_evacuation_ind=0.0)
    data = await state.get_data()
    text = i18n.industrial.text()
    frisk = FireRisk(type_obj='industrial')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(4,
                                      *i18n.get('fire_risk_kb_ind').split('\n'),
                                      i18n=i18n, param_back=True, back_data='back_industrial'))

    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_smoke_ind_true', 'k_smoke_ind_false']))
async def k_smoke_ind_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    call_data = callback.data
    # data = await state.get_data()
    if call_data == 'k_smoke_ind_true':
        await state.update_data(k_smoke_ind=0.8)
    elif call_data == 'k_smoke_ind_false':
        await state.update_data(k_smoke_ind=0.0)
    data = await state.get_data()
    text = i18n.industrial.text()
    frisk = FireRisk(type_obj='industrial')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(4,
                                      *i18n.get('fire_risk_kb_ind').split('\n'),
                                      i18n=i18n, param_back=True, back_data='back_industrial'))

    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['emergency_escape_ind_true', 'emergency_escape_ind_false']))
async def emergency_escape_ind_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    call_data = callback.data
    # data = await state.get_data()
    if call_data == 'emergency_escape_ind_true':
        await state.update_data(emergency_escape_ind=0.03)
    elif call_data == 'emergency_escape_ind_false':
        await state.update_data(emergency_escape_ind=0.001)
    data = await state.get_data()
    text = i18n.industrial.text()
    frisk = FireRisk(type_obj='industrial')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(4,
                                      *i18n.get('fire_risk_kb_ind').split('\n'), i18n=i18n, param_back=True, back_data='back_industrial'))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['fire_freq_ind']))
async def edit_fire_freq_ind_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.set_state(FSMFireRiskForm.edit_fire_freq_ind)
    data = await state.get_data()
    # state_data = await state.get_state()
    text = i18n.edit_industrial.text(industrial_param=i18n.get(
        "name_fire_freq_ind"), edit_industrial=data.get("fire_frequency_industrial", 0))
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3,
                                      *i18n.get('calculator_buttons').split('\n'),
                                      i18n=i18n, param_back=True, back_data='table_404'))
    await callback.answer('')


@ fire_risk_router.callback_query(StateFilter(FSMFireRiskForm.edit_fire_freq_ind), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'dooble_zero', 'point', 'clear']))
async def edit_fire_freq_ind_var_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    # state_data = await state.get_state()
    industrial_param = i18n.get("name_fire_freq_ind")

    edit_data = await state.get_data()
    if callback.data == 'clear':
        await state.update_data(edit_industrial_param="")
        edit_d = await state.get_data()
        edit_data = edit_d.get('edit_industrial_param', 1)
        text = i18n.edit_industrial.text(
            industrial_param=industrial_param, edit_industrial=edit_data)
    else:
        edit_param_1 = edit_data.get('edit_industrial_param')
        edit_sum = edit_param_1 + i18n.get(callback.data)
        await state.update_data(edit_industrial_param=edit_sum)
        edit_data = await state.get_data()
        edit_param = edit_data.get('edit_industrial_param', 0)
        text = i18n.edit_industrial.text(
            industrial_param=industrial_param, edit_industrial=edit_param)
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3,
                                      *i18n.get('calculator_buttons').split('\n'),
                                      i18n=i18n, param_back=True, back_data='table_404'))


@ fire_risk_router.callback_query(F.data.in_(['time_start_evacuation_ind', 'time_blocking_paths_ind', 'time_evacuation_ind', 'area_ind', 'working_days_per_year_ind', 'time_presence_ind', 'probity_evac_ind']))
async def edit_ind_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    if callback.data == 'fire_freq_ind':
        await state.set_state(FSMFireRiskForm.edit_fire_freq_ind)
    elif callback.data == 'area_ind':
        await state.set_state(FSMFireRiskForm.edit_area_ind)
    elif callback.data == 'working_days_per_year_ind':
        await state.set_state(FSMFireRiskForm.edit_work_days_ind)
    elif callback.data == 'time_presence_ind':
        await state.set_state(FSMFireRiskForm.edit_time_presence_ind)
    elif callback.data == 'probity_evac_ind':
        await state.set_state(FSMFireRiskForm.edit_probity_evac_ind)
    elif callback.data == 'time_start_evacuation_ind':
        await state.set_state(FSMFireRiskForm.edit_time_start_evacuation_ind)
    elif callback.data == 'time_evacuation_ind':
        await state.set_state(FSMFireRiskForm.edit_time_evacuation_ind)
    elif callback.data == 'time_blocking_paths_ind':
        await state.set_state(FSMFireRiskForm.edit_time_blocking_paths_ind)

    data = await state.get_data()
    state_data = await state.get_state()
    if state_data == FSMFireRiskForm.edit_time_presence_ind:
        text = i18n.edit_industrial.text(industrial_param=i18n.get(
            "name_time_presence_ind"), edit_industrial=data.get("time_presence_ind", 0))
    elif state_data == FSMFireRiskForm.edit_work_days_ind:
        text = i18n.edit_industrial.text(industrial_param=i18n.get(
            "name_work_days_ind"), edit_industrial=data.get("working_days_per_year_ind", 0))
    elif state_data == FSMFireRiskForm.edit_probity_evac_ind:
        text = i18n.edit_industrial.text(industrial_param=i18n.get(
            "name_probity_evac_ind"), edit_industrial=data.get("probity_evacuation_ind", 0))
    # elif state_data == FSMFireRiskForm.edit_fire_freq_ind:
    #     text = i18n.edit_industrial.text(industrial_param=i18n.get(
    #         "name_fire_freq_ind"), edit_industrial=data.get("fire_frequency_industrial", 0))
    elif state_data == FSMFireRiskForm.edit_area_ind:
        text = i18n.edit_industrial.text(industrial_param=i18n.get(
            "name_area_ind"), edit_industrial=data.get("area_ind", 0))
    elif state_data == FSMFireRiskForm.edit_time_blocking_paths_ind:
        text = i18n.edit_industrial.text(industrial_param=i18n.get(
            "name_time_blocking_paths_ind"), edit_industrial=data.get("time_blocking_paths_ind", 0))
    elif state_data == FSMFireRiskForm.edit_time_evacuation_ind:
        text = i18n.edit_industrial.text(industrial_param=i18n.get(
            "name_time_evacuation_ind"), edit_industrial=data.get("time_evacuation_ind", 0))
    elif state_data == FSMFireRiskForm.edit_time_start_evacuation_ind:
        text = i18n.edit_industrial.text(industrial_param=i18n.get(
            "name_time_start_evacuation_ind"), edit_industrial=data.get("time_start_evacuation_ind", 0))
    else:
        text = i18n.edit_industrial.text(
            industrial_param='Введите значение', edit_area=data.get("edit_industrial_param", 0))
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3,
                                      *i18n.get('calculator_buttons').split('\n'),
                                      i18n=i18n))
    await callback.answer('')


@ fire_risk_router.callback_query(StateFilter(*SFilter_ind), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'dooble_zero', 'point', 'clear']))
async def edit_ind_var_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    if state_data == FSMFireRiskForm.edit_time_presence_ind:
        industrial_param = i18n.get("name_time_presence_ind")
    elif state_data == FSMFireRiskForm.edit_work_days_ind:
        industrial_param = i18n.get("name_work_days_ind")
    elif state_data == FSMFireRiskForm.edit_probity_evac_ind:
        industrial_param = i18n.get("name_probity_evac_ind")
    elif state_data == FSMFireRiskForm.edit_fire_freq_ind:
        industrial_param = i18n.get("name_fire_freq_ind")
    elif state_data == FSMFireRiskForm.edit_area_ind:
        industrial_param = i18n.get("name_area_ind")
    elif state_data == FSMFireRiskForm.edit_time_blocking_paths_ind:
        industrial_param = i18n.get("name_time_blocking_paths_ind")
    elif state_data == FSMFireRiskForm.edit_time_evacuation_ind:
        industrial_param = i18n.get("name_time_evacuation_ind")
    elif state_data == FSMFireRiskForm.edit_time_start_evacuation_ind:
        industrial_param = i18n.get("name_time_start_evacuation_ind")

    edit_data = await state.get_data()
    if callback.data == 'clear':
        await state.update_data(edit_industrial_param="")
        edit_d = await state.get_data()
        edit_data = edit_d.get('edit_industrial_param', 1)
        text = i18n.edit_industrial.text(
            industrial_param=industrial_param, edit_industrial=edit_data)
    else:
        edit_param_1 = edit_data.get('edit_industrial_param')
        edit_sum = edit_param_1 + i18n.get(callback.data)
        await state.update_data(edit_industrial_param=edit_sum)
        edit_data = await state.get_data()
        edit_param = edit_data.get('edit_industrial_param', 0)
        text = i18n.edit_industrial.text(
            industrial_param=industrial_param, edit_industrial=edit_param)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3,
                                      *i18n.get('calculator_buttons').split('\n'),
                                      i18n=i18n))


@ fire_risk_router.callback_query(StateFilter(FSMFireRiskForm.edit_fire_freq_ind), F.data.in_(['ready']))
async def edit_industrial_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_industrial'))

    state_data = await state.get_state()
    data = await state.get_data()
    value = data.get("edit_industrial_param")
    if value != '' and value != '.':
        await state.update_data(fire_frequency_industrial=value)
    else:
        await state.update_data(fire_frequency_industrial=data.get("fire_frequency_industrial", 0))

    data = await state.get_data()
    text = i18n.industrial.text()

    frisk = FireRisk(type_obj='industrial')
    data_out, headers, label = frisk.get_init_data(**data)

    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(4,
                                      *i18n.get('fire_risk_kb_ind').split('\n'), i18n=i18n, param_back=True, back_data='back_industrial'))

    await state.update_data(edit_industrial_param='')
    await state.set_state(state=None)
    await callback.answer('')


@ fire_risk_router.callback_query(StateFilter(*SFilter_ind), F.data.in_(['ready']))
async def edit_industrial_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_industrial'))

    state_data = await state.get_state()
    data = await state.get_data()
    value = data.get("edit_industrial_param")
    if state_data == FSMFireRiskForm.edit_time_presence_ind:
        if value != '' and value != '.':
            await state.update_data(time_presence_ind=value)
        else:
            await state.update_data(time_presence_ind=0)
    elif state_data == FSMFireRiskForm.edit_work_days_ind:
        if value != '' and value != '.':
            await state.update_data(working_days_per_year_ind=value)
        else:
            await state.update_data(working_days_per_year_ind=247)
    elif state_data == FSMFireRiskForm.edit_probity_evac_ind:
        if value != '' and value != '.' and (float(value)) < 1:
            await state.update_data(probity_evacuation_ind=value)
            await state.update_data(time_evacuation_ind=100)
            await state.update_data(time_start_evacuation_ind=30)
            await state.update_data(time_blocking_paths_ind=300)
        else:
            await state.update_data(probity_evacuation_ind=0.999)
            await state.update_data(time_evacuation_ind=100)
            await state.update_data(time_start_evacuation_ind=30)
            await state.update_data(time_blocking_paths_ind=300)

    elif state_data == FSMFireRiskForm.edit_area_ind:
        if value != '' and value != '.':
            # await state.update_data(area_ind=value)
            await state.update_data(edit_area_to_frequency=value)
        else:
            await state.update_data(edit_area_to_frequency='10')
            # await state.update_data(area_ind=100)

    elif state_data == FSMFireRiskForm.edit_fire_freq_ind:
        if value != '' and value != '.':
            await state.update_data(fire_frequency_industrial=value)
        else:
            await state.update_data(fire_frequency_industrial=data.get("fire_frequency_industrial", 0))
    elif state_data == FSMFireRiskForm.edit_time_blocking_paths_ind:
        if value != '' and value != '.':
            await state.update_data(time_blocking_paths_ind=value)
        else:
            await state.update_data(time_blocking_paths_ind=600)
    elif state_data == FSMFireRiskForm.edit_time_start_evacuation_ind:
        if value != '' and value != '.':
            await state.update_data(time_start_evacuation_ind=value)
        else:
            await state.update_data(time_start_evacuation_ind=30)
    elif state_data == FSMFireRiskForm.edit_time_evacuation_ind:
        if value != '' and value != '.':
            await state.update_data(time_evacuation_ind=value)
        else:
            await state.update_data(time_evacuation_ind=300)

    else:
        await state.update_data(edit_industrial_param=value)
    data = await state.get_data()
    text = i18n.industrial.text()
    if state_data == FSMFireRiskForm.edit_probity_evac_ind:
        frisk = FireRisk(type_obj='industrial', prob_evac=True)
    else:
        frisk = FireRisk(type_obj='industrial')

    data_out, headers, label = frisk.get_init_data(**data)

    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(4,
                                      *i18n.get('fire_risk_kb_ind').split('\n'), i18n=i18n, param_back=True, back_data='back_industrial'))

    await state.update_data(edit_industrial_param='')
    await callback.answer('')


@ fire_risk_router.callback_query(F.data.in_(['run_industrial', 'run_industrial_guest']))
async def run_industrial_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()

    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'back_industrial', i18n=i18n))

    state_data = await state.get_state()
    if state_data == FSMFireRiskForm.edit_probity_evac_ind:
        frisk = FireRisk(type_obj='industrial', prob_evac=True)
    else:
        frisk = FireRisk(type_obj='industrial')
    data_out, headers, label, ind_risk = frisk.get_result_data(**data)
    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=5)

    if ind_risk > 0.0001:
        text = i18n.industrial_excess_second.text()
    elif ind_risk > 0.000001:
        text = i18n.industrial_excess_first.text()
    else:
        text = i18n.industrial_not_exceed.text()

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_industrial', i18n=i18n))
    # await state.update_data(data)
    await state.set_state(state=None)
    await callback.answer('')
