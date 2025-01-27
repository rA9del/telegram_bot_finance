from aiogram import F, Router
from aiogram.types import Message, CallbackQuery,  ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from datetime import datetime

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

@router.callback_query(F.data.in_(['Накопить', 'Отслеживать финансы']))
async def register_goal(callback: CallbackQuery, state: FSMContext):
    await state.update_data(goal=callback.data)
    data = await state.get_data()
    
    user_id = callback.from_user.id
    store_user_data(user_id, data) 
    
    await callback.message.answer(
        f"Вы {data['name']}, возраст {data['age']}, что хочет {data['goal']}?\nИщи себя в прошма... Рад знакомству)"
    )
    await callback.message.answer(main_page(), reply_markup=kb.main)
    await state.clear()
    await callback.answer()

def store_user_data(user_id, data):
    registered_users[user_id] = data
    
    
    
    
    
class Expense(StatesGroup):
    date = State()
    category = State()
    currency = State()
    amount = State()
    custom_input = State()


@router.callback_query(F.data == "loss")
async def start_expense_tracking(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Сегодня?", reply_markup=kb.date_keyboard) ##todo: make a db
    await state.set_state(Expense.date)
    await callback.answer()


@router.callback_query(F.data.startswith("date_"))
async def process_expense_date(callback: CallbackQuery, state: FSMContext):
    date_value = callback.data.split("_")[1]
    
    if date_value == "today":
        today = datetime.today().strftime("%Y-%m-%d")
        await state.update_data(date=today)
        await process_expense_category_step(callback.message, state)
    elif date_value == "add":
        await callback.message.edit_text("А когда тогда? (например, 2024-01-31):")
        await state.set_state(Expense.custom_input)
        await state.update_data(field="date")
    await callback.answer()
    
@router.message(Expense.custom_input)
async def process_custom_date(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data.get("field")

    if field == "date":
        try:
            input_date = datetime.strptime(message.text, "%Y-%m-%d").date()
            today = datetime.today().date()
            hundred_years_ago = today.replace(year=today.year - 100)

            if input_date < hundred_years_ago or input_date > today:
                raise ValueError("Инвалидный диапазон какой-то")

            await state.update_data(date=message.text)
            await process_expense_category_step(message, state)

        except ValueError:
            await message.answer("Ошибка: введите дату в формате ГГГГ-ММ-ДД (до 100 лет назад и не позже сегодня).")



async def process_expense_category_step(message: Message, state: FSMContext):
    await message.answer("Выберите категорию", reply_markup=kb.generate_inline_keyboard(kb.user_categories, "Добавить категорию", "category"))
    await state.set_state(Expense.category)


@router.callback_query(F.data.startswith("category_"))
async def process_expense_category(callback: CallbackQuery, state: FSMContext):
    category_value = callback.data.split("_")[1]

    if category_value == "add":
        await callback.message.edit_text("Давайте введем еще одну категорию трат)))")
        await state.set_state(Expense.custom_input)
        await state.update_data(field="category")
    else:
        await state.update_data(category=category_value)
        await callback.message.edit_text("В какой валюте?", reply_markup=kb.generate_inline_keyboard(kb.user_currencies, "Добавить валюту", "currency"))
        await state.set_state(Expense.currency)
    await callback.answer()
    


@router.callback_query(F.data.startswith("currency_"))
async def process_expense_currency(callback: CallbackQuery, state: FSMContext):
    currency_value = callback.data.split("_")[1]

    if currency_value == "add":
        await callback.message.edit_text("Название валюты пж")
        await state.set_state(Expense.custom_input)
        await state.update_data(field="currency")
    else:
        await state.update_data(currency=currency_value)
        await callback.message.edit_text("Какую сумму потратили?")
        await state.set_state(Expense.amount)
    await callback.answer()


# Handle amount input
@router.message(Expense.amount)
async def process_expense_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(amount=amount)
        data = await state.get_data()

        displayed_date = "Сегодня" if data['date'] == datetime.today().strftime("%Y-%m-%d") else "Другая дата"

        await message.answer(
            f"✅ Расход записан:\n"
            f"📅 Дата: {displayed_date}\n"
            f"📂 Категория: {data['category']}\n"
            f"💰 Валюта: {data['currency']}\n"
            f"💸 Сумма: {data['amount']}"
        )
        await message.answer(main_page(), reply_markup=kb.main)
        await state.clear()

    except ValueError:
        await message.answer("Введите корректную сумму (например, 150.75).")