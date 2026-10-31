"""Делим длинный список, чтобы уложиться в ограничение Telegram."""
from collections.abc import Iterable


def task_messages(tasks: Iterable) -> list[str]:
    content = "Общий список задач (время UTC):\n\n" + "\n\n".join(
        f"{task['id']}. {task['text']}\nАвтор: {task['user']}\nСоздано: {task['created_at']}"
        for task in tasks
    )
    # 2000 символов безопасны даже для символов вне BMP (например, эмодзи).
    return [content[index:index + 2000] for index in range(0, len(content), 2000)]
