import logging

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, BufferedInputFile

from fluentogram import TranslatorRunner

# from app.infrastructure.database.database.db import DB
from app.tg_bot.filters.filter_role import IsComrade
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb
from app.tg_bot.utilities.misc_utils import get_picture_filling


log = logging.getLogger(__name__)
# logger = logging.getLogger(__name__)
# logger = logging.getLogger('matplotlib').setLevel(logging.ERROR)
# logger = logging.getLogger('PIL.PngImagePlugin').setLevel(logging.ERROR)


tools_router = Router()
tools_router.message.filter(IsComrade())
tools_router.callback_query.filter(IsComrade())

kb_tools = [2, 'tool_comp_gas', 'tool_liquid', 'tool_liq_gas', 'tool_vap_liquid',
            # 'tool_fifth', 'tool_sixth'
            ]


@tools_router.callback_query(F.data.in_(['tools', 'back_tools']))
async def tools_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.tools.text()
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(*kb_tools, param_back=True, back_data='general_menu', i18n=i18n))
    await callback_data.answer('')


@tools_router.callback_query(F.data == 'tool_liquid')
async def tool_liquid_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    state_data = await state.get_state()
    data = await state.get_data()
    data.setdefault("edit_tool_liquid", "0")
    data.setdefault("tool_liquid_vol", "10")

    text = i18n.tool_liquid.text()
    # frisk = FireRisk(type_obj='public', prob_evac=True)

    # data_out, headers, label = frisk.get_init_data(**data)
    # media = get_data_table(data=data_out, headers=headers, label=label)
    media = get_picture_filling(file_path='temp_files/temp/fsr_logo.png')

    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'tool_liquid', 'edit_tool_liquid', param_back=True, back_data='back_tools', i18n=i18n))
    await state.update_data(data)
    await callback_data.answer('')
