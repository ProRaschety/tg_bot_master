import logging

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state  # , State, StatesGroup
from aiogram.types import CallbackQuery, Message, BufferedInputFile, InputMediaPhoto

from fluentogram import TranslatorRunner

from app.infrastructure.database.database.db import DB
from app.infrastructure.database.models.users import UsersModel
from app.tg_bot.filters.filter_role import IsGuest
# from app.tg_bot.utilities.check_sub_admin import check_sub_admin
# from app.tg_bot.utilities.check_sub_member import check_sub_member
from app.tg_bot.utilities.misc_utils import get_picture_filling
from app.tg_bot.keyboards.kb_builder import get_inline_cd_kb, get_inline_url_kb
from app.tg_bot.states.fsm_state_data import FSMPromoCodeForm
from app.tg_bot.models.role import UserRole


log = logging.getLogger(__name__)

user_router = Router()
user_router.message.filter(IsGuest())
user_router.callback_query.filter(IsGuest())


@user_router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    media = get_picture_filling(
        file_path='temp_files/temp/logo_fe_start.png')
    if role == "subscriber":
        main_kb = ['handbooks', 'tools', 'fire_resistance_guest',
                   'fire_risks', 'fire_category']
        text = i18n.start_subscriber.menu()
    elif role == "comrade":
        main_kb = ['handbooks', 'tools', 'fire_resistance',
                   'fire_risks', 'fire_category']
        text = i18n.start.menu()
    elif role == "admin":
        main_kb = ['handbooks', 'tools', 'fire_resistance',
                   'fire_risks', 'fire_category', 'admin_panel']
        text = i18n.start.menu()
    elif role == "owner":
        main_kb = ['handbooks', 'tools', 'fire_resistance',
                   'fire_risks', 'fire_category', 'admin_panel', 'owner_panel']
        text = i18n.start.menu()
    else:
        main_kb = ['handbooks', 'tools_guest', 'fire_resistance_guest',
                   'fire_risks', 'fire_category_guest']
        text = i18n.start_guest.menu()
    await message.answer_photo(
        photo=BufferedInputFile(file=media, filename="pic_filling.png"),
        caption=text,
        reply_markup=get_inline_cd_kb(1, *main_kb, i18n=i18n))
    await state.set_state(state=None)
    await message.delete()


@user_router.callback_query(F.data == 'general_menu')
async def general_menu_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    media = get_picture_filling(
        file_path='temp_files/temp/logo_fe_start.png')
    if role == "subscriber":
        main_kb = ['handbooks', 'tools', 'fire_resistance_guest',
                   'fire_risks', 'fire_category']
        text = i18n.start_subscriber.menu()
    elif role == "comrade":
        main_kb = ['handbooks', 'tools', 'fire_resistance',
                   'fire_risks', 'fire_category']
        text = i18n.start.menu()
    elif role == "admin":
        main_kb = ['handbooks', 'tools', 'fire_resistance',
                   'fire_risks', 'fire_category', 'admin_panel']
        text = i18n.start.menu()
    elif role == "owner":
        main_kb = ['handbooks', 'tools', 'fire_resistance',
                   'fire_risks', 'fire_category', 'admin_panel', 'owner_panel']
        text = i18n.start.menu()
    else:
        main_kb = ['handbooks', 'tools_guest', 'fire_resistance_guest',
                   'fire_risks', 'fire_category_guest']
        text = i18n.start_guest.menu()
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, *main_kb, i18n=i18n))
    await state.set_state(state=None)


@user_router.callback_query(F.data.in_(['tools_guest', 'fire_resistance_guest', 'fire_risks_guest', 'fire_category_guest', 'substances_guest', "to_cities_guest"]))
async def fire_resistance_guest_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    media = get_picture_filling(
        file_path='temp_files/temp/logo_fe_start.png')
    if role == "subscriber":
        main_kb = ['handbooks', 'tools', 'fire_resistance_guest',
                   'fire_risks', 'fire_category']
        text = i18n.subscriber.menu(button=i18n.get(callback_data.data))
    elif role == "comrade":
        main_kb = ['handbooks', 'tools', 'fire_resistance',
                   'fire_risks', 'fire_category']

    elif role == "admin":
        main_kb = ['handbooks', 'tools', 'fire_resistance',
                   'fire_risks', 'fire_category', 'admin_panel']
        text = i18n.start.menu()
    elif role == "owner":
        main_kb = ['handbooks', 'tools', 'fire_resistance',
                   'fire_risks', 'fire_category', 'admin_panel', 'owner_panel']
        text = i18n.start.menu()
    else:
        main_kb = ['handbooks', 'tools_guest', 'fire_resistance_guest',
                   'fire_risks', 'fire_category_guest']
        text = i18n.guest.menu(button=i18n.get(callback_data.data))
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, *main_kb, i18n=i18n))
    await state.set_state(state=None)


@user_router.message(Command(commands=["setlevel"]))
async def process_set_level(message: Message, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole, db: DB) -> None:
    media = get_picture_filling(
        file_path='temp_files/temp/logo_fe_start.png')
    user_record: UsersModel = await db.users.get_user_record(user_id=message.chat.id)
    dict_role = {'guest': 'Гость',
                 'subscriber': 'Подписчик',
                 'comrade': 'Коллега',
                 'admin': 'Администратор',
                 'owner': 'Владелец'}

    text = i18n.setlevel.text(role_user=dict_role.get(
        str(user_record.role), 'Неизвестно'))

    if role == 'subscriber':
        keyboad = ['select_tariff', 'enter_promo_code', 'general_menu']
    else:
        keyboad = ['select_tariff', 'enter_promo_code',
                   'subscribe_channel', 'general_menu',]
    await message.answer_photo(
        photo=BufferedInputFile(file=media, filename="pic_filling.png"),
        caption=text,
        reply_markup=get_inline_cd_kb(1, *keyboad, i18n=i18n))
    await message.delete()


@user_router.callback_query(F.data.in_(['back_setlevel', 'update_role']))
async def back_setlevel_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole, db: DB) -> None:
    media = get_picture_filling(
        file_path='temp_files/temp/logo_fe_start.png')
    user_record: UsersModel = await db.users.get_user_record(user_id=callback.message.chat.id)
    dict_role = {'guest': 'Гость',
                 'subscriber': 'Подписчик',
                 'comrade': 'Коллега',
                 'admin': 'Администратор',
                 'owner': 'Владелец'}

    text = i18n.setlevel.text(role_user=dict_role.get(
        str(user_record.role), 'Неизвестно'))
    if role == 'subscriber':
        keyboad = ['select_tariff', 'enter_promo_code', 'general_menu']
    else:
        keyboad = ['select_tariff', 'enter_promo_code',
                   'subscribe_channel', 'general_menu']
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, *keyboad, i18n=i18n))


@user_router.callback_query(F.data == 'enter_promo_code')
async def enter_promo_code_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    message_id = callback.message.message_id
    await state.update_data(mes_promocode_id=message_id)
    media = get_picture_filling(
        file_path='temp_files/temp/logo_fe_start.png')
    text = i18n.enter_promo_code.text()
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, 'cansel_enter_promo_code', i18n=i18n))
    await state.set_state(state=FSMPromoCodeForm.promo_code_state)


@user_router.message(StateFilter(FSMPromoCodeForm.promo_code_state))
async def promo_code_input(message: Message, bot: Bot, state: FSMContext, i18n: TranslatorRunner, db: DB) -> None:
    promocode = message.text
    await db.users.update_promocode(user_id=message.chat.id, promocode=promocode.lower())
    await message.delete()
    media = get_picture_filling(
        file_path='temp_files/temp/logo_fe_start.png')
    data = await state.get_data()
    message_id = data.get('mes_promocode_id')

    user_promocode = dict(await db.promocode.get_valid_promocode_user(promocode=promocode.lower()))
    if user_promocode.get('count') != 0:
        text = i18n.entering_code.text(user_code=promocode)
        keyboard = ['update_role']
    else:
        text = i18n.no_such_in_database()
        keyboard = ['enter_promo_code', 'cansel_enter_promo_code']

    await state.set_state(state=None)
    await bot.edit_message_media(
        chat_id=message.chat.id,
        message_id=message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, *keyboard, i18n=i18n))


@user_router.callback_query(F.data == 'cansel_enter_promo_code')
async def cansel_enter_promo_code_call(callback: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole, db: DB) -> None:
    media = get_picture_filling(
        file_path='temp_files/temp/logo_fe_start.png')
    user_record: UsersModel = await db.users.get_user_record(user_id=callback.message.chat.id)
    dict_role = {'guest': 'Гость',
                 'subscriber': 'Подписчик',
                 'comrade': 'Коллега',
                 'admin': 'Администратор',
                 'owner': 'Владелец'}

    text = i18n.setlevel.text(role_user=dict_role.get(
        str(user_record.role), 'Неизвестно'))
    if role == 'subscriber':
        keyboad = ['select_tariff', 'enter_promo_code', 'general_menu']
    else:
        keyboad = ['select_tariff', 'enter_promo_code',
                   'subscribe_channel', 'general_menu']
    await bot.edit_message_media(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_cd_kb(1, *keyboad, i18n=i18n))
    await state.set_state(state=None)


@user_router.callback_query(F.data == 'subscribe_channel')
async def subscribe_channel_call(callback_data: CallbackQuery, bot: Bot, state: FSMContext, i18n: TranslatorRunner, role: UserRole) -> None:
    media = get_picture_filling(
        file_path='temp_files/temp/logo_fe_start.png')
    text = i18n.subscribe_channel.text()
    await bot.edit_message_media(
        chat_id=callback_data.message.chat.id,
        message_id=callback_data.message.message_id,
        media=InputMediaPhoto(media=BufferedInputFile(
            file=media, filename="pic_filling"), caption=text),
        reply_markup=get_inline_url_kb(1, i18n=i18n, param_back=True, back_data="back_setlevel", channel_1="channel_1-text", channel_2="channel_2-text"))
    await state.set_state(state=None)


@user_router.message(Command(commands=["contacts"]))
async def process_get_admin_contacts(message: Message, state: FSMContext, i18n: TranslatorRunner) -> None:
    dict_kb = {"link_owner": "link_owner-text", "link_1": "link_1-text"}
    media = get_picture_filling(
        file_path='temp_files/temp/logo_fe_start.png')
    text = i18n.contacts.admin()
    await message.answer_photo(
        photo=BufferedInputFile(file=media, filename="pic_filling.png"),
        caption=text, reply_markup=get_inline_url_kb(1, i18n=i18n, param_back=True, back_data="general_menu", ** dict_kb))
    await state.set_state(state=None)
    await message.delete()


@user_router.message(Command(commands=["cansel"]), StateFilter(default_state))
async def process_cancel_command(message: Message, i18n: TranslatorRunner) -> None:
    await message.answer(text=i18n.cansel.input())


@user_router.message(Command(commands=["cansel"]), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, i18n: TranslatorRunner, state: FSMContext) -> None:
    await message.answer(text=i18n.cansel.state())
    await state.set_state(state=None)
    await message.delete()
