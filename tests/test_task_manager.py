from datetime import date, datetime, timedelta, timezone

from focusflow.exceptions import AuthorizationError, InvalidTransitionError, ValidationError
from focusflow.models import TaskPriority, TaskStatus
from focusflow.task_manager import TaskManager


def test_create_and_list_tasks() -> None:
    manager = TaskManager()
    due = date.today() + timedelta(days=2)

    created = manager.create_task(
        user_id="user-1",
        title="Finish capstone section",
        due_date=due,
        description="Write first draft of Phase I report",
        priority=TaskPriority.HIGH,
        label="School",
    )

    tasks = manager.list_tasks(user_id="user-1")
    assert len(tasks) == 1
    assert tasks[0].task_id == created.task_id


def test_create_task_requires_title() -> None:
    manager = TaskManager()

    try:
        manager.create_task(user_id="user-1", title="  ", due_date=date.today())
        assert False, "Expected ValidationError"
    except ValidationError as exc:
        assert "title" in str(exc).lower()


def test_task_status_transition_rules() -> None:
    manager = TaskManager()
    task = manager.create_task(user_id="user-1", title="Task", due_date=date.today())

    manager.transition_status(task_id=task.task_id, user_id="user-1", new_status=TaskStatus.IN_PROGRESS)
    manager.transition_status(task_id=task.task_id, user_id="user-1", new_status=TaskStatus.PAUSED)
    manager.transition_status(task_id=task.task_id, user_id="user-1", new_status=TaskStatus.IN_PROGRESS)
    manager.transition_status(task_id=task.task_id, user_id="user-1", new_status=TaskStatus.COMPLETED)

    assert manager.get_task(task_id=task.task_id, user_id="user-1").status == TaskStatus.COMPLETED



def test_invalid_status_transition_raises() -> None:
    manager = TaskManager()
    task = manager.create_task(user_id="user-1", title="Task", due_date=date.today())

    try:
        manager.transition_status(task_id=task.task_id, user_id="user-1", new_status=TaskStatus.COMPLETED)
        assert False, "Expected InvalidTransitionError"
    except InvalidTransitionError:
        assert True


def test_user_cannot_access_other_users_task() -> None:
    manager = TaskManager()
    task = manager.create_task(user_id="user-1", title="Private", due_date=date.today())

    try:
        manager.get_task(task_id=task.task_id, user_id="user-2")
        assert False, "Expected AuthorizationError"
    except AuthorizationError:
        assert True


def test_mark_overdue_updates_status() -> None:
    manager = TaskManager()
    task = manager.create_task(
        user_id="user-1",
        title="Past task",
        due_date=date.today() - timedelta(days=1),
    )

    changed = manager.mark_overdue(reference_date=date.today())

    assert changed == 1
    assert manager.get_task(task_id=task.task_id, user_id="user-1").status == TaskStatus.OVERDUE


def test_task_time_tracking_when_completed() -> None:
    """
    Verifies that completing a task records the total time spent.

    This test simulates a task that has been in progress for
    approximately 30 minutes before being marked as completed.
    The expected behavior is that the task status changes to
    COMPLETED and the total_minutes_spent field is updated.
    """

    manager = TaskManager()

    # Create a new task for testing.
    task = manager.create_task(
        user_id="user-1",
        title="Timed task",
        due_date=date.today(),
    )

    # Start the task so it can legally transition to COMPLETED.
    started = manager.transition_status(
        task_id=task.task_id,
        user_id="user-1",
        new_status=TaskStatus.IN_PROGRESS,
    )

    # Simulate that the task started 30 minutes ago.
    started.started_at = datetime.now(timezone.utc) - timedelta(minutes=30)
    manager._tasks.save(started)

    # Complete the task.
    completed = manager.transition_status(
        task_id=task.task_id,
        user_id="user-1",
        new_status=TaskStatus.COMPLETED,
    )

    # Verify the task status changed successfully.
    assert completed.status == TaskStatus.COMPLETED

    # Verify the total tracked work time is at least 30 minutes.
    assert completed.total_minutes_spent >= 30