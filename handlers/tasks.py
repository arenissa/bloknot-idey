"""Обработчики четырёх команд бота."""
import asyncio

from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import BufferedInputFile, Message

from database.tasks import TaskDatabase
from services.export import tasks_to_csv
from services.messages import task_messages

router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Привет! Я — командный блокнот задач.\n\n"
        "/add текст задачи — добавить задачу\n"
        "/list — показать все задачи\n"
        "/list_csv — скачать CSV\n\n"
        "Список общий для всех пользователей этого бота.\n"
        "Пример: /add Подготовить презентацию к пятнице"
    )


@router.message(Command("add"))
async def add_task(message: Message, command: CommandObject, database: TaskDatabase) -> None:
    text = (command.args or "").strip()
    if not text:
        await message.answer("Напишите задачу после команды:\n/add Подготовить презентацию")
        return
    user = message.from_user
    author = (
        f"@{user.username} (id: {user.id})" if user and user.username
        else f"{user.full_name} (id: {user.id})" if user
        else f"Чат {message.chat.id}"
    )
    # SQLite работает синхронно; to_thread не блокирует обработку других команд.
    task_id = await asyncio.to_thread(database.add, text, author)
    await message.answer(f"Задача №{task_id} добавлена.")


@router.message(Command("list"))
async def list_tasks(message: Message, database: TaskDatabase) -> None:
    tasks = await asyncio.to_thread(database.list_all)
    if not tasks:
        await message.answer("Список пока пуст. Добавьте задачу: /add текст задачи")
        return
    for part in task_messages(tasks):
        await message.answer(part)


@router.message(Command("list_csv"))
async def export_tasks(message: Message, database: TaskDatabase) -> None:
    tasks = await asyncio.to_thread(database.list_all)
    document = BufferedInputFile(tasks_to_csv(tasks), filename="tasks.csv")
    await message.answer_document(document, caption=f"Общий список задач: {len(tasks)}. Время UTC.")
