"""SQLite persistence layer for TaskFlow."""

from __future__ import annotations

import os
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "taskflow.db"
STATUSES = ("Pending", "In Progress", "Completed")
PRIORITIES = ("Low", "Medium", "High")


def _connect(db_path: str | Path | None = None) -> sqlite3.Connection:
    path = Path(db_path or os.environ.get("TASKFLOW_DB_PATH", DEFAULT_DB_PATH))
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(db_path: str | Path | None = None) -> None:
    """Create the task table if it does not exist."""
    with _connect(db_path) as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                priority TEXT NOT NULL CHECK(priority IN ('Low', 'Medium', 'High')),
                due_date TEXT,
                status TEXT NOT NULL CHECK(status IN ('Pending', 'In Progress', 'Completed')),
                created_at TEXT NOT NULL
            )"""
        )


def _validate_task(title: str, priority: str, status: str) -> None:
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Task title is required.")
    if priority not in PRIORITIES:
        raise ValueError("Priority must be Low, Medium, or High.")
    if status not in STATUSES:
        raise ValueError("Status must be Pending, In Progress, or Completed.")


def create_task(title: str, description: str = "", priority: str = "Medium",
                due_date: date | str | None = None, status: str = "Pending",
                db_path: str | Path | None = None) -> int:
    _validate_task(title, priority, status)
    due = due_date.isoformat() if isinstance(due_date, date) else due_date
    with _connect(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title, description, priority, due_date, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (title.strip(), (description or "").strip(), priority, due, status, datetime.now().isoformat(timespec="seconds")),
        )
        return int(cursor.lastrowid)


def get_tasks(db_path: str | Path | None = None) -> list[dict[str, Any]]:
    with _connect(db_path) as connection:
        rows = connection.execute("SELECT * FROM tasks ORDER BY created_at DESC, id DESC").fetchall()
        return [dict(row) for row in rows]


def get_task(task_id: int, db_path: str | Path | None = None) -> dict[str, Any] | None:
    with _connect(db_path) as connection:
        row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return dict(row) if row else None


def update_task(task_id: int, title: str, description: str, priority: str,
                due_date: date | str | None, status: str,
                db_path: str | Path | None = None) -> bool:
    _validate_task(title, priority, status)
    due = due_date.isoformat() if isinstance(due_date, date) else due_date
    with _connect(db_path) as connection:
        cursor = connection.execute(
            "UPDATE tasks SET title = ?, description = ?, priority = ?, due_date = ?, status = ? WHERE id = ?",
            (title.strip(), (description or "").strip(), priority, due, status, task_id),
        )
        return cursor.rowcount > 0


def update_task_status(task_id: int, status: str, db_path: str | Path | None = None) -> bool:
    if status not in STATUSES:
        raise ValueError("Status must be Pending, In Progress, or Completed.")
    with _connect(db_path) as connection:
        cursor = connection.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        return cursor.rowcount > 0


def delete_task(task_id: int, db_path: str | Path | None = None) -> bool:
    with _connect(db_path) as connection:
        cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0
