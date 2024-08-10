import logging

from fluentogram import TranslatorRunner

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# from app.tg_bot.models.role import UserRole
from app.tg_bot.models.keyboard import InlineKeyboardModel

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

    if back_data != None:
        kb_builder.row(InlineKeyboardButton(
            text=i18n.get(back_data), callback_data=back_data), width=1)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


def get_inline_keyboard(
    *args: str,
    i18n: TranslatorRunner,
    keyboard: InlineKeyboardModel,
        **kwargs: str) -> InlineKeyboardMarkup:

    kb_builder = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = []

    if keyboard.buttons != None:
        for button in i18n.get(keyboard.buttons).split('\n'):
            buttons.append(InlineKeyboardButton(
                text=i18n.get(button),
                callback_data=button))

    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))

    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=keyboard.width)

    if keyboard.prepenultimate != None:
        kb_builder.row(InlineKeyboardButton(
            text=i18n.get(keyboard.prepenultimate), callback_data=keyboard.prepenultimate), width=1)

    if keyboard.penultimate != None:
        kb_builder.row(InlineKeyboardButton(
            text=i18n.get(keyboard.penultimate), callback_data=keyboard.penultimate), width=1)

    if keyboard.ultimate != None:
        kb_builder.row(InlineKeyboardButton(
            text=i18n.get(keyboard.ultimate), callback_data=keyboard.ultimate), width=1)

    if keyboard.reference != None:
        kb_builder.row(InlineKeyboardButton(
            text=i18n.get(keyboard.reference), callback_data=keyboard.reference), width=1)

    return kb_builder.as_markup()


def get_keypad(
        i18n: TranslatorRunner,
        penult_button: str | None = 'ready',
        param_back: bool | None = False,
        back_data: str | None = None) -> InlineKeyboardMarkup:

    kb_builder = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = [[], [], [], [], []]

    keypad = [['all_clean', 'clean', 'open_parenthesis', 'closing_parenthesis', 'square_root'],
              ['one', 'two', 'three', 'pow', 'pow_square'],
              ['four', 'five', 'six', 'divide', 'multiply'],
              ['seven', 'eight', 'nine', 'minus', 'plus'],
              ['zero', 'point', 'dooble_zero', 'equals']
              ]
    keypad_dict = {'square_root': '[ √x ]',
                   'clean': 'DEL', 'all_clean': 'AC', 'open_parenthesis': ' ❪ ', 'closing_parenthesis': ' ❫ ',
                   'one': '𝟭', 'two': '𝟮', 'three': '𝟯', 'pow': '[ x^ ]', 'pow_square': '[ x² ]',
                   'four': '𝟰', 'five': '𝟱', 'six': '𝟲', 'divide': '[ ÷ ]', 'multiply': '[ × ]',
                   'seven': '𝟳', 'eight': '𝟴', 'nine': '𝟵', 'minus': '[ - ]', 'plus': '[ + ]',
                   'zero': '𝟬', 'point': '[ . ]', 'dooble_zero': '𝟬𝟬', 'equals': '[enter =]'}

    for row in range(0, len(buttons)):
        for button in keypad[row]:
            buttons[row].append(InlineKeyboardButton(
                text=keypad_dict.get(button), callback_data=button)
            )
        width = 5 if row == 0 else (4 if row == 4 else 5)
        kb_builder.row(*buttons[row], width=width)

    if penult_button != None:
        kb_builder.row(InlineKeyboardButton(
            text=i18n.get(penult_button), callback_data=penult_button), width=1)

    if param_back:
        kb_builder.row(InlineKeyboardButton(
            text=i18n.get(back_data), callback_data=back_data), width=1)

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
