import logging

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
# , InlineQueryResultArticle, InputTextMessageContent
# from aiogram.types import InlineQuery
from aiogram.types import CallbackQuery, Message, BufferedInputFile, InputMediaPhoto, InputMediaAnimation, FSInputFile

from fluentogram import TranslatorRunner

# from app.infrastructure.database.database.db import DB
from app.tg_bot.models.role import UserRole
from app.tg_bot.filters.filter_role import IsGuest
from app.tg_bot.utilities.misc_utils import get_picture_filling, get_plot_graph
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb
from app.tg_bot.states.fsm_state_data import FSMFDSForm
from app.calculation.fds_tools.fds_utils import FDSTools


log = logging.getLogger(__name__)

fds_tools_router = Router()
fds_tools_router.message.filter(IsGuest())
fds_tools_router.callback_query.filter(IsGuest())

SFilterFDS = [FSMFDSForm.accept_document_state]


@fds_tools_router.callback_query(F.data.in_(['fds_tools', 'back_fds_tools']))
async def fire_risks_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    await state.set_state(state=None)
    text = i18n.fds_tools.text()
    # media = FSInputFile(r'temp_files/temp/fds_tools_logo.mp4')
    media = BufferedInputFile(
        file=get_picture_filling(file_path='temp_files/temp/fds_tools_logo.png'), filename="pic_filling")

    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        # media=InputMediaAnimation(media=media, caption=text),
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(1, 'fds_tools_density', 'general_menu', i18n=i18n))


@fds_tools_router.callback_query(F.data == 'fds_tools_density')
async def fds_tools_density_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback_data.message.chat.id)
    message_id = callback_data.message.message_id
    await state.update_data(chat_id=chat_id, fds_tools_mes_id=message_id)
    text = i18n.fds_tools_density.text()
    # media = get_picture_filling(file_path='temp_files/temp/fds_tools_dencity.png')
    media = BufferedInputFile(
        file=get_picture_filling(file_path='temp_files/temp/fds_tools_dencity.png'), filename="pic_filling")

    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        # media=InputMediaAnimation(media=media, caption=text),
        media=InputMediaPhoto(media=media, caption=text),
        reply_markup=get_inline_cd_kb(1, i18n=i18n, param_back=True, back_data='back_fds_tools'))
    await state.set_state(FSMFDSForm.accept_document_state)


@fds_tools_router.message(StateFilter(FSMFDSForm.accept_document_state))
async def input_fds_tools_document(message: Message, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    fds_tools_doc = message.document.file_id
    await state.update_data(fds_tools_doc=fds_tools_doc)
    await message.delete()
    data = await state.get_data()
    message_id = data.get('fds_tools_mes_id')
    text = i18n.request_start.text()
    await bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, i18n=i18n, param_back=True, back_data='back_fds_tools'))

    path = rf"temp_files/temp_data/{str(message.chat.id) + '_fds_tools'}.tsv"
    await bot.download(file=fds_tools_doc, destination=path)
    text = i18n.request_stop.text()
    await bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, i18n=i18n, param_back=True, back_data='back_fds_tools'))

    fds = FDSTools()
    times, densities, total_delta_sum = fds.open_file(
        file_paths=path)

    text = i18n.graph_is_drawn.text()
    await bot.edit_message_caption(
        chat_id=message.chat.id,
        message_id=message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, i18n=i18n, param_back=True, back_data='back_fds_tools'))

    plot_data = {"linewidth": 0.5, "drawstyle": "steps-post", "marker": 'o', "markersize": 0.5, "markeredgewidth": 1,
                 "markerfacecolor": "#1f77b4ff", 'markeredgecolor': "#1f77b4ff"}
    media = get_plot_graph(x_values=times,
                           y_values=densities,
                           x_label='Время, сек',
                           y_label='Плотность, м²/м²',
                           label='График плотности людского потока',
                           add_legend=True, loc_legend=1,
                           add_annotate=True, text_annotate=f"Время существования скоплений (tск*): {total_delta_sum:.1f} сек",
                           add_fill_between=True, param_fill=0.5, label_fill='Зона критической плотности', add_axhline=True, label_axline='Критическая плотность', plot_color="#00FF00ff", **plot_data)

    text = i18n.fds_tools.text()
    await bot.edit_message_media(
        chat_id=message.chat.id,
        message_id=message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"),
            caption=text),
        reply_markup=get_inline_cd_kb(1, i18n=i18n, param_back=True, back_data='back_fds_tools'))

    await state.set_state(state=None)


# @fds_tools_router.callback_query(StateFilter(FSMFDSForm.accept_document_state), F.data == 'fds_tools_density_plot')
# async def fds_tools_density_plot_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
#     path = rf"temp_files\temp_data\{str(callback_data.from_user.id) + '_fds_tools'}.tsv"
#     # data = await state.get_data()
#     # message_id = data.get('fds_tools_mes_id')
#     # file_path = data.get('fds_tools_doc')
#     # log.info(f"path: {path}")
#     text = i18n.fds_tools.text()

#     fds = FDSTools()
#     times, densities, total_delta_sum = fds.open_file_dialog(
#         file_paths=path)
#     plot_data = {"linewidth": 0.5, "drawstyle": "steps-post", "marker": 'o', "markersize": 0.5, "markeredgewidth": 1,
#                  "markerfacecolor": "#1f77b4ff", 'markeredgecolor': "#1f77b4ff"}
#     media = get_plot_graph(x_values=times,
#                            y_values=densities,
#                            x_label='Время, сек',
#                            y_label='Плотность, м²/м²',
#                            label='График плотности людского потока',
#                            add_legend=True, loc_legend=1,
#                            add_annotate=True, text_annotate=f"Время существования скоплений (tск*): {total_delta_sum:.1f} сек",
#                            add_fill_between=True, param_fill=0.5, label_fill='Зона критической плотности', add_axhline=True, label_axline='Критическая плотность', plot_color="#00FF00ff", **plot_data)

#     await bot.edit_message_media(
#         chat_id=callback_data.message.chat.id,
#         message_id=callback_data.message.message_id,
#         media=InputMediaPhoto(media=BufferedInputFile(
#             file=media, filename="pic_filling"), caption=text),
#         reply_markup=get_inline_cd_kb(1, i18n=i18n, param_back=True, back_data='back_fds_tools'))

#     await state.set_state(state=None)
