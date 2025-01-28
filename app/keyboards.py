from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

# main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Каталог')],
#                                      [KeyboardButton(text='Корзина')],
#                                      [KeyboardButton(text='Контакты'),
#                                       KeyboardButton(text='О нас')]],
#                            resize_keyboard=True,
#                            input_field_placeholder='Выберите пункт меню...')

main = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Вношу траты', callback_data='loss')],
                                                     [InlineKeyboardButton(text='Вношу доход', callback_data='profit')],
                                                     [InlineKeyboardButton(text='Хочу отчет', callback_data='report')]])

catalog = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Футболки', callback_data='t-shirt')],
    [InlineKeyboardButton(text='Кроссовки', callback_data='sneakers')],
    [InlineKeyboardButton(text='Кепки', callback_data='cap')]])


get_goal = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Накопить", callback_data="Накопить")],
        [InlineKeyboardButton(text="Отслеживать финансы", callback_data="Отслеживать финансы")],
    ]
)


date_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Сегодня", callback_data="today")],
        [InlineKeyboardButton(text="Другая дата", callback_data="other_date")]
    ]
)

expense_categories = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Продукты", callback_data="Продукты")],
        [InlineKeyboardButton(text="Транспорт", callback_data="Транспорт")],
        [InlineKeyboardButton(text="Развлечения", callback_data="Развлечения")]
    ]
)

currency_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="USD ($)", callback_data="USD")],
        [InlineKeyboardButton(text="EUR (€)", callback_data="EUR")],
        [InlineKeyboardButton(text="KZT", callback_data="KZT")]
    ]
)



user_dates = ["Сегодня"]
user_categories = ["Продукты", "Транспорт", "Развлечения"]
user_currencies = ['KZT', "USD", "EUR"]

user_profit_source = ["Работа"]

date_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Сегодня", callback_data="date_today")],
        [InlineKeyboardButton(text="Другая дата", callback_data="date_add")]
    ]
)

date_keyboard_expense = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Сегодня", callback_data="profit_date_today")],
        [InlineKeyboardButton(text="Другая дата", callback_data="profit_date_add")]
    ]
)

def generate_inline_keyboard(items_list, add_button_text, callback_prefix):
    buttons = [[InlineKeyboardButton(text=item, callback_data=f"{callback_prefix}_{item}")] for item in items_list]
    buttons.append([InlineKeyboardButton(text=add_button_text, callback_data=f"{callback_prefix}_add")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)



