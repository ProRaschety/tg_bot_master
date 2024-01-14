import logging
import json

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.chat_action import ChatActionSender
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message, FSInputFile, InputMediaPhoto, InputFile, BufferedInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from fluentogram import TranslatorRunner

from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb, get_inline_sub_kb, SubCallbackFactory
from app.tg_bot.utilities.misc_utils import get_temp_folder
from app.tg_bot.states.fsm_state_data import FSMSubstanceForm
from app.calculation.database_mode.substance import SubstanceDB

log = logging.getLogger(__name__)
# logger = logging.getLogger(__name__)
# logger = logging.getLogger('matplotlib').setLevel(logging.ERROR)
# logger = logging.getLogger('PIL.PngImagePlugin').setLevel(logging.ERROR)


data_base_req_router = Router()


@data_base_req_router.callback_query(F.data.in_(["substances"]), StateFilter(default_state))
async def process_get_data_base(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    log.info('Запрос: Справочник веществ')
    chat_id = str(callback.message.chat.id)
    await callback.message.bot.send_chat_action(
        chat_id=chat_id,
        action=ChatAction.UPLOAD_PHOTO)

    q_keys = SubstanceDB(i18n=i18n, chat_id=chat_id)
    media = q_keys.get_diagram_sankey()

    text = i18n.data_base(quantity_keys=q_keys.get_quantity_keys())

    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(2,
                                      'one_nine',
                                      'EN_alphabet',
                                      'alfa_omega',
                                      'RUS_alphabet',
                                      'data_base_search',
                                      'data_base_inline_search',
                                      'general_menu',
                                      i18n=i18n))


@data_base_req_router.callback_query(F.data == 'data_base_inline_search')
async def data_base_inline_search_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    message_id = callback.message.message_id
    await state.update_data(sub_chat_id=chat_id, sub_message_id=message_id)
    text = i18n.data_base_inline_search.text()
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text="Начать поиск", switch_inline_query_current_chat="")]])
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=markup)
    await state.set_state(FSMSubstanceForm.database_inline_state)


@data_base_req_router.inline_query(StateFilter(FSMSubstanceForm.database_inline_state))
async def show_substances(inline_query: InlineQuery, state: FSMContext, i18n: TranslatorRunner):
    q_keys = SubstanceDB(i18n=i18n)
    list_sub = q_keys.get_list_substances()
    results = []
    for name in list_sub:
        if inline_query.query in str(name):
            results.append(InlineQueryResultArticle(id=str(name), title=f'{name}',
                                                    input_message_content=InputTextMessageContent(message_text=f'{name}')))
    await inline_query.answer(results=results[:20], cache_time=0, is_personal=True)


@data_base_req_router.message(StateFilter(FSMSubstanceForm.database_inline_state))
async def data_base_search_input(message: Message, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    data = await state.get_data()
    chat_id = data.get('sub_chat_id')
    message_id = data.get('sub_message_id')
    word_search = message.text
    q_keys = SubstanceDB(i18n=i18n, chat_id=chat_id, word_search=word_search)
    media = q_keys.get_diagram_sankey()
    word_keys = q_keys.get_word_search_result()
    dict_word = {key: key for key in word_keys}
    text = i18n.data_base_search_result(
        word_search=word_search, word_search_quan=len(word_keys))
    await message.delete()
    await bot.edit_message_media(
        chat_id=message.chat.id,
        message_id=message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="fig_sankey"), caption=text),
        reply_markup=get_inline_sub_kb(2, i18n=i18n, param_back=True, back_data="back_to_list", ** dict_word))
    await state.set_state(FSMSubstanceForm.database_edit_state)


@data_base_req_router.callback_query(F.data == 'data_base_search')
async def data_base_search_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.data_base_search.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      'cansel_search_database',
                                      i18n=i18n))
    await state.set_state(FSMSubstanceForm.database_search_state)


@data_base_req_router.callback_query(StateFilter(FSMSubstanceForm.database_search_state), F.data == 'cansel_search_database')
async def cansel_search_database_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.data_base_search.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(4,
                                      'one_nine',
                                      'EN_alphabet',
                                      'alfa_omega',
                                      'RUS_alphabet',
                                      'data_base_search',
                                      'general_menu',
                                      i18n=i18n))
    await state.set_state(state=None)


@data_base_req_router.callback_query(StateFilter(FSMSubstanceForm.database_edit_state), F.data == 'cansel_search_database')
async def cansel_search_database_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.data_base_search.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(4,
                                      'one_nine',
                                      'EN_alphabet',
                                      'alfa_omega',
                                      'RUS_alphabet',
                                      'data_base_search',
                                      'general_menu',
                                      i18n=i18n))
    await state.set_state(state=None)


@data_base_req_router.message(StateFilter(FSMSubstanceForm.database_search_state))
async def data_base_search_input(message: Message, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(message.chat.id)
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING)

    word_search = message.text

    q_keys = SubstanceDB(i18n=i18n, chat_id=chat_id, word_search=word_search)
    fig_sankey = q_keys.get_diagram_sankey()
    word_keys = q_keys.get_word_search_result()
    dict_word = {key: key for key in word_keys}

    text = i18n.data_base_search_result(
        word_search=word_search, word_search_quan=len(word_keys))
    await message.answer_photo(
        photo=BufferedInputFile(
            file=fig_sankey, filename="fig_sankey"),
        caption=text,
        has_spoiler=False,
        reply_markup=get_inline_sub_kb(2, i18n=i18n, param_back=True, back_data="back_to_list", ** dict_word))

    await state.set_state(FSMSubstanceForm.database_edit_state)
    await message.delete()


# @data_base_req_router.message(StateFilter(FSMSubstanceForm.database_search_state))
# async def data_base_search_upload(message: Message, state: FSMContext, i18n: TranslatorRunner) -> None:
#     chat_id = str(message.chat.id)
#     await message.bot.send_chat_action(
#         chat_id=message.chat.id,
#         action=ChatAction.TYPING)
#     action_sender = ChatActionSender(
#         bot=message.bot, chat_id=message.chat.id, action=ChatAction.TYPING
#     )
#     async with action_sender:
#         await data_base_search_input(message, state, i18n)


@data_base_req_router.callback_query(F.data == 'back_to_list')
async def back_to_list_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    q_keys = SubstanceDB(i18n=i18n, chat_id=chat_id)
    text = i18n.data_base(quantity_keys=q_keys.get_quantity_keys())
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(2,
                                      'one_nine',
                                      'EN_alphabet',
                                      'alfa_omega',
                                      'RUS_alphabet',
                                      'data_base_search',
                                      'data_base_inline_search',
                                      'general_menu',
                                      i18n=i18n))
    await state.set_state(state=None)


@data_base_req_router.callback_query(F.data == 'back_to_list_rus')
async def back_to_list_rus_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    num_let = 1
    text = i18n.RUS_alphabet.text(rus_letters=num_let)
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


@data_base_req_router.callback_query(F.data == 'RUS_alphabet')
async def rus_alphabet_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    # data = 'rus_1'
    # rus_keys = SubstanceDB(chat_id=chat_id, i18n=i18n, data=data)
    # list_rus = rus_keys.get_rus_alphabet_quan(i18n=i18n)
    num_let = 0
    text = i18n.RUS_alphabet.text(rus_letters=num_let)
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


@data_base_req_router.callback_query(F.data == 'one_nine')
async def one_nine_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.one_nine.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'back_to_list', i18n=i18n))


@data_base_req_router.callback_query(F.data == 'EN_alphabet')
async def en_alphabet_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    text = i18n.EN_alphabet.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'back_to_list', i18n=i18n))


@data_base_req_router.callback_query(F.data == 'alfa_omega')
async def alfa_omega_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    text = i18n.alfa_omega.text()
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'back_to_list', i18n=i18n))


@data_base_req_router.callback_query(F.data.in_(['rus_1', 'rus_2', 'rus_3', 'rus_4', 'rus_5',
                                                 'rus_6', 'rus_7', 'rus_8', 'rus_9', 'rus_10',
                                                 'rus_11', 'rus_12', 'rus_13', 'rus_14', 'rus_15',
                                                 'rus_16', 'rus_17', 'rus_18', 'rus_19', 'rus_20',
                                                 'rus_21', 'rus_22', 'rus_23', 'rus_24', 'rus_25',
                                                 'rus_26', 'rus_27', 'rus_28', 'rus_29', 'rus_30']))
async def select_substance_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    data = i18n.get(callback.data)
    rus_keys = SubstanceDB(chat_id=chat_id, data=data, i18n=i18n)
    list_rus = rus_keys.get_rus_alphabet()
    dict_rus = {key: key for key in list_rus}
    # dict_rus.update({'back_to_list': i18n.get('back_to_list')})
    text = i18n.data_base_rus(rus_letter=data, list_rus=len(list_rus))
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        # reply_markup=get_inline_cd_kb(2, i18n=i18n, param_back=True, back_data="back_to_list_rus", ** dict_rus))
        reply_markup=get_inline_sub_kb(2, i18n=i18n, param_back=True, back_data="back_to_list_rus", ** dict_rus))
    await state.set_state(FSMSubstanceForm.database_edit_state)


@data_base_req_router.callback_query(StateFilter(FSMSubstanceForm.database_edit_state), SubCallbackFactory.filter())
async def select_substance_call(callback: CallbackQuery, callback_data: SubCallbackFactory, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    substance_name = callback.data[4:]
    rus_keys = SubstanceDB(chat_id=chat_id, data=substance_name, i18n=i18n)
    list_sub = rus_keys.get_substance_data()
    text = i18n.data_base_report(substance_full_name=list_sub[0].upper(),
                                 substance_synonym=list_sub[1],
                                 molecular_formula=list_sub[2],
                                 molecular_weight=list_sub[3],
                                 const_ant_a=list_sub[8],
                                 const_ant_b=list_sub[9],
                                 const_ant_ca=list_sub[10],
                                 lower_flammability_limit=list_sub[13],
                                 temperature_flash=list_sub[14],
                                 temperature_spon_combustion=list_sub[15],
                                 heat_of_burn=list_sub[16],
                                 const_ant_in_temp=list_sub[11],
                                 extinguishin_agents=list_sub[19],
                                 description_substance=list_sub[20],
                                 density=list_sub[17],
                                 source=list_sub[-1])
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1, 'back_to_list', i18n=i18n))
    await state.set_state(state=None)


@data_base_req_router.callback_query(F.data == 'export_data_substance')
async def export_data_steel_call(callback: CallbackQuery, bot: Bot, i18n: TranslatorRunner) -> None:
    chat_id = str(callback.message.chat.id)
    text = i18n.export_data_substance.text()
    name_file = f"out_file_property_{chat_id}.csv"
    directory = get_temp_folder(fold_name='temp_data')
    file_csv = get_csv_file(data=data, name_file=name_dir)
    media = FSInputFile(str(name_dir))
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaDocument(media=media, caption=text),
        reply_markup=get_inline_cd_kb(1, 'back_to_list_rus', i18n=i18n))
