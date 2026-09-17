import logging

import aiosqlite
from aiogram import Router, html, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder

rt= Router()

# ---

DB_NAME = "tasks.db"
async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                last_notification TEXT NOT NULL
            )
        """)
        await db.commit()

async def add_user_task(user_id, task, last_notification=None, is_active=1):
    if last_notification is None:
        last_notification = datetime.now().isoformat()
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""INSERT INTO users (user_id, task, last_notification, is_active) VALUES (?, ?, ?, ?)
        """, (user_id, task, last_notification, is_active))
        await db.commit()


async def user_tasks(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""SELECT task FROM users WHERE user_id = ?
        """, (user_id,))
        tasks_list = await cursor.fetchall()
        tasks_arr = [task[0] for task in tasks_list]
        return tasks_arr

async def delete_task(user_id, task):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""DELETE FROM users WHERE user_id = ? AND task = ?
                """, (user_id, task))
        await db.commit()
# ---

class Form(StatesGroup):
    task = State()
    clearing = State()
    set_time = State()

@rt.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await init_db()
    await state.set_state(Form.task)
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}! "
                         f"\nНапиши название дела, с регулярным выполнением которого у тебя возникают трудности.")

@rt.message(Form.task)
async def task_saving(message: Message, state:FSMContext):
    task_text = message.text
    user_id = message.from_user.id

    await add_user_task(user_id=user_id, task=task_text)
    await state.clear() #state.set_state(Form.set_time)

    tasks = await user_tasks(user_id=user_id)
    answr_txt = "".join([f"\n• {task}" for task in tasks])
    await message.answer(f"Отлично! Твоё дело записано. Теперь твой список дел выглядит так:\n{answr_txt}")

@rt.message(Form.set_time)
async def set_time_div(message: Message, state: FSMContext): # выбор дела списком или только для того, которое устанавливаем? а лучше две отдельные функции, чтобы можно было позже редактировать div
    pass

@rt.message(Command("delete"))
async def task_saving(message: Message, state: FSMContext):
    await state.set_state(Form.clearing)
    tasks = await user_tasks(message.from_user.id)
    builder = InlineKeyboardBuilder()
    for task in tasks:
        builder.button(text=task, callback_data=str(task))
    builder.adjust(3, 2)
    keyboard = InlineKeyboardMarkup(inline_keyboard=builder.export())
    await message.answer("Some text here", reply_markup=keyboard)

@rt.callback_query(F.data=="yes")
async def remove_task(callback: CallbackQuery, state: FSMContext): # и тут
    await callback.answer('')
    await callback.message.edit_text("Происходит удаление...")
    task = await state.get_data()
    task = task['clearing']
    await delete_task(user_id=callback.from_user.id, task=task)
    await callback.message.edit_text(f"{task} было удалено!")

@rt.callback_query()
async def start_remove_task(callback: CallbackQuery, state: FSMContext): # починить одинаковые task тут
    await callback.answer('')
    task = callback.data
    await state.update_data(clearing=task)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="yes")],
        [InlineKeyboardButton(text="Нет", callback_data="no")],
    ]
    )
    await callback.message.edit_text(f"Вы хотите удалить {task}?", reply_markup=keyboard)