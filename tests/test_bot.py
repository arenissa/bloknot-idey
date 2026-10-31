import csv
import io
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock

from aiogram.filters import CommandObject
from aiogram.types import Chat, Message, User

from database.tasks import TaskDatabase
from handlers.tasks import add_task, export_tasks, list_tasks, start
from services.export import tasks_to_csv
from services.messages import task_messages


class BotTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.database = TaskDatabase(Path(self.directory.name) / "tasks.sqlite3")
        self.database.initialize()
        self.message = Message(
            message_id=1, date=datetime.now(timezone.utc),
            chat=Chat(id=1, type="private"),
            from_user=User(id=7, is_bot=False, first_name="Анна"),
        )

    async def test_add_and_persistence(self):
        with unittest.mock.patch.object(Message, "answer", new_callable=AsyncMock) as answer:
            await add_task(self.message, CommandObject(command="add", args="Текст ' ; DROP TABLE tasks;"), self.database)
            answer.assert_awaited_once()
        reopened = TaskDatabase(self.database.path)
        reopened.initialize()
        row = reopened.list_all()[0]
        self.assertEqual(row["text"], "Текст ' ; DROP TABLE tasks;")
        self.assertIn("Анна", row["user"])
        self.assertTrue(row["created_at"])

    async def test_empty_add_is_not_saved(self):
        with unittest.mock.patch.object(Message, "answer", new_callable=AsyncMock):
            await add_task(self.message, CommandObject(command="add", args="  "), self.database)
        self.assertEqual(self.database.list_all(), [])

    async def test_start_and_empty_list(self):
        with unittest.mock.patch.object(Message, "answer", new_callable=AsyncMock) as answer:
            await start(self.message)
            await list_tasks(self.message, self.database)
            self.assertEqual(answer.await_count, 2)
            self.assertIn("пуст", answer.call_args.args[0])

    async def test_csv_export(self):
        self.database.add('Задача; с "кавычками"\nи переносом', "Анна")
        with unittest.mock.patch.object(Message, "answer_document", new_callable=AsyncMock) as answer:
            await export_tasks(self.message, self.database)
            document = answer.call_args.args[0]
            rows = list(csv.reader(io.StringIO(document.data.decode("utf-8-sig")), delimiter=";"))
            self.assertEqual(document.filename, "tasks.csv")
            self.assertEqual(rows[1][1], 'Задача; с "кавычками"\nи переносом')

    def test_empty_csv_and_formula(self):
        self.assertEqual(tasks_to_csv([]).decode("utf-8-sig").strip(), "id;text;user;created_at")
        self.database.add("=1+1", "@user")
        rows = list(csv.reader(io.StringIO(tasks_to_csv(self.database.list_all()).decode("utf-8-sig")), delimiter=";"))
        self.assertEqual(rows[1][1], "'=1+1")
        self.assertEqual(rows[1][2], "'@user")

    async def test_long_list(self):
        self.database.add("🌟" * 4000, "Анна")
        messages = task_messages(self.database.list_all())
        self.assertTrue(all(len(part.encode("utf-16-le")) // 2 <= 4096 for part in messages))
        with unittest.mock.patch.object(Message, "answer", new_callable=AsyncMock) as answer:
            await list_tasks(self.message, self.database)
            self.assertEqual(answer.await_count, len(messages))
