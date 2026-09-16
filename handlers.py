import aiosqlite
from aiogram import Router, html
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

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
        await db.execute("""DELETE FROM users WHERE user_is = ? AND task = ?
                """, (user_id, task))
        await db.commit()
# ---

class Form(StatesGroup):
    task = State()

@rt.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.task)
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}! "
                         f"\nНапиши название дела, с регулярным выполнением которого у тебя возникают трудности.")

@rt.message(Form.task)
async def task_saving(message: Message, state:FSMContext):
    task_text = message.text
    user_id = message.from_user.id

    await add_user_task(user_id=user_id, task=task_text)
    await state.clear()

    tasks = await user_tasks(user_id=user_id)
    answr_txt = "".join([f"• {task}" for task in tasks])
    await message.answer(f"Отлично! Твоё дело записано. Теперь твой список дел выглядит так:\n{answr_txt}")

