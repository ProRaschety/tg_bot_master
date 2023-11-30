import logging

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.utils.chat_action import ChatActionSender
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message, FSInputFile, InputMediaPhoto, InputFile

from fluentogram import TranslatorRunner

from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb
from app.tg_bot.utilities.misc_utils import get_temp_folder
from app.infrastructure.substance_data.substance import SubstanceDB

import json

logger = logging.getLogger(__name__)
logger = logging.getLogger('matplotlib').setLevel(logging.ERROR)
logger = logging.getLogger('PIL.PngImagePlugin').setLevel(logging.ERROR)


data_base_req_router = Router()


@data_base_req_router.message(Command(commands=["data_base"]))
async def process_get_data_base(message: Message, bot: Bot, i18n: TranslatorRunner) -> None:
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.UPLOAD_PHOTO)

    chat_id = str(message.chat.id)
    q_keys = SubstanceDB(chat_id)
    name_dir = q_keys.get_diagram_sankey()
    media = FSInputFile(str(name_dir))
    text = i18n.data_base(quantity_keys=q_keys.get_quantity_keys())
    await message.answer_photo(
        photo=media,
        caption=text,
        has_spoiler=False,
        reply_markup=get_inline_cd_kb(4,
                                      'one_nine',
                                      'EN_alphabet',
                                      'alfa_omega',
                                      'RUS_alphabet',
                                      'general_menu',
                                      i18n=i18n))


@data_base_req_router.callback_query(F.data == 'back_to_list')
async def back_to_list_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = callback.message.chat.id

    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=get_inline_cd_kb(4,
                                      'one_nine',
                                      'EN_alphabet',
                                      'alfa_omega',
                                      'RUS_alphabet',
                                      'general_menu',
                                      i18n=i18n))
    await callback.answer('')


@data_base_req_router.callback_query(F.data == 'RUS_alphabet')
async def rus_alphabet_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = callback.message.chat.id

    text = i18n.RUS_alphabet.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(5, 'rus_1', 'rus_2', 'rus_3', 'rus_4', 'rus_5',
                                         'rus_6', 'rus_7', 'rus_8', 'rus_9', 'rus_10',
                                         'rus_11', 'rus_12', 'rus_13', 'rus_14', 'rus_15',
                                         'rus_16', 'rus_17', 'rus_18', 'rus_19', 'rus_20',
                                         'rus_21', 'rus_22', 'rus_23', 'rus_24', 'rus_25',
                                         'rus_26', 'rus_27', 'rus_28', 'rus_29', 'rus_30',
                                         'back_to_list',
                                         i18n=i18n))
    await callback.answer('')


@data_base_req_router.callback_query(F.data == 'one_nine')
async def one_nine_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = callback.message.chat.id

    text = i18n.one_nine.text()

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'back_to_list', i18n=i18n))
    await callback.answer('')


@data_base_req_router.callback_query(F.data == 'EN_alphabet')
async def en_alphabet_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = callback.message.chat.id

    text = i18n.EN_alphabet.text()

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'back_to_list', i18n=i18n))
    await callback.answer('')


@data_base_req_router.callback_query(F.data == 'alfa_omega')
async def alfa_omega_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = callback.message.chat.id

    text = i18n.alfa_omega.text()

    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'back_to_list', i18n=i18n))
    await callback.answer('')

# @data_base_req_router.callback_query(F.data == 'List_sub')
# async def select_substance(callback_data: CallbackQuery):
#     data = callback_data.data
#     with open('data_base\combustible_gas.json', 'r', encoding='utf-8') as file_r_gas:
#         db_gas = json.load(file_r_gas)
#     with open('data_base\combustible_liquid.json', 'r', encoding='utf-8') as file_r_liquid:
#         db_liquid = json.load(file_r_liquid)
#     with open('data_base\combustible_dust.json', 'r', encoding='utf-8') as file_r_dust:
#         db_dust = json.load(file_r_dust)
#     List_sub = list(db_gas.keys())+list(db_liquid.keys())+list(db_dust.keys())
#     quantity_keys = len(List_sub)

#     # проверяем в каком словаре данный ключ
#     if db_gas.get(data) is not None:
#         substance_name = db_gas[data]['substance_name'][0]
#         molecular_formula = db_gas[data]['molecular_formula'][0]
#         molecular_weight = db_gas[data]['molecular_weight'][0]
#         atoms_nC = db_gas[data]['atoms_nC'][0]
#         atoms_nH = db_gas[data]['atoms_nH'][0]
#         atoms_nO = db_gas[data]['atoms_nO'][0]
#         atoms_nX = db_gas[data]['atoms_nX'][0]
#         const_ant_a = db_gas[data]['const_ant_a'][0]
#         const_ant_b = db_gas[data]['const_ant_b'][0]
#         const_ant_ca = db_gas[data]['const_ant_ca'][0]
#         substance_type = db_gas[data]['substance_type'][0]
#         lower_flammability_limit = db_gas[data]['lower_flammability_limit'][0]
#         temperature_flash = db_gas[data]['temperature_flash'][0]
#         temperature_spon_combustion = db_gas[data]['temperature_spon_combustion'][0]
#         heat_of_burn = db_gas[data]['heat_of_burn'][0]
#         const_ant_in_temp = db_gas[data]['const_ant_in_temp'][0]
#         burning_rate = db_gas[data]['burning_rate'][0]
#         s = db_gas[data]['source'][0]
#         source = s.replace('*', '\n')

#     if db_liquid.get(data) is not None:
#         substance_name = db_liquid[data]['substance_name'][0]
#         molecular_formula = db_liquid[data]['molecular_formula'][0]
#         molecular_weight = db_liquid[data]['molecular_weight'][0]
#         atoms_nC = db_liquid[data]['atoms_nC'][0]
#         atoms_nH = db_liquid[data]['atoms_nH'][0]
#         atoms_nO = db_liquid[data]['atoms_nO'][0]
#         atoms_nX = db_liquid[data]['atoms_nX'][0]
#         const_ant_a = db_liquid[data]['const_ant_a'][0]
#         const_ant_b = db_liquid[data]['const_ant_b'][0]
#         const_ant_ca = db_liquid[data]['const_ant_ca'][0]
#         substance_type = db_liquid[data]['substance_type'][0]
#         lower_flammability_limit = db_liquid[data]['lower_flammability_limit'][0]
#         temperature_flash = db_liquid[data]['temperature_flash'][0]
#         temperature_spon_combustion = db_liquid[data]['temperature_spon_combustion'][0]
#         heat_of_burn = db_liquid[data]['heat_of_burn'][0]
#         const_ant_in_temp = db_liquid[data]['const_ant_in_temp'][0]
#         burning_rate = db_liquid[data]['burning_rate'][0]
#         s = db_liquid[data]['source'][0]
#         source = s.replace('*', '\n')

#     if db_dust.get(data) is not None:
#         substance_name = db_dust[data]['substance_name'][0]
#         molecular_formula = db_dust[data]['molecular_formula'][0]
#         molecular_weight = db_dust[data]['molecular_weight'][0]
#         atoms_nC = db_dust[data]['atoms_nC'][0]
#         atoms_nH = db_dust[data]['atoms_nH'][0]
#         atoms_nO = db_dust[data]['atoms_nO'][0]
#         atoms_nX = db_dust[data]['atoms_nX'][0]
#         const_ant_a = db_dust[data]['const_ant_a'][0]
#         const_ant_b = db_dust[data]['const_ant_b'][0]
#         const_ant_ca = db_dust[data]['const_ant_ca'][0]
#         substance_type = db_dust[data]['substance_type'][0]
#         lower_flammability_limit = db_dust[data]['lower_flammability_limit'][0]
#         temperature_flash = db_dust[data]['temperature_flash'][0]
#         temperature_spon_combustion = db_dust[data]['temperature_spon_combustion'][0]
#         heat_of_burn = db_dust[data]['heat_of_burn'][0]
#         const_ant_in_temp = db_dust[data]['const_ant_in_temp'][0]
#         burning_rate = db_dust[data]['burning_rate'][0]
#         s = db_dust[data]['source'][0]
#         source = s.replace('*', '\n')

#     type_substance = substance_type
#     if type_substance == 'ЛВЖ' or type_substance == 'ГЖ' or type_substance == 'ГГ' or type_substance == 'ГП':
#         str_name = str(f'\u2139   <b>{substance_name}</b>\n'
#                        f'\n'
#                        f'<i>Физико-химические свойства</i>\n'
#                        f'Молекулярная формула: <b>{molecular_formula}</b>\n'
#                        f'Молярная масса: <b>{molecular_weight} кг/кмоль</b>\n'
#                        f'Плотность: <b>{molecular_weight} кг/м\u00B3</b>\n'
#                        f'Константа уравнения Антуана "А": <b>{const_ant_a}</b>\n'
#                        f'Константа уравнения Антуана "B": <b>{const_ant_b}</b>\n'
#                        f'Константа уравнения Антуана "Ca": <b>{const_ant_ca}</b>\n'
#                        f'Температурный интервал\n'
#                        f'значений констант уравнения Антуана: <b>{const_ant_in_temp} \u00B0С</b>\n'
#                        f'Нижний концентрационный\n'
#                        f'предел распространения пламени: <b>{lower_flammability_limit} % (об.)</b>\n'
#                        f'Температура вспышки: <b>{temperature_flash} \u00B0С</b>\n'
#                        f'Температура самовоспламенения: <b>{temperature_spon_combustion} \u00B0С</b>\n'
#                        f'Теплота сгорания: <b>{heat_of_burn} кДж/кг</b>\n'
#                        f'\n'
#                        f'<i>Источник</i>\n'
#                        f'<b>{source}</b>\n')

#     else:
#         str_name = 'нет такого вещества'

#     db_select_sub_kb_button = InlineKeyboardButton(text='\u2B05 Назад', callback_data='А...Я')
#     db_select_sub_kb = InlineKeyboardMarkup(inline_keyboard=[[db_select_sub_kb_button]])

#     await bot.edit_message_text(chat_id=callback_data.message.chat.id,
#                                 message_id=callback.message.message_id,
#                                 text=str_name,
#                                 reply_markup=db_select_sub_kb)
