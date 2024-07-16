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
                     penult_button: str | None = None,
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
    # log.info(args)
    if args:
        if check_role:
            if role == 'guest':
                for button in args:
                    buttons.append(InlineKeyboardButton(
                        text=i18n.get(button + '_guest'),
                        callback_data=button + '_guest'))
            elif role == 'subscriber':
                for button in args:
                    buttons.append(InlineKeyboardButton(
                        text=i18n.get(button + '_subscriber'),
                        callback_data=button + '_subscriber'))
            elif role == 'comrade':
                for button in args:
                    buttons.append(InlineKeyboardButton(
                        text=i18n.get(button + '_comrade'),
                        callback_data=button + '_comrade'))
            elif role == 'admin':
                for button in args:
                    buttons.append(InlineKeyboardButton(
                        text=i18n.get(button + '_admin'),
                        callback_data=button + '_admin'))
            elif role == 'owner':
                for button in args:
                    buttons.append(InlineKeyboardButton(
                        text=i18n.get(button + '_owner'),
                        callback_data=button + '_owner'))
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

    if penult_button != None:
        kb_builder.row(InlineKeyboardButton(
            text=i18n.get(penult_button), callback_data=penult_button), width=1)

    if param_back:
        kb_builder.row(InlineKeyboardButton(
            text=i18n.get(back_data), callback_data=back_data), width=1)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


def get_keypad(
    # width: int = 1,
        *args: str,
        i18n: TranslatorRunner,
        penult_button: str | None = 'ready',
        param_back: bool | None = False,
        back_data: str | None = None,
        **kwargs: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    # buttons: list[InlineKeyboardButton] = []
    buttons_row0: list[InlineKeyboardButton] = []
    buttons_row1: list[InlineKeyboardButton] = []
    buttons_row2: list[InlineKeyboardButton] = []
    buttons_row3: list[InlineKeyboardButton] = []
    buttons_row4: list[InlineKeyboardButton] = []
    # Заполняем список кнопками из аргументов args и kwargs
    keypad = [['all_clean', 'clean', 'open_parenthesis', 'closing_parenthesis'],
              ['one', 'two', 'three', 'pow', 'pow_square'],
              ['four', 'five', 'six', 'divide', 'multiply'],
              ['seven', 'eight', 'nine', 'minus', 'plus'],
              ['zero', 'point', 'dooble_zero', 'equals']
              ]
    # for row in range(0, 5):
    # for button in keypad[row]:
    #     if row == 0:
    #         buttons_row0.append(InlineKeyboardButton(
    #             text=i18n.get(button), callback_data=button))
    #         kb_builder.row(*buttons_row0, width=4)
    #     elif row == 4:
    #         buttons_row4.append(InlineKeyboardButton(
    #             text=i18n.get(button), callback_data=button))
    #         kb_builder.row(*buttons_row4, width=4)

    #         else:
    #             kb_builder.row(InlineKeyboardButton(
    #                 text=i18n.get(button), callback_data=button), width=5)

    for button in keypad[0]:
        buttons_row0.append(InlineKeyboardButton(
            text=i18n.get(button), callback_data=button))
    kb_builder.row(*buttons_row0, width=4)

    for button in keypad[1]:
        buttons_row1.append(InlineKeyboardButton(
            text=i18n.get(button), callback_data=button))
    kb_builder.row(*buttons_row1, width=5)

    for button in keypad[2]:
        buttons_row2.append(InlineKeyboardButton(
            text=i18n.get(button), callback_data=button))
    kb_builder.row(*buttons_row2, width=5)

    for button in keypad[3]:
        buttons_row3.append(InlineKeyboardButton(
            text=i18n.get(button), callback_data=button))
    kb_builder.row(*buttons_row3, width=5)

    for button in keypad[4]:
        buttons_row4.append(InlineKeyboardButton(
            text=i18n.get(button), callback_data=button))
    kb_builder.row(*buttons_row4, width=4)

    # if args:
    #     for button in args:
    #         buttons.append(InlineKeyboardButton(
    #             text=i18n.get(button),
    #             callback_data=button))
    # if kwargs:
    #     for button, text in kwargs.items():
    #         buttons.append(InlineKeyboardButton(
    #             text=text,
    #             callback_data=button))
    # Распаковываем список с кнопками в билдер методом row c параметром width
    # kb_builder.row(*buttons, width=width)

    if penult_button != None:
        kb_builder.row(InlineKeyboardButton(
            text=i18n.get(penult_button), callback_data=penult_button), width=1)

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
