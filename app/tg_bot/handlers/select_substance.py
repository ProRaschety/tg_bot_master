import logging
import io
import json

from dataclasses import dataclass, asdict, astuple

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
# , InlineQueryResultArticle, InputTextMessageContent
# from aiogram.types import InlineQuery
from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaPhoto

from fluentogram import TranslatorRunner

# from app.infrastructure.database.database.db import DB
from app.tg_bot.models.tables import DataFrameModel
from app.tg_bot.models.role import UserRole
from app.tg_bot.models.keyboard import InlineKeyboardModel
from app.tg_bot.filters.filter_role import IsGuest, IsSubscriber
from app.tg_bot.states.fsm_state_data import FSMFireAccidentForm, FSMEditForm

from app.tg_bot.utilities import tables
from app.tg_bot.utilities.tables import DataFrameBuilder
from app.tg_bot.utilities.misc_utils import get_data_table, get_plot_graph, get_dataframe_table
from app.tg_bot.utilities.misc_utils import compute_value_with_eval, check_string, count_decimal_digits, count_zeros_and_digits, result_formatting, count_digits_before_dot, custom_round, modify_dict_value
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_keypad, get_inline_keyboard

from app.infrastructure.database.models.calculations import AccidentModel
from app.calculation.physics.physics_utils import get_property_fuel
from app.infrastructure.database.models.substance import FlammableMaterialModel, SubstanceModel


from pprint import pprint

log = logging.getLogger(__name__)

select_substance_router = Router()
select_substance_router.message.filter(IsSubscriber())
select_substance_router.callback_query.filter(IsSubscriber())

# select_substance_router_filter = [FSMEditForm.select_substance_state]


@select_substance_router.callback_query(F.data.in_(['edit_substance']))
async def edit_substance_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner) -> None:
    context_data = await state.get_data()

    list_sibstance = ['gasoline', 'diesel', 'LNG',
                      'LPG', 'liq_hydrogen', 'any_substance']

    text = 'Выберите вещество из списка или введите параметры произвольного вещества'
    kb = InlineKeyboardModel(**context_data['keyboard_model'])
    await bot.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        caption=text,
        reply_markup=get_inline_cd_kb(1,
                                      *list_sibstance,
                                      i18n=i18n,
                                      back_data=kb.ultimate,
                                      )
    )
    # await state.set_state(FSMEditForm.select_substance_state)


@select_substance_router.callback_query(F.data.in_(['gasoline', 'diesel', 'LNG', 'LPG', 'liq_hydrogen', 'other_liquid', 'any_substance']))
async def select_substance_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner,) -> None:

    context_data = await state.get_data()
    call_data = callback.data
    log.info(
        f"Request select substance handler from: {i18n.get(context_data.get('temporary_request'))}")

    molar_mass, boling_point, mass_burning_rate, LFL = await get_property_fuel(subst=call_data)
    substance = SubstanceModel(substance_name='',
                               molar_mass=molar_mass,
                               boiling_point=boling_point,
                               mass_burning_rate=mass_burning_rate,
                               lower_flammability_limit=LFL)

    context_data = await state.get_data()
    accident_model = AccidentModel(**context_data.get('accident_model'))
    accident_model.substance_name = call_data
    accident_model.substance = substance
    await state.update_data(accident_model=asdict(accident_model),)

    context_data = await state.get_data()

    requests = {
        'fire_flash': AccidentModel,
        'fire_pool': AccidentModel,
        'cloud_explosion': AccidentModel,
        'fire_ball': AccidentModel,
        'accident_bleve': AccidentModel,
        'horizontal_jet': AccidentModel,
        'vertical_jet': AccidentModel,
        'standard_flammable_load': FlammableMaterialModel,
        'handbooks': SubstanceModel,
    }

    model = requests[context_data.get('temporary_request', None)](
        **context_data.get('accident_model'))

    dfb = DataFrameBuilder(i18n=i18n,  request=context_data.get(
        'temporary_request'), model=model)
    dataframe = dfb.action_request()
    media = get_dataframe_table(data=dataframe)

    kb = InlineKeyboardModel(**context_data['keyboard_model'])

    # text = i18n.temporary_parameter.text(
    #     text=i18n.get('name_' + context_data.get('temporary_text')), value=equals_result)
    text = f'{call_data}'
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename='pic_filling'), caption=text),
        reply_markup=get_inline_keyboard(keyboard=kb, i18n=i18n,
                                         )
    )

    await state.update_data(temporary_parameter='')
    # await state.update_data(temporary_request='')
    await state.update_data(temporary_text='')
    await state.set_state(state=None)
