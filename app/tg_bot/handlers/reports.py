import logging
import io

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
# from aiogram.fsm.state import default_state  # , State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, CallbackQuery, Message, BufferedInputFile, InputMediaPhoto, InputMediaDocument, FSInputFile

from fluentogram import TranslatorRunner

from app.infrastructure.database.database.db import DB
from app.infrastructure.database.models.substance import FlammableMaterialModel
from app.infrastructure.database.models.users import UsersModel
from app.tg_bot.filters.filter_role import IsGuest, IsComrade
# from app.tg_bot.utilities.check_sub_admin import check_sub_admin
# from app.tg_bot.utilities.check_sub_member import check_sub_member
from app.tg_bot.states.fsm_state_data import FSMPromoCodeForm
from app.tg_bot.models.role import UserRole
from app.calculation.qra_mode.fire_risk_calculator import FireModel
from app.calculation.physics.accident_parameters import AccidentParameters

from app.calculation.reports.reports import get_data_fire_load, get_report_analytics_model
from app.tg_bot.utilities.misc_utils import get_picture_filling, get_plot_graph
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb


log = logging.getLogger(__name__)

report_router = Router()
report_router.message.filter(IsComrade)
report_router.callback_query.filter(IsComrade())


@report_router.callback_query(F.data.in_(['report_analytics_model', 'back_report_analytics_model']), StateFilter(default_state))
async def report_analytics_model_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    log.info('Запрос: Отчет. Аналитическая модель')
    data = await state.get_data()
    # subst = data.get('accident_bleve_sub')
    coef_k = float(data.get("accident_bleve_energy_fraction"))
    heat_capacity = float(
        data.get('accident_bleve_heat_capacity_liquid_phase'))
    mass = float(data.get('accident_bleve_mass_fuel'))
    temp_liq = float(data.get('accident_bleve_temperature_liquid_phase'))
    boiling_point = float(data.get('accident_bleve_boiling_point'))
    impuls_30 = round(
        float(data.get('accident_bleve_impuls_on_30m')), 2)
    distance = float(data.get('accident_bleve_distance'))
    acc_bleve = AccidentParameters(type_accident='accident_bleve')
    expl_energy = acc_bleve.compute_expl_energy(
        k=coef_k, Cp=heat_capacity, mass=mass, temp_liquid=temp_liq, boiling_point=boiling_point)
    reduced_mass = acc_bleve.compute_redused_mass(expl_energy=expl_energy)
    overpres, impuls, dist = acc_bleve.compute_overpres_inopen(
        reduced_mass=reduced_mass, distance_run=True, distance=distance)

    unit_i = i18n.get('pascal_in_sec')
    text_annotate = f" I+ = {impuls_30:.2e} {unit_i}"

    media = get_plot_graph(x_values=dist, y_values=impuls, ylim=impuls_30 * 4.0,
                           add_annotate=True,
                           text_annotate=text_annotate, x_ann=distance, y_ann=impuls_30,
                           label=i18n.get('plot_impuls_label'), x_label=i18n.get('distance_label'), y_label=i18n.get('plot_impuls_legend'),
                           add_legend=True, loc_legend=1)
    await state.set_state(state=None)
    # media = get_picture_filling(file_path='temp_files/temp/logo.png')

    get_report_analytics_model(name=role, file=io.BytesIO(media))

    file_data = FSInputFile(
        rf"temp_files/temp_data/report_analytics_model_{role.lower()}.docx")

    text = i18n.report_analytics_model.text()
    # await bot.edit_message_media(
    #     chat_id=callback.message.chat.id,
    #     message_id=callback.message.message_id,
    #     media=InputMediaPhoto(media=BufferedInputFile(
    #         file=media, filename="pic_filling"), caption=text),
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaDocument(media=file_data, caption=text),
        reply_markup=get_inline_cd_kb(1,
                                      'back_analytics_model',
                                      i18n=i18n, param_back=True, back_data='exit_to_analytics_model'))


@report_router.callback_query(F.data.in_(['export_data_standard_flammable_load']), StateFilter(default_state))
async def export_data_standard_flammable_load_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    log.info('Запрос: Экспорт данных горючей нагрузки')
    await state.set_state(state=None)
    data = await state.get_data()
    text = i18n.handbooks.text()
    name_sub = data.get('analytics_model_flammable_load')
    model = FireModel()
    model_data: FlammableMaterialModel = model.get_data_standard_flammable_load(
        name=name_sub)
    get_data_fire_load(
        file_path=r"locales/ru/static/Document_template_fireload.docx", subname=name_sub, data=model_data)
    file_data = FSInputFile(
        rf"temp_files/temp_data/flammable_load_{name_sub.lower()}.docx", filename=f'flammable_load_{name_sub.lower()}.docx')

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaDocument(media=file_data, caption=text),
        reply_markup=get_inline_cd_kb(i18n=i18n, param_back=True, back_data='back_standard_flammable_load'))
