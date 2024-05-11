import logging

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, BufferedInputFile

from fluentogram import TranslatorRunner

# from app.infrastructure.database.database.db import DB
from app.tg_bot.models.role import UserRole
from app.tg_bot.filters.filter_role import IsSubscriber
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb
from app.tg_bot.utilities.misc_utils import get_picture_filling, get_data_table
from app.tg_bot.states.fsm_state_data import FSMToolLiquidForm, FSMToolCompGasForm
from app.calculation.physics.physics_tools import PhysicTool

log = logging.getLogger(__name__)


tools_router = Router()
tools_router.message.filter(IsSubscriber())
tools_router.callback_query.filter(IsSubscriber())

kb_tools = [1, 'tool_liquid', 'tool_comp_gas',
            'tool_liq_gas', 'tool_evaporation_rate']

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

kb_but_liquid = [4, "but_liquid_density",
                 "but_liquid_volume_vessel",
                 "but_liquid_height_vessel",
                 #  "but_liquid_vessel_diameter",
                 "but_liquid_temperature",
                 "but_liquid_fill_factor",
                 "but_liquid_hole_diameter",
                 "but_liquid_hole_distance",
                 "but_liquid_mu"]

SFilter_tool_comp_gas = [
    FSMToolCompGasForm.edit_state_comp_gas_pres_init,
    FSMToolCompGasForm.edit_state_comp_gas_density,
    FSMToolCompGasForm.edit_state_comp_gas_volume_vessel,
    FSMToolCompGasForm.edit_state_comp_gas_height_vessel,
    FSMToolCompGasForm.edit_state_comp_gas_vessel_diameter,
    FSMToolCompGasForm.edit_state_comp_gas_coef_poisson,
    FSMToolCompGasForm.edit_state_comp_gas_hole_diameter,
    FSMToolCompGasForm.edit_state_comp_gas_molar_mass,
    FSMToolCompGasForm.edit_state_comp_gas_mu,
    FSMToolCompGasForm.edit_state_comp_gas_specific_heat_const_vol]

kb_but_comp_gas = [4,
                   "but_comp_gas_pres_init",
                   "but_comp_gas_volume_vessel",
                   #    "but_comp_gas_height_vessel",
                   #    "but_comp_gas_vessel_diameter",
                   "but_comp_gas_temperature",
                   "but_comp_gas_coef_poisson",
                   "but_comp_gas_hole_diameter",
                   "but_comp_gas_molar_mass",
                   "but_comp_gas_mu",
                   "but_comp_gas_specific_heat_const_vol"
                   ]


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


"""____жидкость____"""


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
    data.setdefault("accident_horizontal_jet_mass_rate", "5")

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


@tools_router.callback_query(F.data.in_(['run_tool_liquid']))
async def run_tool_liquid_call(callback: CallbackQuery, state: FSMContext, bot: Bot, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    text = i18n.tool_liquid.text()
    ph_tool = PhysicTool(type_substance='liquid')
    data_out, headers, label = ph_tool.get_result_data(**data)
    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=9)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="plot_tools"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'plot_tool_liquid', param_back=True, back_data='back_tool_liquid', i18n=i18n))
    await state.set_state(state=None)
    await callback.answer('')


@tools_router.callback_query(F.data.in_(['plot_tool_liquid']))
async def plot_tool_liquid_call(callback: CallbackQuery, state: FSMContext, bot: Bot, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    text = i18n.tool_liquid.text()
    ph_tool = PhysicTool(type_substance='liquid')
    # mass_flow = ph_tool.compute_init_mass_flow_rate(**data)
    media = ph_tool.get_plot_mass_flow_rate(
        add_annotate=True, add_legend=True, **data)
    # data_out, headers, label = ph_tool.get_init_data(**data)
    # media = get_data_table(data=data_out, headers=headers, label=label)

    # text = i18n.tool_liquid_result.text(mass_flow=f'{mass_flow:.3f}')
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


"""____сжатый_газ____"""


@tools_router.callback_query(F.data.in_(['tool_comp_gas', 'back_tool_comp_gas']))
async def tool_comp_gas_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    data = await state.get_data()
    data.setdefault("edit_tool_comp_gas_param", "1")
    data.setdefault("tool_comp_gas_density", "1")
    data.setdefault("tool_comp_gas_volume_vessel", "200")
    data.setdefault("tool_comp_gas_height_vessel", "10")
    data.setdefault("tool_comp_gas_vessel_diameter", "10")
    data.setdefault("tool_comp_gas_temperature", "20")
    data.setdefault("tool_comp_gas_coef_poisson", "1.40")
    data.setdefault("tool_comp_gas_hole_diameter", "0.1")
    data.setdefault("tool_comp_gas_mu", "0.8")
    data.setdefault("tool_comp_gas_pres_init", "5000000")
    data.setdefault("tool_comp_gas_molar_mass", "0.002")
    data.setdefault("tool_comp_gas_specific_heat_const_vol", "10.24")
    data.setdefault("accident_horizontal_jet_mass_rate", "5")

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


@tools_router.callback_query(F.data.in_(['run_tool_comp_gas', 'result_tool_comp_gas']))
async def run_tool_comp_gas_call(callback: CallbackQuery, state: FSMContext, bot: Bot, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    text = i18n.tool_comp_gas.text()
    ph_tool = PhysicTool(type_substance='comp_gas')
    # mass_flow = ph_tool.compute_outflow_comp_gas(**data)
    # media = ph_tool.get_plot_mass_flow_rate(
    #     add_annotate=True, add_legend=True, **data)
    # data_out, headers, label = ph_tool.get_init_data(**data)
    # media = get_data_table(data=data_out, headers=headers, label=label)
    # text = i18n.tool_comp_gas_result.text(mass_flow=f'{mass_flow:.2f}')
    # await state.update_data(time_fsr=t_fsr/60)
    data_out, headers, label = ph_tool.get_result_data(**data)
    media = get_data_table(data=data_out, headers=headers,
                           label=label, results=True, row_num=10)
    # media = get_picture_filling(file_path='temp_files/temp/logo_pic_filling.png')

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="plot_tools"), caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'plot_tool_comp_gas',
                                      param_back=True, back_data='back_tool_comp_gas', i18n=i18n))
    await state.set_state(state=None)


@tools_router.callback_query(F.data.in_(['plot_tool_comp_gas']))
async def plot_tool_comp_gas_call(callback: CallbackQuery, state: FSMContext, bot: Bot, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    text = i18n.tool_comp_gas.text()
    ph_tool = PhysicTool(type_substance='comp_gas')
    # mass_flow = ph_tool.compute_outflow_comp_gas(**data)
    # media = ph_tool.get_plot_mass_flow_rate(
    #     add_annotate=True, add_legend=True, **data)
    # data_out, headers, label = ph_tool.get_init_data(**data)
    # media = get_data_table(data=data_out, headers=headers, label=label)
    # text = i18n.tool_comp_gas_result.text(mass_flow=f'{mass_flow:.2f}')
    # await state.update_data(time_fsr=t_fsr/60)
    # data_out, headers, label = ph_tool.get_result_data(**data)
    # media = get_data_table(data=data_out, headers=headers,
    #                        label=label, results=True, row_num=11)
    # media = get_picture_filling(file_path='temp_files/temp/logo_pic_filling.png')
    media = ph_tool.get_plot_mass_flow_rate(
        add_annotate=True, add_legend=True, **data)
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="plot_tools"), caption=text),
        reply_markup=get_inline_cd_kb(param_back=True, back_data='back_tool_comp_gas', i18n=i18n))
    await state.set_state(state=None)


@tools_router.callback_query(F.data.in_(['edit_tool_comp_gas', 'edit_tool_comp_gas_guest', 'stop_edit_tool_comp_gas']))
async def edit_tool_comp_gas_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    await state.set_state(state=None)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(*kb_but_comp_gas, i18n=i18n, param_back=True, back_data='back_tool_comp_gas', check_role=True, role=role))
    await callback.answer('')


@tools_router.callback_query(F.data.in_(kb_but_comp_gas))
async def edit_tool_comp_gas_kb_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    log.info(callback.data)
    if callback.data == 'but_comp_gas_pres_init':
        await state.set_state(FSMToolCompGasForm.edit_state_comp_gas_pres_init)
    elif callback.data == 'but_comp_gas_hole_diameter':
        await state.set_state(FSMToolCompGasForm.edit_state_comp_gas_hole_diameter)
    elif callback.data == 'but_comp_gas_density':
        await state.set_state(FSMToolCompGasForm.edit_state_comp_gas_density)
    elif callback.data == 'but_comp_gas_volume_vessel':
        await state.set_state(FSMToolCompGasForm.edit_state_comp_gas_volume_vessel)
    elif callback.data == 'but_comp_gas_vessel_diameter':
        await state.set_state(FSMToolCompGasForm.edit_state_comp_gas_vessel_diameter)
    elif callback.data == 'but_comp_gas_temperature':
        await state.set_state(FSMToolCompGasForm.edit_state_comp_gas_temperature)
    elif callback.data == 'but_comp_gas_coef_poisson':
        await state.set_state(FSMToolCompGasForm.edit_state_comp_gas_coef_poisson)
    elif callback.data == 'but_comp_gas_molar_mass':
        await state.set_state(FSMToolCompGasForm.edit_state_comp_gas_molar_mass)
    elif callback.data == 'but_comp_gas_mu':
        await state.set_state(FSMToolCompGasForm.edit_state_comp_gas_mu)
    elif callback.data == 'but_comp_gas_specific_heat_const_vol':
        await state.set_state(FSMToolCompGasForm.edit_state_comp_gas_specific_heat_const_vol)

    data = await state.get_data()
    state_data = await state.get_state()
    if state_data == FSMToolCompGasForm.edit_state_comp_gas_pres_init:
        text = i18n.edit_tool_comp_gas.text(tool_comp_gas_param=i18n.get(
            "name_comp_gas_pres_init"), edit_tool_comp_gas=data.get("tool_comp_gas_pres_init", 0))
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_hole_diameter:
        text = i18n.edit_tool_comp_gas.text(tool_comp_gas_param=i18n.get(
            "name_comp_gas_hole_diameter"), edit_tool_comp_gas=data.get("tool_comp_gas_hole_diameter", 0))
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_density:
        text = i18n.edit_tool_comp_gas.text(tool_comp_gas_param=i18n.get(
            "name_comp_gas_density"), edit_tool_comp_gas=data.get("tool_comp_gas_density", 0))
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_volume_vessel:
        text = i18n.edit_tool_comp_gas.text(tool_comp_gas_param=i18n.get(
            "name_comp_gas_volume_vessel"), edit_tool_comp_gas=data.get("tool_comp_gas_volume_vessel", 0))
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_vessel_diameter:
        text = i18n.edit_tool_comp_gas.text(tool_comp_gas_param=i18n.get(
            "name_comp_gas_vessel_diameter"), edit_tool_comp_gas=data.get("tool_comp_gas_vessel_diameter", 0))
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_temperature:
        text = i18n.edit_tool_comp_gas.text(tool_comp_gas_param=i18n.get(
            "name_comp_gas_temperature"), edit_tool_comp_gas=data.get("tool_comp_gas_temperature", 0))
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_coef_poisson:
        text = i18n.edit_tool_comp_gas.text(tool_comp_gas_param=i18n.get(
            "name_comp_gas_coef_poisson"), edit_tool_comp_gas=data.get("tool_comp_gas_coef_poisson", 0))
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_molar_mass:
        text = i18n.edit_tool_comp_gas.text(tool_comp_gas_param=i18n.get(
            "name_comp_gas_molar_mass"), edit_tool_comp_gas=data.get("tool_comp_gas_molar_mass", 0))
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_mu:
        text = i18n.edit_tool_comp_gas.text(tool_comp_gas_param=i18n.get(
            "name_comp_gas_mu"), edit_tool_comp_gas=data.get("tool_comp_gas_mu", 0))
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_specific_heat_const_vol:
        text = i18n.edit_tool_comp_gas.text(tool_comp_gas_param=i18n.get(
            "name_comp_gas_specific_heat_const_vol"), edit_tool_comp_gas=data.get("tool_comp_gas_specific_heat_const_vol", 0))

    if state_data == FSMToolCompGasForm.edit_state_comp_gas_temperature:
        kb = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
              'nine', 'zero', 'point', 'dooble_zero', 'minus', 'clear', 'ready']
    else:
        kb = ['one', 'two', 'three', 'four', 'five', 'six', 'seven',
              'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready']

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, *kb, i18n=i18n))
    await callback.answer('')


@tools_router.callback_query(StateFilter(*SFilter_tool_comp_gas), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'dooble_zero', 'point', 'clear']))
async def edit_tool_comp_gas_in_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    if state_data == FSMToolCompGasForm.edit_state_comp_gas_pres_init:
        tool_comp_gas_param = i18n.get("name_comp_gas_pres_init")
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_hole_diameter:
        tool_comp_gas_param = i18n.get("name_comp_gas_hole_diameter")
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_density:
        tool_comp_gas_param = i18n.get("name_comp_gas_density")
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_volume_vessel:
        tool_comp_gas_param = i18n.get("name_comp_gas_volume_vessel")
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_vessel_diameter:
        tool_comp_gas_param = i18n.get("name_comp_gas_vessel_diameter")
    # elif state_data == FSMToolCompGasForm.edit_state_comp_gas_temperature:
    #     tool_comp_gas_param = i18n.get("name_comp_gas_temperature")
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_coef_poisson:
        tool_comp_gas_param = i18n.get("name_comp_gas_coef_poisson")
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_molar_mass:
        tool_comp_gas_param = i18n.get("name_comp_gas_molar_mass")
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_mu:
        tool_comp_gas_param = i18n.get("name_comp_gas_mu")
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_specific_heat_const_vol:
        tool_comp_gas_param = i18n.get("name_comp_gas_specific_heat_const_vol")

    edit_data = await state.get_data()
    if callback.data == 'clear':
        await state.update_data(edit_tool_comp_gas_param="")
        edit_d = await state.get_data()
        edit_data = edit_d.get('edit_tool_comp_gas_param', 1)
        text = i18n.edit_tool_comp_gas.text(
            tool_comp_gas_param=tool_comp_gas_param, edit_tool_comp_gas=edit_data)

    else:
        edit_param_1 = edit_data.get('edit_tool_comp_gas_param')
        edit_sum = edit_param_1 + i18n.get(callback.data)
        await state.update_data(edit_tool_comp_gas_param=edit_sum)
        edit_data = await state.get_data()
        edit_param = edit_data.get('edit_tool_comp_gas_param', 0)
        text = i18n.edit_tool_comp_gas.text(
            tool_comp_gas_param=tool_comp_gas_param, edit_tool_comp_gas=edit_param)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'point', 'dooble_zero', 'clear', 'ready', i18n=i18n))


@tools_router.callback_query(StateFilter(FSMToolCompGasForm.edit_state_comp_gas_temperature), F.data.in_(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'dooble_zero', 'point', 'clear', 'minus']))
async def edit_tool_comp_gas_temp_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    tool_comp_gas_param = i18n.get("name_comp_gas_temperature")
    edit_data = await state.get_data()
    if callback.data == 'clear':
        await state.update_data(edit_tool_comp_gas_param="")
        edit_d = await state.get_data()
        edit_data = edit_d.get('edit_tool_comp_gas_param', 1)
        text = i18n.edit_tool_comp_gas.text(
            tool_comp_gas_param=tool_comp_gas_param, edit_tool_comp_gas=edit_data)
    else:
        edit_param_1 = edit_data.get('edit_tool_comp_gas_param')
        edit_sum = edit_param_1 + i18n.get(callback.data)
        await state.update_data(edit_tool_comp_gas_param=edit_sum)
        edit_data = await state.get_data()
        edit_param = edit_data.get('edit_tool_comp_gas_param', 0)
        text = i18n.edit_tool_comp_gas.text(
            tool_comp_gas_param=tool_comp_gas_param, edit_tool_comp_gas=edit_param)

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(3, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero', 'point', 'dooble_zero', 'minus', 'clear', 'ready', i18n=i18n))


@tools_router.callback_query(StateFilter(*SFilter_tool_comp_gas), F.data.in_(['ready']))
async def edit_tool_comp_gas_param_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    data = await state.get_data()
    value = data.get("edit_tool_comp_gas_param")
    if state_data == FSMToolCompGasForm.edit_state_comp_gas_pres_init:
        if value != '' and value != '.':
            await state.update_data(tool_comp_gas_pres_init=value)
        else:
            await state.update_data(tool_comp_gas_pres_init=0)
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_hole_diameter:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(tool_comp_gas_hole_diameter=value)
        else:
            await state.update_data(tool_comp_gas_hole_diameter=0.01)
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_density:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(tool_comp_gas_density=value)
        else:
            await state.update_data(tool_comp_gas_density=1000)
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_volume_vessel:
        if value != '' and value != '.' and (float(value)) > 0 and (float(value)) < 200:
            await state.update_data(tool_comp_gas_volume_vessel=value)
        else:
            await state.update_data(tool_comp_gas_volume_vessel=200)
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_vessel_diameter:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(tool_comp_gas_vessel_diameter=value)
        else:
            await state.update_data(tool_comp_gas_vessel_diameter=5)
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_temperature:
        if value != '' and value != '.' and (float(value)) > -273.15:
            await state.update_data(tool_comp_gas_temperature=value)
        else:
            await state.update_data(tool_comp_gas_temperature=20)
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_coef_poisson:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(tool_comp_gas_coef_poisson=value)
        else:
            await state.update_data(tool_comp_gas_coef_poisson=0.95)
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_molar_mass:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(tool_comp_gas_molar_mass=value)
        else:
            await state.update_data(tool_comp_gas_molar_mass=0.016)
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_mu:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(tool_comp_gas_mu=value)
        else:
            await state.update_data(tool_comp_gas_mu=0.80)
    elif state_data == FSMToolCompGasForm.edit_state_comp_gas_specific_heat_const_vol:
        if value != '' and value != '.' and (float(value)) > 0:
            await state.update_data(tool_comp_gas_specific_heat_const_vol=value)
        else:
            await state.update_data(tool_comp_gas_specific_heat_const_vol=1.40)
    else:
        await state.update_data(edit_tool_comp_gas_param=value)

    data = await state.get_data()
    text = i18n.tool_comp_gas.text()
    ph_tool = PhysicTool(type_substance='comp_gas')
    data_out, headers, label = ph_tool.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*kb_but_comp_gas, i18n=i18n, param_back=True, back_data='back_tool_comp_gas'))

    await state.update_data(edit_tool_comp_gas_param='')
    await callback.answer('')


@tools_router.callback_query(StateFilter(FSMToolCompGasForm.edit_state_comp_gas_temperature), F.data.in_(['ready']))
async def edit_tool_comp_gas_ready_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    value = data.get("edit_tool_comp_gas_param")
    if value != '' and value != '.' and value != '-' and (float(value)) > -273.15:
        await state.update_data(tool_comp_gas_temperature=value)
    else:
        await state.update_data(tool_comp_gas_temperature=20)

    data = await state.get_data()
    text = i18n.tool_comp_gas.text()
    ph_tool = PhysicTool(type_substance='comp_gas')
    data_out, headers, label = ph_tool.get_init_data(**data)
    media = get_data_table(data=data_out, headers=headers, label=label)

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*kb_but_comp_gas, i18n=i18n, param_back=True, back_data='back_tool_comp_gas'))

    await state.update_data(edit_tool_comp_gas_param='')
    await callback.answer('')


"""____сжиженный_газ____"""


@tools_router.callback_query(F.data.in_(['tool_liq_gas', 'back_tool_liq_gas']))
async def tool_liq_gas_call(callback_data: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.tools.text()
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'tool_liq_gas_vap', 'tool_liq_gas_liq', param_back=True, back_data='back_tools', i18n=i18n))
    await callback_data.answer('')

"""____испарение_жидкой_фазы____"""


@tools_router.callback_query(F.data.in_(['tool_evaporation_rate']))
async def tool_evaporation_rate_call(callback_data: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.tools.text()
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(param_back=True, back_data='back_tools', i18n=i18n))
    await callback_data.answer('')
