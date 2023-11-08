import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.types.input_file import BufferedInputFile
from fluentogram import TranslatorRunner
from app.tg_bot.utilities.getting_data_base import quantity_keys_get
from app.calculation.fire_resistance.fire_mode import run_fire_mode
from app.calculation.physics._graph import plotting_fire_resistance
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb
from app.calculation.fire_resistance.steel_heating_calculation import steel_heating
from app.tg_bot.utilities.misc_utils import get_temp_folder

logger = logging.getLogger(__name__)

fire_res_router = Router()


@fire_res_router.callback_query(F.data == 'fire_resistance')
async def fire_resistance_call(callback_data: CallbackQuery, i18n: TranslatorRunner) -> None:

    await callback_data.message.answer(
        text=i18n.fire_resistance.text(),
        reply_markup=get_inline_cd_kb(1, 'thermal_calculation', 'strength_calculation', i18n=i18n))


@fire_res_router.callback_query(F.data == 'thermal_calculation')
async def thermal_calculation_call(callback_data: CallbackQuery, i18n: TranslatorRunner) -> None:

    time_res = steel_heating()

    await callback_data.message.answer(
        text=i18n.thermal_calculation.text(time_fsr=time_res),
        reply_markup=get_inline_cd_kb(1, 'plot_thermal_calculation', 'general_menu', i18n=i18n))


@fire_res_router.callback_query(F.data == 'plot_thermal_calculation')
async def strength_calculation_call(callback_data: CallbackQuery, i18n: TranslatorRunner) -> None:
    chat_id = str(callback_data.message.chat.id)
    text = i18n.plot_thermal_calculation.text()

    mode = 'Стандартный'
    time = 30

    temperature_element = run_fire_mode(mode=mode, time=time)

    name_plot = "_".join([str(i18n.plot_thermal_name.text()), chat_id, '.png'])
    name_dir = "/".join([get_temp_folder(), name_plot])

    with open(name_dir, 'rb') as file:
        input_file = BufferedInputFile(file.read(), 'any_filename')
    # E:\tg_bot_master\temp\plot_heating_793011788_.png

    await callback_data.message.answer_photo(
        photo=input_file,
        caption=text,
        has_spoiler=False,
        reply_markup=get_inline_cd_kb(1, 'general_menu', i18n=i18n))
