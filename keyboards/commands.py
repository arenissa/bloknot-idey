"""Команды появляются в стандартном меню Telegram рядом с полем ввода."""
from aiogram.types import BotCommand

COMMANDS = [
    BotCommand(command="start", description="Приветствие и помощь"),
    BotCommand(command="add", description="Добавить: /add текст задачи"),
    BotCommand(command="list", description="Общий список задач"),
    BotCommand(command="list_csv", description="Скачать задачи в CSV"),
]
