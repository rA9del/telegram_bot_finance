from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import  get_db
from func.states import *
import app.keyboards as kb



router = Router()
    
registered_users = {} ###todo: connect a DB


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db: AsyncSession = None):
    """Handle the /start command."""
    async with get_db() as db:
        user = await db.execute(select(User).where(User.user_id == message.from_user.id))
        user = user.scalars().first()

        if not user:
            await message.answer("Добро пожаловать!")
            await start_registration(message, state)
        else:
            await message.answer(f"С возвращением, {user.name}!")
            await message.answer(main_page(), reply_markup=kb.main)

def main_page():
    return("Что сделаем?")

async def start_registration(message: Message, state: FSMContext):
    await message.answer("Как звать?")
    await state.set_state(Register.name)

@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Вы нажали на кнопку помощи') ###todo: how to use your bot

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
async def register_goal(callback: CallbackQuery, state: FSMContext, db: AsyncSession = None):
    """Save the user's goal and complete registration."""
    async with get_db() as db:
        await state.update_data(goal=callback.data)
        data = await state.get_data()

        new_user = User(
            user_id=callback.from_user.id,
            name=data['name'],
            age=int(data['age']),
            goal=data['goal']
        )
        db.add(new_user)
        await db.commit()

        await callback.message.answer(
            f"Вы {data['name']}, возраст {data['age']}, что хочет {data['goal']}? Рад знакомству!"
        )
        await callback.message.answer(main_page(), reply_markup=kb.main)
        await state.clear()

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
        
        
        
        
        
        
        
        
class Profit(StatesGroup):
    date = State()
    category = State()
    currency = State()
    amount = State()
    custom_input = State()

@router.callback_query(F.data == "profit")
async def start_profit_tracking(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Сегодня?", reply_markup=kb.date_keyboard_expense)
    await state.set_state(Profit.date)
    await callback.answer()


@router.callback_query(F.data.startswith("profit_date_"))
async def process_profit_date(callback: CallbackQuery, state: FSMContext):
    date_value = callback.data.split("_")[2]

    if date_value == "today":
        today = datetime.today().strftime("%Y-%m-%d")
        await state.update_data(date=today)
        await process_profit_category_step(callback.message, state)
    elif date_value == "add":
        await callback.message.edit_text("А когда тогда? (например, 2024-01-31):")
        await state.set_state(Profit.custom_input)
        await state.update_data(field="date")
    await callback.answer()


async def process_profit_category_step(message: Message, state: FSMContext):
    await message.answer(
        "Выберите категорию дохода",
        reply_markup=kb.generate_inline_keyboard(kb.user_profit_source, "Добавить категорию", "profit_category")
    )
    await state.set_state(Profit.category)


@router.callback_query(F.data.startswith("profit_category_"))
async def process_profit_category(callback: CallbackQuery, state: FSMContext):
    category_value = callback.data.split("_")[2]

    if category_value == "add":
        await callback.message.edit_text("Введите новую категорию дохода:")
        await state.set_state(Profit.custom_input)
        await state.update_data(field="category")
    else:
        await state.update_data(category=category_value)
        await callback.message.edit_text(
            "В какой валюте?",
            reply_markup=kb.generate_inline_keyboard(kb.user_currencies, "Добавить валюту", "profit_currency")
        )
        await state.set_state(Profit.currency)
    await callback.answer()


@router.callback_query(F.data.startswith("profit_currency_"))
async def process_profit_currency(callback: CallbackQuery, state: FSMContext):
    currency_value = callback.data.split("_")[2]

    if currency_value == "add":
        await callback.message.edit_text("Название валюты пж")
        await state.set_state(Profit.custom_input)
        await state.update_data(field="currency")
    else:
        await state.update_data(currency=currency_value)
        await callback.message.edit_text("Какую получил этот сигма?")
        await state.set_state(Profit.amount)
    await callback.answer()


@router.message(Profit.amount)
async def process_profit_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(amount=amount)
        data = await state.get_data()

        displayed_date = "Сегодня" if data['date'] == datetime.today().strftime("%Y-%m-%d") else data['date']

        await message.answer(
            f"✅ Доход записан:\n"
            f"📅 Дата: {displayed_date}\n"
            f"📂 Категория: {data['category']}\n"
            f"💰 Валюта: {data['currency']}\n"
            f"💵 Сумма: {data['amount']}"
        )
        await message.answer(main_page(), reply_markup=kb.main)
        await state.clear()

    except ValueError:
        await message.answer("Введите корректную сумму (например, 150.75).")








class Report(StatesGroup):
    range = State()
    start_date = State()
    end_date = State()

@router.callback_query(F.data == "report")
async def start_report(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Выберите временной диапазон:", reply_markup=kb.report_keyboard)
    await state.set_state(Report.range)
    await callback.answer()

@router.callback_query(F.data.startswith("report_"))
async def generate_report(callback: CallbackQuery, state: FSMContext):
    report_type = callback.data.split("_")[1]
    today = datetime.today()
    
    if report_type == "week":
        start_date = today - timedelta(days=7)
    elif report_type == "month":
        start_date = today - timedelta(days=30)
    elif report_type == "year":
        start_date = today - timedelta(days=365)
    elif report_type == "custom":
        await callback.message.edit_text("Введите начальную дату (например, 2024-01-01):")
        await state.set_state(Report.start_date)
        await callback.answer()
        return
    
    end_date = today
    await display_report(callback.message, start_date, end_date)
    await state.clear()
    await callback.answer()

@router.message(Report.start_date)
async def get_start_date(message: Message, state: FSMContext):
    try:
        start_date = datetime.strptime(message.text, "%Y-%m-%d").date()
        await state.update_data(start_date=start_date)
        await message.answer("Введите конечную дату (например, 2024-12-31):")
        await state.set_state(Report.end_date)
    except ValueError:
        await message.answer("Неверный формат даты. Попробуйте еще раз (ГГГГ-ММ-ДД).")


@router.message(Report.end_date)
async def get_end_date(message: Message, state: FSMContext):
    try:
        end_date = datetime.strptime(message.text, "%Y-%m-%d").date()
        data = await state.get_data()
        start_date = data.get("start_date")

        if not start_date or end_date < start_date:
            raise ValueError("Конечная дата должна быть позже начальной.")
        await display_report(message, start_date, end_date)
        await state.clear()
    except ValueError:
        await message.answer("Неверный формат даты или конечная дата раньше начальной. Попробуйте снова.")




async def display_report(message: Message, start_date: datetime.date, end_date: datetime.date):
    # Sample data for demonstration
    sample_data = {
        "losses": [{"date": "2024-01-25", "amount": 100, "currency": "USD", "category": "Транспорт"}],
        "profits": [{"date": "2024-01-27", "amount": 200, "currency": "USD", "category": "Работа"}]
    }
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    total_losses = sum(
        item["amount"] for item in sample_data["losses"]
        if start_datetime <= datetime.strptime(item["date"], "%Y-%m-%d") <= end_datetime
    )
    total_profits = sum(
        item["amount"] for item in sample_data["profits"]
        if start_datetime <= datetime.strptime(item["date"], "%Y-%m-%d") <= end_datetime
    )

    # Send the report to the user
    await message.answer(
        f"📅 Отчет с {start_date} по {end_date}:\n"
        f"💸 Траты: {total_losses} USD\n"
        f"💵 Доходы: {total_profits} USD\n"
        f"📊 Баланс: {total_profits - total_losses} USD"
    )




@router.message(Expense.amount)
async def process_expense_amount(message: Message, state: FSMContext, db: AsyncSession = Depends(get_db)):
    try:
        amount = float(message.text)
        await state.update_data(amount=amount)
        data = await state.get_data()

        # Save to database
        transaction = Transaction(
            user_id=message.from_user.id,
            date=datetime.strptime(data["date"], "%Y-%m-%d").date(),
            category=data["category"],
            currency=data["currency"],
            amount=amount,
            type="loss"
        )
        db.add(transaction)
        await db.commit()

        # Send confirmation
        displayed_date = "Сегодня" if data["date"] == datetime.today().strftime("%Y-%m-%d") else data["date"]
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


@router.message(Profit.amount)
async def process_profit_amount(message: Message, state: FSMContext, db: AsyncSession = Depends(get_db)):
    try:
        amount = float(message.text)
        await state.update_data(amount=amount)
        data = await state.get_data()

        # Save to database
        transaction = Transaction(
            user_id=message.from_user.id,
            date=datetime.strptime(data["date"], "%Y-%m-%d").date(),
            category=data["category"],
            currency=data["currency"],
            amount=amount,
            type="profit"
        )
        db.add(transaction)
        await db.commit()

        # Send confirmation
        displayed_date = "Сегодня" if data["date"] == datetime.today().strftime("%Y-%m-%d") else data["date"]
        await message.answer(
            f"✅ Доход записан:\n"
            f"📅 Дата: {displayed_date}\n"
            f"📂 Категория: {data['category']}\n"
            f"💰 Валюта: {data['currency']}\n"
            f"💵 Сумма: {data['amount']}"
        )
        await message.answer(main_page(), reply_markup=kb.main)
        await state.clear()

    except ValueError:
        await message.answer("Введите корректную сумму (например, 150.75).")



@router.message
async def display_report(message: Message, start_date: datetime.date, end_date: datetime.date, db: AsyncSession = Depends(get_db)):
    # Query losses
    losses = await db.execute(
        select(Transaction).where(
            Transaction.user_id == message.from_user.id,
            Transaction.type == "loss",
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
    )
    losses = losses.scalars().all()

    # Query profits
    profits = await db.execute(
        select(Transaction).where(
            Transaction.user_id == message.from_user.id,
            Transaction.type == "profit",
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
    )
    profits = profits.scalars().all()

    # Calculate totals
    total_losses = sum(item.amount for item in losses)
    total_profits = sum(item.amount for item in profits)

    # Send the report
    await message.answer(
        f"📅 Отчет с {start_date} по {end_date}:\n"
        f"💸 Траты: {total_losses} USD\n"
        f"💵 Доходы: {total_profits} USD\n"
        f"📊 Баланс: {total_profits - total_losses} USD"
    )
