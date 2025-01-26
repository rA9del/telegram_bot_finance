from aiogram import F, Router
from aiogram.types import Message, CallbackQuery,  ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.keyboards as kb

router = Router()

class Register(StatesGroup):
    name = State()
    age = State()
    goal = State()
    
registered_users = {} ###todo: connect a DB


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in registered_users:
        await message.answer("Добро пожаловать!")
        await start_registration(message, state)
    else:
        user_data = registered_users.get(user_id, {})
        user_name = user_data.get("name", "гость")
        await message.answer(f"С возвращением, {user_name}!")
        await message.answer(main_page(), reply_markup=kb.main)
        
def main_page():
    return("Что сделаем?")

async def start_registration(message: Message, state: FSMContext):
    await message.answer("Как звать?")
    await state.set_state(Register.name)

@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Вы нажали на кнопку помощи') ###todo: how to use your bot

@router.message(F.text == 'Каталог')
async def catalog(message: Message):
    await message.answer('Выберите категорию товара', reply_markup=kb.catalog)

@router.callback_query(F.data == 't-shirt')
async def t_shirt(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию', show_alert=True)
    await callback.message.answer('Вы выбрали категорию футболок.')

@router.message(Register.name)
async def register_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Register.age)
    await message.answer('Сколько лет?', reply_markup=ReplyKeyboardRemove())

@router.message(Register.age)
async def register_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(Register.goal)
    await message.answer('Что привело сюда?', reply_markup=kb.get_goal)

@router.message(Register.goal)
async def register_number(message: Message, state: FSMContext):
    await state.update_data(goal=message.text)
    data = await state.get_data()
    
    user_id = message.from_user.id
    store_user_data(user_id, data)  # Store the user data temporary in the dictionary
    await message.answer(f"Вы {data['name']}, что хочет {data['goal']}?\nИщи себя в прошма... Рад знакомству)")
    await message.answer(main_page(), reply_markup=kb.main)
    await state.clear()

def store_user_data(user_id, data):
    registered_users[user_id] = data
