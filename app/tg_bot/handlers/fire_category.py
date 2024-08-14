import logging

# import json
# from datetime import datetime
from dataclasses import asdict

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaPhoto
# from aiogram.utils.chat_action import ChatActionSender
# from aiogram.enums import ChatAction

from fluentogram import TranslatorRunner

# from app.infrastructure.database.database.db import DB
from app.infrastructure.database.models.substance import FlammableMaterialModel

from app.tg_bot.models.role import UserRole
from app.tg_bot.models.keyboard import InlineKeyboardModel
from app.tg_bot.filters.filter_role import IsSubscriber, IsGuest
from app.tg_bot.utilities.tables import DataFrameBuilder
from app.tg_bot.states.fsm_state_data import FSMCatBuildForm, FSMEditForm
from app.calculation.fire_hazard_category.fire_hazard_categories import FireCategoryBuild, FireCategoryOutInstall
from app.calculation.models.calculations import RoomModel, SectionModel, from_dict
from app.calculation.physics.physics_utils import get_property_flammable_material

from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_keypad, get_inline_keyboard
from app.tg_bot.utilities.misc_utils import get_picture_filling, plot_graph, get_dataframe_table, find_key_path, get_dict_value, get_data_table


# from pprint import pprint

logging.getLogger('matplotlib.font_manager').disabled = True

log = logging.getLogger(__name__)

fire_category_router = Router()
# fire_category_router.message.filter(IsComrade())
# fire_category_router.callback_query.filter(IsComrade())
# fire_category_router.message.filter(IsSubscriber())
# fire_category_router.callback_query.filter(IsSubscriber())
fire_category_router.message.filter(IsGuest())
fire_category_router.callback_query.filter(IsGuest())


SFilter = [FSMCatBuildForm.edit_area_A_state,
           FSMCatBuildForm.edit_area_B_state,
           FSMCatBuildForm.edit_area_V1_state,
           FSMCatBuildForm.edit_area_V2_state,
           FSMCatBuildForm.edit_area_V3_state,
           FSMCatBuildForm.edit_area_V4_state,
           FSMCatBuildForm.edit_area_G_state,
           FSMCatBuildForm.edit_area_D_state]


@fire_category_router.callback_query(F.data.in_(['fire_category', 'back_fire_category']))
async def fire_category_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:

    material = get_property_flammable_material(material='АБС_Пластик')
    section_st = SectionModel(distance_to_ceiling=2, share_fire_load_area=5)
    section_st.material.append(material)
    section_st.mass.append(20)
    room_model = RoomModel(
        room_height=3.0, room_air_temperature=25.0, room_area=100.0)
    room_model.sections.append(section_st)
    # await state.update_data(room_model=asdict(room_model), temporary_parameter='', temporary_request='')

    text = i18n.fire_category.text()
    media = get_picture_filling(
        file_path='temp_files/temp/fire_category_logo.png')
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('category_kb_' +
                                                role).split('\n'),
                                      i18n=i18n, back_data='general_menu'
                                      )
    )

    context_data = await state.get_data()
    context_data.setdefault('room_model', asdict(room_model))
    await state.update_data(context_data)


@fire_category_router.callback_query(F.data.in_(['category_build', 'back_category_build']))
async def category_build_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_fire_category'))

    await state.set_state(state=None)

    data = await state.get_data()
    data.setdefault("edit_category_build_param", "")
    data.setdefault("area_build", "100")
    data.setdefault("area_A", "100")
    data.setdefault("area_B", "100")
    data.setdefault("area_V1", "100")
    data.setdefault("area_V2", "100")
    data.setdefault("area_V3", "100")
    data.setdefault("area_V4", "100")
    data.setdefault("area_G", "100")
    data.setdefault("area_D", "100")
    data.setdefault("area_A_EFS", "True")
    data.setdefault("area_B_EFS", "True")
    data.setdefault("area_V1_EFS", "True")
    data.setdefault("area_V2_EFS", "True")
    data.setdefault("area_V3_EFS", "True")

    info_area = [
        {'area': data.get("area_A", 0), 'category': 'А',
         'efs': data.get("area_A_EFS", False)},
        {'area': data.get("area_B", 0), 'category': 'Б',
         'efs': data.get("area_B_EFS", False)},
        {'area': data.get("area_V1", 0), 'category': 'В1',
         'efs': data.get("area_V1_EFS", False)},
        {'area': data.get("area_V2", 0), 'category': 'В2',
         'efs': data.get("area_V2_EFS", False)},
        {'area': data.get("area_V3", 0), 'category': 'В3',
         'efs': data.get("area_V3_EFS", False)},
        {'area': data.get("area_V4", 0), 'category': 'В4', 'efs': '-'},
        {'area': data.get("area_G", 0), 'category': 'Г', 'efs': '-'},
        {'area': data.get("area_D", 0), 'category': 'Д', 'efs': '-'}
    ]

    fc_build = FireCategoryBuild()
    data_out, headers, label = fc_build.get_init_data_table(
        *info_area)
    media = get_data_table(
        data=data_out, headers=headers, label=label, column=3)
    await state.update_data(data)

    text = i18n.category_build.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('category_build_kb_guest').split('\n') if role in ['guest'] else i18n.get('category_build_kb').split('\n'),
                                      i18n=i18n, back_data='back_fire_category'))
    await callback.answer('')


@fire_category_router.callback_query(F.data.in_(['edit_category_build_guest']))
async def edit_category_build_guest_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.get('initial_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('category_build_kb_guest').split('\n'),
                                      i18n=i18n, back_data='back_fire_category'))

    text = i18n.get('repeated_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('category_build_kb_guest').split('\n'),
                                      i18n=i18n, back_data='back_fire_category'))
    await callback.answer('')


@fire_category_router.callback_query(F.data.in_(['edit_category_build', 'back_category_build_edit', 'stop_edit_category_build']))
async def edit_init_data_strength_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2,
                                      'edit_area_A', 'edit_area_B', 'edit_area_V1', 'edit_area_V2',
                                      'edit_area_V3', 'edit_area_V4', 'edit_area_G', 'edit_area_D',
                                      'edit_area_A_EFS', 'edit_area_B_EFS', 'edit_area_V1_EFS', 'edit_area_V2_EFS', 'edit_area_V3_EFS',
                                      i18n=i18n, penult_button='run_category_build',
                                      back_data='back_category_build'))
    await callback.answer('')


@fire_category_router.callback_query(F.data.in_(['edit_area_A_EFS', 'edit_area_B_EFS', 'edit_area_V1_EFS', 'edit_area_V2_EFS', 'edit_area_V3_EFS']))
async def edit_area_efs_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    if callback.data == 'edit_area_A_EFS':
        await state.set_state(FSMCatBuildForm.edit_area_A_EFS_state)
    elif callback.data == 'edit_area_B_EFS':
        await state.set_state(FSMCatBuildForm.edit_area_B_EFS_state)
    elif callback.data == 'edit_area_V1_EFS':
        await state.set_state(FSMCatBuildForm.edit_area_V1_EFS_state)
    elif callback.data == 'edit_area_V2_EFS':
        await state.set_state(FSMCatBuildForm.edit_area_V2_EFS_state)
    elif callback.data == 'edit_area_V3_EFS':
        await state.set_state(FSMCatBuildForm.edit_area_V3_EFS_state)
    else:
        await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(2, 'efs_build_true', 'efs_build_false', i18n=i18n,
                                      param_back=True, back_data='back_category_build_edit'))
    await callback.answer('')


@fire_category_router.callback_query(~StateFilter(default_state), F.data.in_(['efs_build_true', 'efs_build_false']))
async def edit_area_efs_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    data = await state.get_data()

    if state_data == FSMCatBuildForm.edit_area_A_EFS_state:
        await state.update_data(area_A_EFS='True' if callback.data == 'efs_build_true' else 'False')
    elif state_data == FSMCatBuildForm.edit_area_B_EFS_state:
        await state.update_data(area_B_EFS='True' if callback.data == 'efs_build_true' else 'False')
    elif state_data == FSMCatBuildForm.edit_area_V1_EFS_state:
        await state.update_data(area_V1_EFS='True' if callback.data == 'efs_build_true' else 'False')
    elif state_data == FSMCatBuildForm.edit_area_V2_EFS_state:
        await state.update_data(area_V2_EFS='True' if callback.data == 'efs_build_true' else 'False')
    elif state_data == FSMCatBuildForm.edit_area_V3_EFS_state:
        await state.update_data(area_V3_EFS='True' if callback.data == 'efs_build_true' else 'False')
    else:
        await state.update_data(area_build='1')

    data = await state.get_data()
    info_area = [
        {'area': data.get("area_A", 0), 'category': 'А',
         'efs': data.get("area_A_EFS", False)},
        {'area': data.get("area_B", 0), 'category': 'Б',
         'efs': data.get("area_B_EFS", False)},
        {'area': data.get("area_V1", 0), 'category': 'В1',
         'efs': data.get("area_V1_EFS", False)},
        {'area': data.get("area_V2", 0), 'category': 'В2',
         'efs': data.get("area_V2_EFS", False)},
        {'area': data.get("area_V3", 0), 'category': 'В3',
         'efs': data.get("area_V3_EFS", False)},
        {'area': data.get("area_V4", 0), 'category': 'В4', 'efs': '-'},
        {'area': data.get("area_G", 0), 'category': 'Г', 'efs': '-'},
        {'area': data.get("area_D", 0), 'category': 'Д', 'efs': '-'}
    ]

    fc_build = FireCategoryBuild()
    data_out, headers, label = fc_build.get_init_data_table(
        *info_area)
    media = get_data_table(
        data=data_out, headers=headers, label=label, column=3)

    text = i18n.category_build.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(2,
                                      'edit_area_A', 'edit_area_B', 'edit_area_V1', 'edit_area_V2',
                                      'edit_area_V3', 'edit_area_V4', 'edit_area_G', 'edit_area_D',
                                      'edit_area_A_EFS', 'edit_area_B_EFS', 'edit_area_V1_EFS', 'edit_area_V2_EFS', 'edit_area_V3_EFS',
                                      i18n=i18n, back_data='back_category_build'))
    await state.set_state(state=None)
    await callback.answer('')


@fire_category_router.callback_query(F.data.in_(['edit_area_A', 'edit_area_B', 'edit_area_V1', 'edit_area_V2', 'edit_area_V3', 'edit_area_V4', 'edit_area_G', 'edit_area_D']))
async def edit_area_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    if callback.data == 'edit_area_A':
        await state.set_state(FSMCatBuildForm.edit_area_A_state)
    elif callback.data == 'edit_area_B':
        await state.set_state(FSMCatBuildForm.edit_area_B_state)
    elif callback.data == 'edit_area_V1':
        await state.set_state(FSMCatBuildForm.edit_area_V1_state)
    elif callback.data == 'edit_area_V2':
        await state.set_state(FSMCatBuildForm.edit_area_V2_state)
    elif callback.data == 'edit_area_V3':
        await state.set_state(FSMCatBuildForm.edit_area_V3_state)
    elif callback.data == 'edit_area_V4':
        await state.set_state(FSMCatBuildForm.edit_area_V4_state)
    elif callback.data == 'edit_area_G':
        await state.set_state(FSMCatBuildForm.edit_area_G_state)
    elif callback.data == 'edit_area_D':
        await state.set_state(FSMCatBuildForm.edit_area_D_state)

    state_data = await state.get_state()
    data = await state.get_data()
    if state_data == FSMCatBuildForm.edit_area_A_state:
        text = i18n.edit_area.text(edit_area=data.get("area_A", 0))
    elif state_data == FSMCatBuildForm.edit_area_B_state:
        text = i18n.edit_area.text(edit_area=data.get("area_B", 0))
    elif state_data == FSMCatBuildForm.edit_area_V1_state:
        text = i18n.edit_area.text(edit_area=data.get("area_V1", 0))
    elif state_data == FSMCatBuildForm.edit_area_V2_state:
        text = i18n.edit_area.text(edit_area=data.get("area_V2", 0))
    elif state_data == FSMCatBuildForm.edit_area_V3_state:
        text = i18n.edit_area.text(edit_area=data.get("area_V3", 0))
    elif state_data == FSMCatBuildForm.edit_area_V4_state:
        text = i18n.edit_area.text(edit_area=data.get("area_V4", 0))
    elif state_data == FSMCatBuildForm.edit_area_G_state:
        text = i18n.edit_area.text(edit_area=data.get("area_G", 0))
    elif state_data == FSMCatBuildForm.edit_area_D_state:
        text = i18n.edit_area.text(edit_area=data.get("area_D", 0))
    else:
        text = i18n.edit_area.text(edit_area=data.get("area_build", 0))
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3,
                                      *i18n.get('calculator_buttons').split('\n'),
                                      i18n=i18n))
    await callback.answer('')


@fire_category_router.callback_query(StateFilter(*SFilter), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'dooble_zero',]))
async def edit_area_cat_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    edit_area_data = await state.get_data()
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
    elif call_data == "dooble_zero":
        call_data = 00

    if call_data != 'clear':
        if edit_area_data.get('area_build') == None:
            await state.update_data(area_build="")
            edit_area_data = await state.get_data()
            await state.update_data(area_build=call_data)
            edit_area_data = await state.get_data()
            edit_area_edit = edit_area_data.get('area_build', 200)
            text = i18n.edit_area.text(edit_area=edit_area_edit)
        else:
            edit_area_1 = edit_area_data.get('area_build')
            edit_area_sum = str(edit_area_1) + str(call_data)
            await state.update_data(area_build=edit_area_sum)
            edit_area_data = await state.get_data()
            edit_area_edit = edit_area_data.get('area_build', 200)
            text = i18n.edit_area.text(edit_area=edit_area_edit)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3,
                                      *i18n.get('calculator_buttons').split('\n'),
                                      i18n=i18n))


@fire_category_router.callback_query(StateFilter(*SFilter), F.data.in_(['point']))
async def edit_area_var_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    edit_area_data = await state.get_data()
    call_data = callback.data
    if call_data == "point":
        call_data = '.'

    if edit_area_data.get('area_build') == None:
        await state.update_data(area_build="")
        edit_area_data = await state.get_data()
        await state.update_data(area_build=call_data)
        edit_area_data = await state.get_data()
        edit_area_edit = edit_area_data.get('area_build', 200)
        await state.update_data(area_build=edit_area_edit)
        text = i18n.edit_area.text(edit_area=edit_area_edit)
    else:
        edit_area_1 = edit_area_data.get('area_build')
        edit_area_sum = str(edit_area_1) + str(call_data)
        await state.update_data(area_build=edit_area_sum)
        edit_area_data = await state.get_data()
        edit_area_edit = edit_area_data.get('area_build', 200)
        await state.update_data(area_build=edit_area_edit)
        text = i18n.edit_area.text(edit_area=edit_area_edit)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3,
                                      *i18n.get('calculator_buttons').split('\n'),
                                      i18n=i18n))


@fire_category_router.callback_query(StateFilter(*SFilter), F.data.in_(['clear']))
async def edit_area_point_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    area_build_data = await state.get_data()
    await state.update_data(area_build="")
    area_build_data = await state.get_data()
    area_build_edit = area_build_data.get('area_build', 1000)
    text = i18n.edit_area.text(edit_area=area_build_edit)
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3,
                                      *i18n.get('calculator_buttons').split('\n'),
                                      i18n=i18n))
    await callback.answer('')


@fire_category_router.callback_query(StateFilter(*SFilter), F.data.in_(['ready']))
async def edit_area_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    data = await state.get_data()
    value = data.get("area_build")
    if value != '' and value != '.':
        await state.update_data(area_build=value)
    else:
        await state.update_data(area_build=0)
    data = await state.get_data()
    if state_data == FSMCatBuildForm.edit_area_A_state:
        await state.update_data(area_A=data.get("area_build", 0))
    elif state_data == FSMCatBuildForm.edit_area_B_state:
        await state.update_data(area_B=data.get("area_build", 0))
    elif state_data == FSMCatBuildForm.edit_area_V1_state:
        await state.update_data(area_V1=data.get("area_build", 0))
    elif state_data == FSMCatBuildForm.edit_area_V2_state:
        await state.update_data(area_V2=data.get("area_build", 0))
    elif state_data == FSMCatBuildForm.edit_area_V3_state:
        await state.update_data(area_V3=data.get("area_build", 0))
    elif state_data == FSMCatBuildForm.edit_area_V4_state:
        await state.update_data(area_V4=data.get("area_build", 0))
    elif state_data == FSMCatBuildForm.edit_area_G_state:
        await state.update_data(area_G=data.get("area_build", 0))
    elif state_data == FSMCatBuildForm.edit_area_D_state:
        await state.update_data(area_D=data.get("area_build", 0))
    else:
        await state.update_data(area_build='0')

    data = await state.get_data()
    info_area = [
        {'area': data.get("area_A", 0), 'category': 'А',
         'efs': data.get("area_A_EFS", False)},
        {'area': data.get("area_B", 0), 'category': 'Б',
         'efs': data.get("area_B_EFS", False)},
        {'area': data.get("area_V1", 0), 'category': 'В1',
         'efs': data.get("area_V1_EFS", False)},
        {'area': data.get("area_V2", 0), 'category': 'В2',
         'efs': data.get("area_V2_EFS", False)},
        {'area': data.get("area_V3", 0), 'category': 'В3',
         'efs': data.get("area_V3_EFS", False)},
        {'area': data.get("area_V4", 0), 'category': 'В4', 'efs': '-'},
        {'area': data.get("area_G", 0), 'category': 'Г', 'efs': '-'},
        {'area': data.get("area_D", 0), 'category': 'Д', 'efs': '-'}
    ]

    fc_build = FireCategoryBuild()
    data_out, headers, label = fc_build.get_init_data_table(
        *info_area)
    media = get_data_table(
        data=data_out, headers=headers, label=label, column=3)
    # fc_build_data = fc_build.get_category_build(*info_area)
    text = i18n.category_build.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="initial_data"), caption=text),
        reply_markup=get_inline_cd_kb(2,
                                      'edit_area_A', 'edit_area_B', 'edit_area_V1', 'edit_area_V2',
                                      'edit_area_V3', 'edit_area_V4', 'edit_area_G', 'edit_area_D',
                                      'edit_area_A_EFS', 'edit_area_B_EFS', 'edit_area_V1_EFS', 'edit_area_V2_EFS', 'edit_area_V3_EFS',
                                      i18n=i18n, back_data='back_category_build'))
    await state.update_data(area_build='')
    await state.set_state(state=None)
    await callback.answer('')


@fire_category_router.callback_query(F.data == 'run_category_build')
async def run_category_build_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    info_area = [
        {'area': data.get("area_A", 0),
         'category': 'А',
         'efs': data.get("area_A_EFS", False)},
        {'area': data.get("area_B", 0),
         'category': 'Б',
         'efs': data.get("area_B_EFS", False)},
        {'area': data.get("area_V1", 0),
         'category': 'В1',
         'efs': data.get("area_V1_EFS", False)},
        {'area': data.get("area_V2", 0),
         'category': 'В2',
         'efs': data.get("area_V2_EFS", False)},
        {'area': data.get("area_V3", 0),
         'category': 'В3',
         'efs': data.get("area_V3_EFS", False)},
        {'area': data.get("area_V4", 0),
         'category': 'В4',
         'efs': '-'},
        {'area': data.get("area_G", 0),
         'category': 'Г',
         'efs': '-'},
        {'area': data.get("area_D", 0),
         'category': 'Д',
         'efs': '-'}
    ]
    fc_build = FireCategoryBuild()
    data_out, headers, label = fc_build.get_init_data_table(
        *info_area)
    media = get_data_table(
        data=data_out, headers=headers, label=label, column=3)
    fc_build_data, cause = fc_build.get_category_build(*info_area)

    text = i18n.category_build_result.text(
        category_build=fc_build_data, cause=cause)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_category_build'))
    await callback.answer('')


@fire_category_router.callback_query(F.data.in_(['category_premises', 'back_category_premises']))
async def category_premises_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_fire_category'
                                      )
    )

    context_data = await state.get_data()
    line_numbers = [4, 9, 14]

    room_model = from_dict(data=context_data.get('room_model'))
    dfb = DataFrameBuilder(i18n=i18n,  request='category_premises',
                           model=room_model)
    dataframe = dfb.action_request()
    media = get_dataframe_table(
        data=dataframe, results=True, line_numbers=line_numbers)

    text = i18n.category_premises.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(2,
                                      *i18n.get('category_premises_kb_guest').split('\n') if role in ['guest'] else i18n.get('category_premises_kb').split('\n'),
                                      i18n=i18n, penult_button='run_category_premises', back_data='back_fire_category'
                                      )
    )
    # await state.update_data(temporary_request='category_premises', temporary_model='room_model')
    await callback.answer('')


@fire_category_router.callback_query(F.data.in_(['edit_category_premises']))
async def edit_category_premises_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    context_data = await state.get_data()

    kb = InlineKeyboardModel(
        width=2, buttons='edit_category_premises_kb', penultimate='run_category_premises', ultimate='back_category_premises', reference=None)

    context_data['keyboard_model'] = asdict(kb)
    context_data['temporary_request'] = 'category_premises'
    context_data['temporary_model'] = 'room_model'

    text = 'Какие параметры нужно изменить?'
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(2,
                                      *i18n.get('edit_category_premises_kb').split('\n'),
                                      i18n=i18n, penult_button='run_category_premises', back_data='back_category_premises'
                                      )
    )
    await state.update_data(context_data)
    # await state.update_data(temporary_request='category_premises', temporary_model='room_model')
    await callback.answer('')


@fire_category_router.callback_query(F.data.in_(['edit_parameter_room']))
async def edit_parameter_room_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_category_premises'
                                      )
    )

    context_data = await state.get_data()
    room_model = from_dict(data=context_data.get('room_model'))
    dfb = DataFrameBuilder(i18n=i18n,  request='edit_parameter_room',
                           model=room_model)
    dataframe = dfb.action_request()
    media = get_dataframe_table(data=dataframe)

    text = ''
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('edit_parameter_room_kb').split('\n'),
                                      i18n=i18n, penult_button='run_category_premises', back_data='back_category_premises'
                                      )
    )


@fire_category_router.callback_query(F.data.in_(['room_height', 'room_area', 'room_air_temperature']))
async def edit_pool_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    context_data = await state.get_data()

    path_edited_parameter = find_key_path(
        dictionary=context_data, key=callback.data)

    editable_parameter = get_dict_value(
        dictionary=context_data, keys_list=path_edited_parameter)

    text = i18n.temporary_parameter.text(
        text=i18n.get('name_' + callback.data), value=editable_parameter)

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
    await callback.answer('')


@fire_category_router.callback_query(F.data.in_(['edit_section_room']))
async def edit_section_room_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_category_premises'
                                      )
    )

    context_data = await state.get_data()
    num_sections = len(context_data['room_model']['sections'])

    if num_sections > 1:
        if num_sections == 2:
            kb = InlineKeyboardModel(
                width=3, buttons='num_two_sections_kb', prepenultimate='distance_to_section', penultimate='run_category_premises', ultimate='back_category_premises', reference=None)
        else:
            kb = InlineKeyboardModel(
                width=3, buttons='num_three_sections_kb', prepenultimate='distance_to_section', penultimate='run_category_premises', ultimate='back_category_premises', reference=None)
        text = 'Выбрать участок для редактирования'
        await bot.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            caption=text,
            reply_markup=get_inline_keyboard(keyboard=kb, i18n=i18n,
                                             )
        )
        await callback.answer('')

    else:
        context_data = await state.get_data()
        room_model = from_dict(data=context_data.get('room_model'))
        dfb = DataFrameBuilder(i18n=i18n,  request='edit_section_room',
                               model=room_model)
        dataframe = dfb.action_request()
        media = get_dataframe_table(data=dataframe)
        kb = InlineKeyboardModel(
            width=1, buttons='edit_section_kb', penultimate='run_category_premises', ultimate='back_category_premises', reference=None)
        text = 'Выбрать параметр для редактирования'
        await bot.edit_message_media(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            media=InputMediaPhoto(media=BufferedInputFile(
                file=media, filename="pic_filling"), caption=text),
            reply_markup=get_inline_keyboard(keyboard=kb, i18n=i18n,
                                             )
        )


@fire_category_router.callback_query(F.data.in_(['add_section_room']))
async def add_section_room_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_category_premises'
                                      )
    )

    context_data = await state.get_data()
    num_sections = len(context_data['room_model']['sections'])
    line_numbers = [4, 9, 14]
    if num_sections < 3:
        if num_sections == 2:
            material = get_property_flammable_material(material='Древесина')
        else:
            material = get_property_flammable_material(material='Полиэтилен')

        room_model = RoomModel(**context_data.get('room_model'))
        # room_model.sections.append(SectionModel())
        section = SectionModel(distance_to_ceiling=2, share_fire_load_area=5)
        section.material.append(material)
        section.mass.append(10)

        room_model.sections.append(section)

        await state.update_data(room_model=asdict(room_model), temporary_parameter='', temporary_request='')

        text = i18n.category_premises.text()
    else:
        text = 'В помещение можно добавить не более 3-х участков'

    context_data = await state.get_data()
    room_model = from_dict(data=context_data.get('room_model'))
    dfb = DataFrameBuilder(i18n=i18n,  request='category_premises',
                           model=room_model)
    dataframe = dfb.action_request()
    media = get_dataframe_table(
        data=dataframe, results=True, line_numbers=line_numbers)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(2,
                                      *i18n.get('category_premises_kb_guest').split('\n') if role in ['guest'] else i18n.get('category_premises_kb').split('\n'),
                                      i18n=i18n, penult_button='run_category_premises', back_data='back_category_premises'
                                      )
    )

    await callback.answer('')


@fire_category_router.callback_query(F.data.in_(['del_section_room']))
async def del_section_room_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_category_premises'
                                      )
    )

    context_data = await state.get_data()

    num_sections = len(context_data['room_model']['sections'])
    line_numbers = [4, 9, 14]
    if num_sections == 1:
        text = 'В помещении должно быть не менее 1-го участка'
    else:
        # Нужно удалить из словаря по ключу 'room_model'
        room_model = RoomModel(**context_data.get('room_model'))

        section = room_model.sections
        del section[-1]
        await state.update_data(room_model=asdict(room_model), temporary_parameter='', temporary_request='')
        text = i18n.category_premises.text()

    context_data = await state.get_data()
    room_model = from_dict(data=context_data.get('room_model'))
    dfb = DataFrameBuilder(i18n=i18n,  request='category_premises',
                           model=room_model)
    dataframe = dfb.action_request()
    media = get_dataframe_table(
        data=dataframe, results=True, line_numbers=line_numbers)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(2,
                                      *i18n.get('category_premises_kb_guest').split('\n') if role in ['guest'] else i18n.get('category_premises_kb').split('\n'),
                                      i18n=i18n, penult_button='run_category_premises',
                                      back_data='back_category_premises'
                                      )
    )

    await callback.answer('')


@fire_category_router.callback_query(F.data.in_(['first_section', 'second_section', 'third_section']))
async def select_section_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    context_data = await state.get_data()
    num_sections = len(context_data['room_model']['sections'])

    # if num_sections > 1:
    #     if num_sections == 2:
    #         kb = InlineKeyboardModel(
    #             width=1, buttons='num_two_sections_kb', penultimate='run_category_premises', ultimate='back_category_premises', reference=None)
    #     else:
    #         kb = InlineKeyboardModel(
    #             width=1, buttons='num_three_sections_kb', penultimate='run_category_premises', ultimate='back_category_premises', reference=None)

    # else:
    kb = InlineKeyboardModel(
        width=1, buttons=callback.data + '_kb', penultimate=None, ultimate='back_category_premises', reference=None)

    # context_data['keyboard_model'] = asdict(kb)

    context_data = await state.get_data()
    room_model = from_dict(data=context_data.get('room_model'))
    dfb = DataFrameBuilder(i18n=i18n,  request='edit_section_room',
                           model=room_model)
    dataframe = dfb.action_request()
    media = get_dataframe_table(data=dataframe)
    text = 'Выбрать параметр для редактирования'

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_keyboard(keyboard=kb, i18n=i18n,
                                         )
    )
    # await bot.edit_message_caption(
    #     chat_id=callback.message.chat.id,
    #     message_id=callback.message.message_id,
    #     caption=text,
    #     reply_markup=get_inline_keyboard(keyboard=kb, i18n=i18n,
    #                                      )
    # )
    context_data['temporary_section'] = callback.data
    await state.update_data(context_data)
    await callback.answer('')


@fire_category_router.callback_query(F.data.in_(['add_material_section']))
async def add_material_section_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    # context_data = await state.get_data()
    # num_sections = len(context_data['room_model']['sections'])
    kb = InlineKeyboardModel(
        width=2, buttons='list_flammable_material_kb', penultimate='run_category_premises', ultimate='back_category_premises', reference=None)

    text = 'Выберите материал'
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_keyboard(keyboard=kb, i18n=i18n,
                                         )
    )
    # context_data['temporary_material'] = asdict(kb)
    # await state.update_data(context_data)
    await callback.answer('')


@fire_category_router.callback_query(F.data.in_(['ABS_plastic', 'wood', 'polyethylene']))
async def select_material_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    context_data = await state.get_data()
    num_sections = len(context_data['room_model']['sections'])

    if num_sections > 1:
        if num_sections == 2:
            kb = InlineKeyboardModel(
                width=1, buttons='num_two_sections_kb', penultimate='run_category_premises', ultimate='back_category_premises', reference=None)
        else:
            kb = InlineKeyboardModel(
                width=1, buttons='num_three_sections_kb', penultimate='run_category_premises', ultimate='back_category_premises', reference=None)

    else:
        kb = InlineKeyboardModel(
            width=1, buttons='first_section', penultimate='run_category_premises', ultimate='back_category_premises', reference=None)

    text = 'Выберите участок'
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_keyboard(keyboard=kb, i18n=i18n,
                                         )
    )
    context_data['temporary_material'] = callback.data
    await state.update_data(context_data)
    await callback.answer('')


@fire_category_router.callback_query(F.data.in_(['add_material_section_process']))
async def add_material_section_process_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(i18n=i18n, back_data='back_category_premises'
                                      )
    )

    context_data = await state.get_data()

    num_sections = len(context_data['room_model']['sections'])
    if num_sections > 1:
        text = 'На один участок можно добавить не более 5-и материалов'
    else:
        # Нужно добавить материал на выбранный участок
        room_model = RoomModel(**context_data.get('room_model'))

        section = room_model.sections
        del section[-1]
        await state.update_data(room_model=asdict(room_model), temporary_parameter='', temporary_request='')
        text = i18n.category_premises.text()

    context_data = await state.get_data()
    room_model = from_dict(data=context_data.get('room_model'))
    dfb = DataFrameBuilder(i18n=i18n,  request='category_premises',
                           model=room_model)
    dataframe = dfb.action_request()
    media = get_dataframe_table(data=dataframe)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('category_premises_kb_guest').split('\n') if role in ['guest'] else i18n.get('category_premises_kb').split('\n'),
                                      i18n=i18n, penult_button='run_category_premises', back_data='back_category_premises'
                                      )
    )

    await callback.answer('')


@fire_category_router.callback_query(F.data.in_(['edit_category_premises_guest']))
async def edit_category_premises_guest_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.get('initial_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('category_premises_kb_guest').split('\n'),
                                      i18n=i18n, penult_button='run_category_premises', back_data='back_category_premises'
                                      )
    )

    text = i18n.get('repeated_request_guest')
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      *i18n.get('category_premises_kb_guest').split('\n'),
                                      i18n=i18n, penult_button='run_category_premises', back_data='back_category_premises'
                                      )
    )
    await callback.answer('')


@fire_category_router.callback_query((F.data.in_(['category_outdoor_installation', 'back_outdoor_installation',])))
async def category_outdoor_installation_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    text = i18n.category_outdoor_installation.text()

    data = await state.get_data()
    data.setdefault("substance", "Пропилен"),
    data.setdefault("pressure_substance_kPa", "2500"),
    data.setdefault("temperature_substance_C", "60"),
    data.setdefault("type_container", "Сепаратор"),
    data.setdefault("volume_container", "50.0"),
    data.setdefault("valve_closing_time", "120")

    fc_out_inst = FireCategoryOutInstall()
    data_out, headers, label = fc_out_inst.get_init_data_table()
    media = get_data_table(
        data=data_out, headers=headers, label=label, column=3)

    await state.update_data(data)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      # 'run_category_outdoor_installation',
                                      'back_fire_category', i18n=i18n
                                      )
    )
    await callback.answer('')


@fire_category_router.callback_query((F.data.in_(['run_category_outdoor_installation'])))
async def run_category_outdoor_installation_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    data = await state.get_data()
    data.setdefault("substance", "Пропилен"),
    data.setdefault("pressure_substance_kPa", "2500"),
    data.setdefault("temperature_substance_C", "60"),
    data.setdefault("type_container", "Сепаратор"),
    data.setdefault("volume_container", "50.0"),
    data.setdefault("valve_closing_time", "120")

    cat_out_inst = FireCategoryOutInstall()
    data_out, headers, label = cat_out_inst.get_init_data_table()

    media = get_data_table(
        data=data_out, headers=headers, label=label, column=3)

    category_out_inst = cat_out_inst.get_fire_hazard_categories()

    text = i18n.run_category_outdoor_installation.text(
        category_out_inst=category_out_inst)

    await state.update_data(data)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      i18n=i18n, back_data='back_outdoor_installation'
                                      )
    )
    await callback.answer('')

# @fire_category_router.callback_query(F.data == 'back_fire_category')
# async def back_fire_category_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
#     text = i18n.fire_category.text()
#     media = get_picture_filling(
#         file_path='temp_files/temp/fire_category_logo.png')
#     await bot.edit_message_media(
#         chat_id=callback.message.chat.id,
#         message_id=callback.message.message_id,
#         media=InputMediaPhoto(media=BufferedInputFile(
#             file=media, filename="pic_filling"), caption=text),
#         reply_markup=get_inline_cd_kb(1, 'category_build', 'category_premises', 'category_outdoor_installation', 'general_menu', i18n=i18n))
#     await callback.answer('')
