from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import Column, Integer, String, Float, Date, Enum

from app.db import Base

# --- States ---
class Register(StatesGroup):
    name = State()
    age = State()
    goal = State()


class Expense(StatesGroup):
    date = State()
    category = State()
    currency = State()
    amount = State()
    custom_input = State()


class Profit(StatesGroup):
    date = State()
    category = State()
    currency = State()
    amount = State()
    custom_input = State()


class Report(StatesGroup):
    range = State()
    start_date = State()
    end_date = State()


class Register(StatesGroup):
    name = State()
    age = State()
    goal = State()
    
    
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, index=True, nullable=False)
    date = Column(Date, nullable=False)
    category = Column(String(255), nullable=False)
    currency = Column(String(10), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(Enum("loss", "profit", name="transaction_type"), nullable=False) 
    
    
    