import logging

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
# , InlineQueryResultArticle, InputTextMessageContent
from aiogram.types import InlineQuery
from aiogram.types import CallbackQuery, Message, BufferedInputFile, InputMediaPhoto, InputFile, InputMediaDocument

from fluentogram import TranslatorRunner

from app.infrastructure.database.database.db import DB
from app.tg_bot.filters.filter_role import IsSubscriber
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb
from app.tg_bot.utilities.misc_utils import get_temp_folder, get_csv_file, get_csv_bt_file, get_picture_filling, get_data_table
from app.tg_bot.states.fsm_state_data import FSMFireRiskForm
from app.calculation.qra_mode.fire_risk_calculator import FireRisk

log = logging.getLogger(__name__)

fire_risk_router = Router()
fire_risk_router.message.filter(IsSubscriber())
fire_risk_router.callback_query.filter(IsSubscriber())


@fire_risk_router.callback_query(F.data == 'fire_risks')
async def fire_risks_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.fire_risks.text()
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'fire_risks_calculator', 'typical_accidents', 'general_menu', i18n=i18n))
    await callback_data.answer('')


@fire_risk_router.callback_query(F.data == 'back_fire_risks')
async def back_fire_risks_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.fire_risks.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'fire_risks_calculator',
                                      'typical_accidents',
                                      'general_menu', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'back_typical_accidents')
async def back_typical_accidents_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.fire_risks.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'fire_pool',
                                      'fire_flash',
                                      'cloud_explosion',
                                      'horizontal_jet',
                                      'vertical_jet',
                                      'fire_ball',
                                      'bleve',
                                      'back_fire_risks', i18n=i18n))

    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'typical_accidents')
async def typical_accidents_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.fire_risks.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'fire_pool',
                                      'fire_flash',
                                      'cloud_explosion',
                                      'horizontal_jet',
                                      'vertical_jet',
                                      'fire_ball',
                                      'bleve',
                                      'back_fire_risks', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['fire_risks_calculator', 'back_fire_risks_calc']))
async def fire_risks_calculator_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
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


@fire_risk_router.callback_query(F.data.in_(['public', 'back_public']))
async def public_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.set_state(state=None)
    data = await state.get_data()
    data.setdefault("edit_public_param", "0")
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
    log.info(str(callback.data))
    frisk = FireRisk(type_obj='public')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_public', 'run_public', 'back_fire_risks_calc', i18n=i18n))
    await state.update_data(data)
    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'run_public')
async def run_public_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
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
    text = i18n.public.text()
    log.info(str(callback.data))
    frisk = FireRisk(type_obj='public')
    data_out, headers, label = frisk.get_result_data(**data)
    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=9)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_public', 'back_fire_risks_calc', i18n=i18n))
    await state.update_data(data)
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['edit_public', 'stop_edit_public']))
async def edit_public_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(1, 'fire_freq_pub', 'time_presence_pub', 'probity_evac_pub',
                                      'k_efs_pub', 'k_alarm_pub', 'k_evacuation_pub', 'k_smoke_pub',
                                      'back_public', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['fire_freq_pub', 'time_presence_pub', 'probity_evac_pub']))
async def edit_pub_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.set_state(f'FSMFireRiskForm.{"edit_"+callback.data}')
    data = await state.get_data()
    state_data = await state.get_state()
    if state_data == 'FSMFireRiskForm.edit_time_presence_pub':
        text = i18n.edit_public.text(public_param=i18n.get(
            "name_time_presence_pub"), edit_public=data.get("time_presence_pub", 0))
    elif state_data == 'FSMFireRiskForm.edit_probity_evac_pub':
        text = i18n.edit_public.text(public_param=i18n.get(
            "name_probity_evac_pub"), edit_public=data.get("probity_evacuation_pub", 0))
    elif state_data == 'FSMFireRiskForm.edit_fire_freq_pub':
        text = i18n.edit_public.text(public_param=i18n.get(
            "name_fire_freq_pub"), edit_public=data.get("fire_freq_pub", 0))
    else:
        text = i18n.edit_public.text(
            public_param='Тут будет текст', edit_area=data.get("edit_public_param", 0))
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(~StateFilter(default_state), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero']))
async def edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    if state_data == 'FSMFireRiskForm.edit_time_presence_pub':
        public_param = i18n.get("name_time_presence_pub")
    elif state_data == 'FSMFireRiskForm.edit_probity_evac_pub':
        public_param = i18n.get("name_probity_evac_pub")
    elif state_data == 'FSMFireRiskForm.edit_fire_freq_pub':
        public_param = i18n.get("name_fire_freq_pub")

    edit_data = await state.get_data()
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
        if edit_data.get('edit_public_param') == None:
            await state.update_data(edit_public_param="")
            edit_data = await state.get_data()
            await state.update_data(edit_public_param=call_data)
            edit_data = await state.get_data()
            edit_param = edit_data.get('edit_public_param', 0)
            text = i18n.edit_public.text(
                public_param=public_param, edit_public=edit_param)
        else:
            edit_param_1 = edit_data.get('edit_public_param')
            edit_sum = str(edit_param_1) + str(call_data)
            await state.update_data(edit_public_param=edit_sum)
            edit_data = await state.get_data()
            edit_param = edit_data.get('edit_public_param', 0)
            text = i18n.edit_public.text(
                public_param=public_param, edit_public=edit_param)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))


@fire_risk_router.callback_query(~StateFilter(default_state), F.data.in_(['point']))
async def edit_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    if state_data == 'FSMFireRiskForm.edit_time_presence_pub':
        public_param = i18n.get("name_time_presence_pub")
    elif state_data == 'FSMFireRiskForm.edit_probity_evac_pub':
        public_param = i18n.get("name_probity_evac_pub")
    elif state_data == 'FSMFireRiskForm.edit_fire_freq_pub':
        public_param = i18n.get("name_fire_freq_pub")

    edit_data = await state.get_data()
    call_data = callback.data
    if call_data == "point":
        call_data = '.'
    if edit_data.get('edit_public_param') == None:
        await state.update_data(edit_public_param="")
        edit_data = await state.get_data()
        await state.update_data(edit_public_param=call_data)
        edit_data = await state.get_data()
        edit_param = edit_data.get('edit_public_param', 0)
        text = i18n.edit_public.text(
            public_param=public_param, edit_public=edit_param)
    else:
        edit_param_1 = edit_data.get('edit_public_param')
        edit_sum = str(edit_param_1) + str(call_data)
        await state.update_data(edit_public_param=edit_sum)
        edit_data = await state.get_data()
        edit_param = edit_data.get('edit_public_param', 0)
        text = i18n.edit_public.text(
            public_param=public_param, edit_public=edit_param)
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))


@fire_risk_router.callback_query(~StateFilter(default_state), F.data.in_(['clear']))
async def edit_point_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    if state_data == 'FSMFireRiskForm.edit_time_presence_pub':
        public_param = i18n.get("name_time_presence_pub")
    elif state_data == 'FSMFireRiskForm.edit_probity_evac_pub':
        public_param = i18n.get("name_probity_evac_pub")
    elif state_data == 'FSMFireRiskForm.edit_fire_freq_pub':
        public_param = i18n.get("name_fire_freq_pub")

    edit_data = await state.get_data()
    await state.update_data(edit_public_param="")
    edit_d = await state.get_data()
    edit_data = edit_d.get('edit_public_param', 1000)
    text = i18n.edit_public.text(
        public_param=public_param, edit_public=edit_data)
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'point', 'zero', 'clear', 'ready', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(~StateFilter(default_state), F.data.in_(['ready']))
async def edit_public_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    data = await state.get_data()
    value = data.get("edit_public_param")
    if state_data == 'FSMFireRiskForm.edit_time_presence_pub':
        if value != '' and value != '.':
            await state.update_data(time_presence_pub=value)
        else:
            await state.update_data(time_presence_pub=1)
    elif state_data == 'FSMFireRiskForm.edit_probity_evac_pub':
        if value != '' and value != '.':
            await state.update_data(probity_evacuation_pub=value)
        else:
            await state.update_data(probity_evacuation_pub=0.999)

    elif state_data == 'FSMFireRiskForm.edit_fire_freq_pub':
        if value != '' and value != '.':
            await state.update_data(fire_freq_pub=value)
        else:
            await state.update_data(fire_freq_pub=0.04)

    else:
        await state.update_data(edit_public_param=value)
    data = await state.get_data()
    text = i18n.public.text()
    frisk = FireRisk(type_obj='public')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'fire_freq_pub', 'time_presence_pub', 'probity_evac_pub',
                                      'k_efs_pub', 'k_alarm_pub', 'k_evacuation_pub', 'k_smoke_pub', 'back_public', i18n=i18n))
    await state.update_data(edit_public_param='')
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_efs_pub']))
async def k_efs_pub_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, 'k_efs_pub_true', 'k_efs_pub_false', 'stop_edit_public', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_alarm_pub']))
async def k_alarm_pub_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, 'k_alarm_pub_true', 'k_alarm_pub_false', 'stop_edit_public', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_evacuation_pub']))
async def k_evacuation_pub_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, 'k_evacuation_pub_true', 'k_evacuation_pub_false', 'stop_edit_public', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_smoke_pub']))
async def k_evacuation_pub_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, 'k_smoke_pub_true', 'k_smoke_pub_false', 'stop_edit_public', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_efs_pub_true', 'k_efs_pub_false']))
async def k_efs_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    call_data = callback.data
    data = await state.get_data()
    if call_data == 'k_efs_pub_true':
        await state.update_data(k_efs_pub=0.9)
    elif call_data == 'k_efs_pub_false':
        await state.update_data(k_efs_pub=0.0)
    data = await state.get_data()
    text = i18n.public.text()
    log.info(str(callback.data))
    frisk = FireRisk(type_obj='public')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'fire_freq_pub', 'time_presence_pub', 'probity_evac_pub',
                                      'k_efs_pub', 'k_alarm_pub', 'k_evacuation_pub', 'k_smoke_pub', 'back_public', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_alarm_pub_true', 'k_alarm_pub_false']))
async def k_alarm_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    call_data = callback.data
    data = await state.get_data()
    if call_data == 'k_alarm_pub_true':
        await state.update_data(k_alarm_pub=0.8)
    elif call_data == 'k_alarm_pub_false':
        await state.update_data(k_alarm_pub=0.0)
    data = await state.get_data()
    text = i18n.public.text()
    log.info(str(callback.data))
    frisk = FireRisk(type_obj='public')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'fire_freq_pub', 'time_presence_pub', 'probity_evac_pub',
                                      'k_efs_pub', 'k_alarm_pub', 'k_evacuation_pub', 'k_smoke_pub', 'back_public', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_evacuation_pub_true', 'k_evacuation_pub_false']))
async def k_evacuation_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    call_data = callback.data
    data = await state.get_data()
    if call_data == 'k_evacuation_pub_true':
        await state.update_data(k_evacuation_pub=0.8)
    elif call_data == 'k_evacuation_pub_false':
        await state.update_data(k_evacuation_pub=0.0)
    data = await state.get_data()
    text = i18n.public.text()
    log.info(str(callback.data))
    frisk = FireRisk(type_obj='public')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'fire_freq_pub', 'time_presence_pub', 'probity_evac_pub',
                                      'k_efs_pub', 'k_alarm_pub', 'k_evacuation_pub', 'k_smoke_pub', 'back_public', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['k_smoke_pub_true', 'k_smoke_pub_false']))
async def k_evacuation_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    call_data = callback.data
    data = await state.get_data()
    if call_data == 'k_smoke_pub_true':
        await state.update_data(k_smoke_pub=0.8)
    elif call_data == 'k_smoke_pub_false':
        await state.update_data(k_smoke_pub=0.0)
    data = await state.get_data()
    text = i18n.public.text()
    log.info(str(callback.data))
    frisk = FireRisk(type_obj='public')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'fire_freq_pub', 'time_presence_pub', 'probity_evac_pub',
                                      'k_efs_pub', 'k_alarm_pub', 'k_evacuation_pub', 'k_smoke_pub', 'back_public', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['industrial', 'back_industrial']))
async def industrial_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    data.setdefault("area_ind", "100.0")
    data.setdefault("fire_freq_ind", "0.04")
    data.setdefault("k_efs_ind", "0.9")
    data.setdefault("time_presence_ind", "2.0")
    data.setdefault("probity_evacuation_ind", "0.999")
    data.setdefault("time_evacuation_ind", "5.0")
    data.setdefault("time_blocking_paths_ind", "10")
    data.setdefault("time_crowding_ind", "1.0")
    data.setdefault("time_start_evacuation_ind", "1.0")
    data.setdefault("k_alarm_ind", "0.8")
    data.setdefault("k_evacuation_ind", "0.8")
    data.setdefault("k_smoke_ind", "0.8")
    data.setdefault("working_days_per_year_ind", "0.8")
    data.setdefault("emergency_escape_ind", "0.001")

    text = i18n.industrial.text()
    log.info(str(callback.data))
    frisk = FireRisk(type_obj='industrial')
    data_out, headers, label = frisk.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'run_industrial', 'back_fire_risks_calc', i18n=i18n))
    await state.update_data(data)
    await callback.answer('')


@fire_risk_router.callback_query(F.data.in_(['run_industrial']))
async def run_industrial_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    data.setdefault("area_ind", "100.0")
    data.setdefault("fire_freq_ind", "0.04")
    data.setdefault("k_efs_ind", "0.9")
    data.setdefault("time_presence_ind", "2.0")
    data.setdefault("probity_evacuation_ind", "0.999")
    data.setdefault("time_evacuation_ind", "5.0")
    data.setdefault("time_blocking_paths_ind", "10")
    data.setdefault("time_crowding_ind", "1.0")
    data.setdefault("time_start_evacuation_ind", "1.0")
    data.setdefault("k_alarm_ind", "0.8")
    data.setdefault("k_evacuation_ind", "0.8")
    data.setdefault("k_smoke_ind", "0.8")
    data.setdefault("working_days_per_year_ind", "0.8")
    data.setdefault("emergency_escape_ind", "0.001")

    text = i18n.industrial.text()
    log.info(str(callback.data))
    frisk = FireRisk(type_obj='industrial')
    data_out, headers, label = frisk.get_result_data(**data)
    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=5)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_industrial', i18n=i18n))
    await state.update_data(data)
    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'fire_pool')
async def fire_pool_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.fire_pool.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'fire_flash')
async def fire_flash_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.fire_flash.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'cloud_explosion')
async def cloud_explosion_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.cloud_explosion.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'horizontal_jet')
async def horizontal_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.horizontal_jet.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'vertical_jet')
async def vertical_jet_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.vertical_jet.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'fire_ball')
async def fire_ball_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.fire_ball.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')


@fire_risk_router.callback_query(F.data == 'bleve')
async def bleve_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.bleve.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_risk_logo.png')
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_typical_accidents', 'general_menu', i18n=i18n))
    await callback.answer('')
