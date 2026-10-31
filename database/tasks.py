"""SQLite: отдельное соединение на каждую операцию, без общих курсоров."""
import sqlite3
from pathlib import Path


class TaskDatabase:
    def __init__(self, path: Path) -> None:
        self.path = path

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    user TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def add(self, text: str, user: str) -> int:
        text = text.strip()
        if not text:
            raise ValueError("Текст задачи не может быть пустым.")
        with sqlite3.connect(self.path) as connection:
            # Параметры ?, а не склейка строк, защищают SQL-запрос.
            cursor = connection.execute(
                "INSERT INTO tasks (text, user) VALUES (?, ?)", (text, user)
            )
            return int(cursor.lastrowid)

    def list_all(self) -> list[sqlite3.Row]:
        with sqlite3.connect(self.path) as connection:
            connection.row_factory = sqlite3.Row
            return connection.execute(
                "SELECT id, text, user, created_at FROM tasks ORDER BY id"
            ).fetchall()
