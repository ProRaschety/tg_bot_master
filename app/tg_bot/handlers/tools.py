import logging

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, BufferedInputFile

from fluentogram import TranslatorRunner

# from app.infrastructure.database.database.db import DB
from app.tg_bot.models.role import UserRole
from app.tg_bot.filters.filter_role import IsComrade
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb
from app.tg_bot.utilities.misc_utils import get_picture_filling, get_data_table
from app.tg_bot.states.fsm_state_data import FSMToolLiquidForm, FSMToolCompGasForm
from app.calculation.physics.physics_tools import PhysicTool

log = logging.getLogger(__name__)


tools_router = Router()
tools_router.message.filter(IsComrade())
tools_router.callback_query.filter(IsComrade())

kb_tools = [1, 'tool_liquid', 'tool_comp_gas', 'tool_liq_gas', 'tool_vap_liquid',
            # 'tool_fifth', 'tool_sixth'
            ]

SFilter_tool_liquid = [
    FSMToolLiquidForm.edit_state_liquid_density,
    FSMToolLiquidForm.edit_state_liquid_volume_vessel,
    FSMToolLiquidForm.edit_state_liquid_height_vessel,
    FSMToolLiquidForm.edit_state_liquid_vessel_diameter,
    FSMToolLiquidForm.edit_state_liquid_temperature,
    FSMToolLiquidForm.edit_state_liquid_fill_factor,
    FSMToolLiquidForm.edit_state_liquid_hole_diameter,
    FSMToolLiquidForm.edit_state_liquid_hole_distance,
    FSMToolLiquidForm.edit_state_liquid_mu]

SFilter_tool_comp_gas = [
    FSMToolCompGasForm.edit_state_comp_gas_density,
    FSMToolCompGasForm.edit_state_comp_gas_volume_vessel,
    FSMToolCompGasForm.edit_state_comp_gas_height_vessel,
    FSMToolCompGasForm.edit_state_comp_gas_vessel_diameter,
    FSMToolCompGasForm.edit_state_comp_gas_temperature,
    FSMToolCompGasForm.edit_state_comp_gas_fill_factor,
    FSMToolCompGasForm.edit_state_comp_gas_hole_diameter,
    FSMToolCompGasForm.edit_state_comp_gas_hole_distance,
    FSMToolCompGasForm.edit_state_comp_gas_mu]

kb_but_liquid = [3, "but_liquid_density",
                 "but_liquid_volume_vessel",
                 "but_liquid_height_vessel",
                 #  "but_liquid_vessel_diameter",
                 "but_liquid_temperature",
                 "but_liquid_fill_factor",
                 "but_liquid_hole_diameter",
                 "but_liquid_hole_distance",
                 "but_liquid_mu"]


@tools_router.callback_query(F.data.in_(['tools', 'back_tools']))
async def tools_call(callback_data: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.tools.text()
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*kb_tools, param_back=True, back_data='general_menu', i18n=i18n))
    await callback_data.answer('')


@tools_router.callback_query(F.data.in_(['tool_liquid', 'back_tool_liquid']))
async def tool_liquid_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    data = await state.get_data()
    data.setdefault("edit_tool_liquid_param", "0")
    data.setdefault("tool_liquid_density", "1000")
    data.setdefault("tool_liquid_volume_vessel", "1000")
    data.setdefault("tool_liquid_height_vessel", "10")
    data.setdefault("tool_liquid_vessel_diameter", "10")
    data.setdefault("tool_liquid_temperature", "20")
    data.setdefault("tool_liquid_fill_factor", "0.85")
    data.setdefault("tool_liquid_hole_diameter", "0.1")
    data.setdefault("tool_liquid_hole_distance", "0.1")
    data.setdefault("tool_liquid_mu", "0.62")
    # data.setdefault("tool_liquid_hole_area", "1")

    text = i18n.tool_liquid.text()
    ph_tool = PhysicTool(type_substance='liquid')
    data_out, headers, label = ph_tool.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)

    # media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')

    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_tool_liquid', 'run_tool_liquid', param_back=True, back_data='back_tools', i18n=i18n))
    await state.update_data(data)
    await callback_data.answer('')


@tools_router.callback_query(F.data.in_(['run_tool_liquid', 'plot_tool_liquid']))
async def run_tool_liquid_call(callback: CallbackQuery, state: FSMContext, bot: Bot, i18n: TranslatorRunner) -> None:
    data = await state.get_data()

    ph_tool = PhysicTool(type_substance='liquid')
    mass_flow = ph_tool.compute_init_mass_flow_rate(**data)
    media = ph_tool.get_plot_mass_flow_rate(
        add_annotate=True, add_legend=True, **data)
    # data_out, headers, label = ph_tool.get_init_data(**data)
    # media = get_data_table(data=data_out, headers=headers, label=label)

    text = i18n.tool_liquid_result.text(mass_flow=f'{mass_flow:.2f}')
    # await state.update_data(time_fsr=t_fsr/60)

    # media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="plot_tools"), caption=text),
        reply_markup=get_inline_cd_kb(param_back=True, back_data='back_tool_liquid', i18n=i18n))
    await state.set_state(state=None)
    await callback.answer('')


@tools_router.callback_query(F.data.in_(['edit_tool_liquid', 'edit_tool_liquid_guest', 'stop_edit_tool_liquid']))
async def edit_tool_liquid_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(*kb_but_liquid, i18n=i18n, param_back=True, back_data='back_tool_liquid', check_role=True, role=role))
    await callback.answer('')


@tools_router.callback_query(F.data.in_(kb_but_liquid))
async def edit_tool_liquid_kb_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    log.info(callback.data)
    if callback.data == 'but_liquid_height_vessel':
        await state.set_state(FSMToolLiquidForm.edit_state_liquid_height_vessel)
    elif callback.data == 'but_liquid_hole_diameter':
        await state.set_state(FSMToolLiquidForm.edit_state_liquid_hole_diameter)
    elif callback.data == 'but_liquid_density':
        await state.set_state(FSMToolLiquidForm.edit_state_liquid_density)
    elif callback.data == 'but_liquid_volume_vessel':
        await state.set_state(FSMToolLiquidForm.edit_state_liquid_volume_vessel)
    elif callback.data == 'but_liquid_vessel_diameter':
        await state.set_state(FSMToolLiquidForm.edit_state_liquid_vessel_diameter)
    elif callback.data == 'but_liquid_temperature':
        await state.set_state(FSMToolLiquidForm.edit_state_liquid_temperature)
    elif callback.data == 'but_liquid_fill_factor':
        await state.set_state(FSMToolLiquidForm.edit_state_liquid_fill_factor)
    elif callback.data == 'but_liquid_hole_distance':
        await state.set_state(FSMToolLiquidForm.edit_state_liquid_hole_distance)
    elif callback.data == 'but_liquid_mu':
        await state.set_state(FSMToolLiquidForm.edit_state_liquid_mu)

    data = await state.get_data()
    state_data = await state.get_state()
    if state_data == FSMToolLiquidForm.edit_state_liquid_height_vessel:
        text = i18n.edit_tool_liquid.text(tool_liquid_param=i18n.get(
            "name_liquid_height_vessel"), edit_tool_liquid=data.get("tool_liquid_height_vessel", 0))
    elif state_data == FSMToolLiquidForm.edit_state_liquid_hole_diameter:
        text = i18n.edit_tool_liquid.text(tool_liquid_param=i18n.get(
            "name_liquid_hole_diameter"), edit_tool_liquid=data.get("tool_liquid_hole_diameter", 0))
    elif state_data == FSMToolLiquidForm.edit_state_liquid_density:
        text = i18n.edit_tool_liquid.text(tool_liquid_param=i18n.get(
            "name_liquid_density"), edit_tool_liquid=data.get("tool_liquid_density", 0))
    elif state_data == FSMToolLiquidForm.edit_state_liquid_volume_vessel:
        text = i18n.edit_tool_liquid.text(tool_liquid_param=i18n.get(
            "name_liquid_volume_vessel"), edit_tool_liquid=data.get("tool_liquid_volume_vessel", 0))
    elif state_data == FSMToolLiquidForm.edit_state_liquid_vessel_diameter:
        text = i18n.edit_tool_liquid.text(tool_liquid_param=i18n.get(
            "name_liquid_vessel_diameter"), edit_tool_liquid=data.get("tool_liquid_vessel_diameter", 0))
    elif state_data == FSMToolLiquidForm.edit_state_liquid_temperature:
        text = i18n.edit_tool_liquid.text(tool_liquid_param=i18n.get(
            "name_liquid_temperature"), edit_tool_liquid=data.get("tool_liquid_temperature", 0))
    elif state_data == FSMToolLiquidForm.edit_state_liquid_fill_factor:
        text = i18n.edit_tool_liquid.text(tool_liquid_param=i18n.get(
            "name_liquid_fill_factor"), edit_tool_liquid=data.get("tool_liquid_fill_factor", 0))
    elif state_data == FSMToolLiquidForm.edit_state_liquid_hole_distance:
        text = i18n.edit_tool_liquid.text(tool_liquid_param=i18n.get(
            "name_liquid_hole_distance"), edit_tool_liquid=data.get("tool_liquid_hole_distance", 0))
    elif state_data == FSMToolLiquidForm.edit_state_liquid_mu:
        text = i18n.edit_tool_liquid.text(tool_liquid_param=i18n.get(
            "name_liquid_mu"), edit_tool_liquid=data.get("tool_liquid_mu", 0))
    else:
        text = i18n.edit_tool_liquid.text(
            tool_liquid_param='Введите значение', edit_tool_liquid=data.get("edit_tool_liquid_param", 0))

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready', i18n=i18n))
    await callback.answer('')


@tools_router.callback_query(StateFilter(*SFilter_tool_liquid), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'dooble_zero', 'point', 'clear']))
async def edit_tool_liquid_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    if state_data == FSMToolLiquidForm.edit_state_liquid_height_vessel:
        tool_liquid_param = i18n.get("name_liquid_height_vessel")
    elif state_data == FSMToolLiquidForm.edit_state_liquid_hole_diameter:
        tool_liquid_param = i18n.get("name_liquid_hole_diameter")
    elif state_data == FSMToolLiquidForm.edit_state_liquid_density:
        tool_liquid_param = i18n.get("name_liquid_density")
    elif state_data == FSMToolLiquidForm.edit_state_liquid_volume_vessel:
        tool_liquid_param = i18n.get("name_liquid_volume_vessel")
    elif state_data == FSMToolLiquidForm.edit_state_liquid_vessel_diameter:
        tool_liquid_param = i18n.get("name_liquid_vessel_diameter")
    elif state_data == FSMToolLiquidForm.edit_state_liquid_temperature:
        tool_liquid_param = i18n.get("name_liquid_temperature")
    elif state_data == FSMToolLiquidForm.edit_state_liquid_fill_factor:
        tool_liquid_param = i18n.get("name_liquid_fill_factor")
    elif state_data == FSMToolLiquidForm.edit_state_liquid_hole_distance:
        tool_liquid_param = i18n.get("name_liquid_hole_distance")
    elif state_data == FSMToolLiquidForm.edit_state_liquid_mu:
        tool_liquid_param = i18n.get("name_liquid_mu")

    edit_data = await state.get_data()
    if callback.data == 'clear':
        await state.update_data(edit_tool_liquid_param="")
        edit_d = await state.get_data()
        edit_data = edit_d.get('edit_tool_liquid_param', 1)
        text = i18n.edit_tool_liquid.text(
            tool_liquid_param=tool_liquid_param, edit_tool_liquid=edit_data)

    else:
        edit_param_1 = edit_data.get('edit_tool_liquid_param')
        edit_sum = edit_param_1 + i18n.get(callback.data)
        await state.update_data(edit_tool_liquid_param=edit_sum)
        edit_data = await state.get_data()
        edit_param = edit_data.get('edit_tool_liquid_param', 0)
        text = i18n.edit_tool_liquid.text(
            tool_liquid_param=tool_liquid_param, edit_tool_liquid=edit_param)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready', i18n=i18n))


@tools_router.callback_query(StateFilter(*SFilter_tool_liquid), F.data.in_(['ready']))
async def edit_tool_liquid_param_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    data = await state.get_data()
    value = data.get("edit_tool_liquid_param")
    if state_data == FSMToolLiquidForm.edit_state_liquid_height_vessel:
        if value != '' and value != '.':
            await state.update_data(tool_liquid_height_vessel=value)
        else:
            await state.update_data(tool_liquid_height_vessel=0)
    elif state_data == FSMToolLiquidForm.edit_state_liquid_hole_diameter:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(tool_liquid_hole_diameter=value)
        else:
            await state.update_data(tool_liquid_hole_diameter=0.01)
    elif state_data == FSMToolLiquidForm.edit_state_liquid_density:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(tool_liquid_density=value)
        else:
            await state.update_data(tool_liquid_density=1000)
    elif state_data == FSMToolLiquidForm.edit_state_liquid_volume_vessel:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(tool_liquid_volume_vessel=value)
        else:
            await state.update_data(tool_liquid_volume_vessel=100)
    elif state_data == FSMToolLiquidForm.edit_state_liquid_vessel_diameter:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(tool_liquid_vessel_diameter=value)
        else:
            await state.update_data(tool_liquid_vessel_diameter=5)
    elif state_data == FSMToolLiquidForm.edit_state_liquid_temperature:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(tool_liquid_temperature=value)
        else:
            await state.update_data(tool_liquid_temperature=20)
    elif state_data == FSMToolLiquidForm.edit_state_liquid_fill_factor:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(tool_liquid_fill_factor=value)
        else:
            await state.update_data(tool_liquid_fill_factor=0.95)
    elif state_data == FSMToolLiquidForm.edit_state_liquid_hole_distance:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(tool_liquid_hole_distance=value)
        else:
            await state.update_data(tool_liquid_hole_distance=0.1)
    elif state_data == FSMToolLiquidForm.edit_state_liquid_mu:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(tool_liquid_mu=value)
        else:
            await state.update_data(tool_liquid_mu=0.62)
    else:
        await state.update_data(edit_tool_liquid_param=value)

    data = await state.get_data()
    text = i18n.tool_liquid.text()
    ph_tool = PhysicTool(type_substance='liquid')
    data_out, headers, label = ph_tool.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*kb_but_liquid, i18n=i18n, param_back=True, back_data='back_tool_liquid'))

    await state.update_data(edit_tool_liquid_param='')
    await callback.answer('')


@tools_router.callback_query(F.data.in_(['tool_comp_gas', 'back_tool_comp_gas']))
async def tool_comp_gas_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    data = await state.get_data()
    data.setdefault("edit_tool_comp_gas_param", "0")
    data.setdefault("tool_comp_gas_density", "1000")
    data.setdefault("tool_comp_gas_volume_vessel", "1000")
    data.setdefault("tool_comp_gas_height_vessel", "10")
    data.setdefault("tool_comp_gas_vessel_diameter", "10")
    data.setdefault("tool_comp_gas_temperature", "20")
    data.setdefault("tool_comp_gas_fill_factor", "0.85")
    data.setdefault("tool_comp_gas_hole_diameter", "0.1")
    data.setdefault("tool_comp_gas_hole_distance", "0.1")
    data.setdefault("tool_comp_gas_mu", "0.62")
    # data.setdefault("tool_comp_gas_hole_area", "1")

    text = i18n.tool_comp_gas.text()
    ph_tool = PhysicTool(type_substance='comp_gas')
    data_out, headers, label = ph_tool.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)

    # media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')

    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'edit_tool_comp_gas', 'run_tool_comp_gas', param_back=True, back_data='back_tools', i18n=i18n))
    await state.update_data(data)
    await callback_data.answer('')
