from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest

from focusflow.exceptions import AuthorizationError, ValidationError
from focusflow.models import TaskPriority
from focusflow.reminder_manager import ReminderManager
from focusflow.repositories import InMemoryReminderRepository, InMemoryTaskRepository
from focusflow.task_manager import TaskManager


def _make_task_repo_with_task(user_id: str = "user-1") -> tuple[InMemoryTaskRepository, str]:
    task_repo = InMemoryTaskRepository()
    task_manager = TaskManager(task_repository=task_repo)
    task = task_manager.create_task(
        user_id=user_id,
        title="Prepare release",
        due_date=date.today() + timedelta(days=1),
        priority=TaskPriority.MEDIUM,
    )
    return task_repo, task.task_id


def test_create_and_list_reminders() -> None:
    task_repo, task_id = _make_task_repo_with_task()
    manager = ReminderManager(
        reminder_repository=InMemoryReminderRepository(),
        task_repository=task_repo,
    )

    reminder = manager.create_reminder(
        user_id="user-1",
        task_id=task_id,
        remind_at=datetime.now(timezone.utc) + timedelta(hours=1),
        message="Start task",
    )

    reminders = manager.list_reminders(user_id="user-1")

    assert len(reminders) == 1
    assert reminders[0].reminder_id == reminder.reminder_id


def test_cannot_create_past_reminder() -> None:
    task_repo, task_id = _make_task_repo_with_task()
    manager = ReminderManager(
        reminder_repository=InMemoryReminderRepository(),
        task_repository=task_repo,
    )

    with pytest.raises(ValidationError):
        manager.create_reminder(
            user_id="user-1",
            task_id=task_id,
            remind_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            message="Late reminder",
        )


def test_acknowledge_and_delete_reminder() -> None:
    task_repo, task_id = _make_task_repo_with_task()
    manager = ReminderManager(
        reminder_repository=InMemoryReminderRepository(),
        task_repository=task_repo,
    )
    reminder = manager.create_reminder(
        user_id="user-1",
        task_id=task_id,
        remind_at=datetime.now(timezone.utc) + timedelta(hours=2),
        message="Acknowledge me",
    )

    acknowledged = manager.acknowledge(user_id="user-1", reminder_id=reminder.reminder_id)
    assert acknowledged.is_acknowledged is True

    manager.delete_reminder(user_id="user-1", reminder_id=reminder.reminder_id)
    assert manager.list_reminders(user_id="user-1") == []


def test_cannot_access_other_user_task_reminder() -> None:
    task_repo, task_id = _make_task_repo_with_task(user_id="user-1")
    manager = ReminderManager(
        reminder_repository=InMemoryReminderRepository(),
        task_repository=task_repo,
    )

    with pytest.raises(AuthorizationError):
        manager.create_reminder(
            user_id="user-2",
            task_id=task_id,
            remind_at=datetime.now(timezone.utc) + timedelta(hours=1),
            message="Cross-user",
        )
