"""Small, UI-independent calculations and validation helpers."""

from datetime import date
from typing import Any

from database import PRIORITIES, STATUSES


def validate_task_input(title: str, priority: str, status: str, due_date: date | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(title, str) or not title.strip():
        errors.append("Task title is required.")
    elif len(title.strip()) > 120:
        errors.append("Task title must be 120 characters or fewer.")
    if priority not in PRIORITIES:
        errors.append("Choose a valid priority.")
    if status not in STATUSES:
        errors.append("Choose a valid status.")
    if due_date is not None and not isinstance(due_date, date):
        errors.append("Due date must be a date.")
    return errors


def completion_stats(tasks: list[dict[str, Any]]) -> dict[str, int | float]:
    total = len(tasks)
    completed = sum(task.get("status") == "Completed" for task in tasks)
    return {"total": total, "completed": completed,
            "pending": sum(task.get("status") == "Pending" for task in tasks),
            "in_progress": sum(task.get("status") == "In Progress" for task in tasks),
            "completion_pct": round(completed * 100 / total, 1) if total else 0.0}
