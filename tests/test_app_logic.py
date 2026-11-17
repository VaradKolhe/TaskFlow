from datetime import date

from task_logic import completion_stats, validate_task_input


def test_completion_statistics():
    tasks = [{"status": "Completed"}, {"status": "Pending"}, {"status": "In Progress"}, {"status": "Completed"}]
    assert completion_stats(tasks) == {"total": 4, "completed": 2, "pending": 1, "in_progress": 1, "completion_pct": 50.0}
    assert completion_stats([])["completion_pct"] == 0.0


def test_task_input_validation():
    assert validate_task_input("Plan demo", "Medium", "Pending", date(2026, 12, 1)) == []
    errors = validate_task_input(" ", "Urgent", "Blocked")
    assert "Task title is required." in errors
    assert "Choose a valid priority." in errors
    assert "Choose a valid status." in errors
    assert validate_task_input("x" * 121, "Low", "Completed") == ["Task title must be 120 characters or fewer."]
