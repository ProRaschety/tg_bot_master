import logging

from fluentogram import TranslatorRunner

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# from app.tg_bot.models.role import UserRole


log = logging.getLogger(__name__)


# Функция для формирования инлайн-клавиатуры на лету
def get_inline_cd_kb(width: int = 1,
                     *args: str,
                     i18n: TranslatorRunner,
                     param_back: bool | None = False,
                     back_data: str | None = None,
                     switch: bool | None = False,
                     switch_data: str | None = None,
                     switch_text: str | None = None,
                     check_role: bool | None = False,
                     role: str | None = None,
                     **kwargs: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []
    # Заполняем список кнопками из аргументов args и kwargs

    if args:
        if check_role:
            if role == 'guest':
                for button in args:
                    buttons.append(InlineKeyboardButton(
                        text=i18n.get(button + '_guest'),
                        callback_data=button + '_guest'))
            else:
                for button in args:
                    buttons.append(InlineKeyboardButton(
                        text=i18n.get(button),
                        callback_data=button))
        else:
            for button in args:
                buttons.append(InlineKeyboardButton(
                    text=i18n.get(button),
                    callback_data=button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))
    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)

    if switch:
        kb_builder.row(InlineKeyboardButton(
            text=i18n.get(switch_text), switch_inline_query_current_chat=switch_data), width=1)

    if param_back:
        kb_builder.row(InlineKeyboardButton(
            text=i18n.get(back_data), callback_data=back_data), width=1)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


def get_inline_url_kb(width: int,
                      *args: str,
                      i18n: TranslatorRunner,
                      param_back: bool | None = False,
                      back_data: str | None = None,
                      **kwargs: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder = InlineKeyboardBuilder()

    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []
    # Заполняем список кнопками из аргументов args и kwargs
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=i18n.get(button),
                callback_data=button))

    # Заполняем список кнопками из аргументов args и kwargs
    if kwargs:
        for link, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=i18n.get(text),
                url=i18n.get(link)))

    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)

    if param_back:
        kb_builder.row(InlineKeyboardButton(
            text=i18n.get(back_data), callback_data=back_data), width=1)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


class SubCallbackFactory(CallbackData, prefix="sub", sep="_"):
    name_sub: str


def get_inline_sub_kb(width: int,
                      *args: str,
                      i18n: TranslatorRunner,
                      param_back: bool | None = False,
                      back_data: str | None = None,
                      **kwargs: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []
    # Заполняем список кнопками из аргументов args и kwargs
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=i18n.get(button),
                callback_data=SubCallbackFactory(name_sub=button).pack()))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=SubCallbackFactory(name_sub=button).pack()))
    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)

    if param_back:
        kb_builder.row(InlineKeyboardButton(
            text=i18n.get(back_data), callback_data=back_data), width=1)
    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()
