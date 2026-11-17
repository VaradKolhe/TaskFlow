from database import create_task, delete_task, get_task, get_tasks, init_db, update_task, update_task_status


def test_database_initialization_is_repeatable(tmp_path):
    path = tmp_path / "test.db"
    init_db(path)
    init_db(path)
    assert get_tasks(path) == []


def test_create_and_retrieve_task(tmp_path):
    path = tmp_path / "test.db"
    init_db(path)
    task_id = create_task("  Write report  ", "First draft", "High", "2026-12-01", db_path=path)
    task = get_task(task_id, path)
    assert task["title"] == "Write report"
    assert task["description"] == "First draft"
    assert task["priority"] == "High"
    assert task["status"] == "Pending"
    assert len(get_tasks(path)) == 1


def test_update_status_edit_and_delete(tmp_path):
    path = tmp_path / "test.db"
    init_db(path)
    task_id = create_task("Initial", db_path=path)
    assert update_task_status(task_id, "In Progress", path)
    assert get_task(task_id, path)["status"] == "In Progress"
    assert update_task(task_id, "Updated", "Details", "Low", None, "Completed", path)
    assert get_task(task_id, path)["title"] == "Updated"
    assert get_task(task_id, path)["status"] == "Completed"
    assert delete_task(task_id, path)
    assert get_task(task_id, path) is None
    assert not delete_task(task_id, path)


def test_invalid_task_values_are_rejected(tmp_path):
    path = tmp_path / "test.db"
    init_db(path)
    import pytest
    with pytest.raises(ValueError, match="title"):
        create_task("  ", db_path=path)
    with pytest.raises(ValueError, match="Priority"):
        create_task("Valid", priority="Urgent", db_path=path)
