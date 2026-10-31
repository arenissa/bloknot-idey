"""Создание CSV в памяти: временный файл на диске не нужен."""
import csv
import io
from collections.abc import Iterable, Mapping
from typing import Any


def safe_cell(value: Any) -> str:
    text = str(value)
    # Excel не должен выполнять пользовательский текст как формулу.
    if text.lstrip().startswith(("=", "+", "-", "@")) or text.startswith(("\t", "\r", "\n")):
        return "'" + text
    return text


def tasks_to_csv(tasks: Iterable[Mapping]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["id", "text", "user", "created_at"])
    for task in tasks:
        writer.writerow([safe_cell(task[key]) for key in ("id", "text", "user", "created_at")])
    # BOM помогает Excel правильно распознать кириллицу.
    return output.getvalue().encode("utf-8-sig")
