from aiogram import Router, html
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


rt= Router()

class Form():
    task = State()

@rt.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.task)
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}! "
                         f"\nНапиши название дела, с регулярным выполнением которого у тебя возникают трудности.")

@rt.message(Form.task)
async def task_saving(message: Message, state:FSMContext):
    pass