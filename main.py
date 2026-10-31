"""Точка входа: python main.py."""
import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import load_config
from database.tasks import TaskDatabase
from handlers.tasks import router
from keyboards.commands import COMMANDS


async def main() -> None:
    config = load_config()
    database = TaskDatabase(config.database_path)
    await asyncio.to_thread(database.initialize)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    # aiogram передаст database в аргументы обработчиков по имени.
    async with Bot(token=config.bot_token) as bot:
        await bot.set_my_commands(COMMANDS)
        await dispatcher.start_polling(bot, database=database)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (ValueError, RuntimeError) as error:
        raise SystemExit(str(error)) from None
