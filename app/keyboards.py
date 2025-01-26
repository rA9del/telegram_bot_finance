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


get_goal = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Накопить')],
                                         [KeyboardButton(text='Отслеживать финансы')]],
                               resize_keyboard=True)