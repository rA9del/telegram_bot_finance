from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
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
        await message.answer('Привет! Пасиба за доверие, рад знакомству')
        await message.answer("Как звать?")
        await state.set_state(Register.name)
    else:
        await message.answer('Привет! С возвращением', reply_markup=kb.main)


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Вы нажали на кнопку помощи')

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
    await message.answer('Введите ваш возраст')

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
    await state.clear()

def store_user_data(user_id, data):
    registered_users[user_id] = data
