from __future__ import annotations

import os
from datetime import date, datetime, timezone

import pytest

from focusflow.models import Task, TaskPriority, TaskStatus, User
from focusflow.mysql_persistence import Base, SqlAlchemyContext, SqlTaskRepository, SqlUserRepository

pytestmark = pytest.mark.mysql


@pytest.fixture()
def mysql_context() -> SqlAlchemyContext:
    url = os.getenv("MYSQL_TEST_URL")
    if not url:
        pytest.skip("MYSQL_TEST_URL not set; skipping MySQL integration tests.")

    context = SqlAlchemyContext(url)
    Base.metadata.drop_all(context.engine)
    Base.metadata.create_all(context.engine)
    return context


def test_sql_user_repository_roundtrip(mysql_context: SqlAlchemyContext) -> None:
    repo = SqlUserRepository(mysql_context)
    user = User(
        user_id="user-1",
        username="alice",
        password_hash="hash-value",
        email="alice@example.com",
        created_at=datetime.now(timezone.utc),
    )

    saved = repo.save(user)
    fetched = repo.get_by_username("alice")

    assert saved.user_id == "user-1"
    assert fetched is not None
    assert fetched.username == "alice"
    assert fetched.email == "alice@example.com"


def test_sql_task_repository_crud(mysql_context: SqlAlchemyContext) -> None:
    repo = SqlTaskRepository(mysql_context)
    task = Task(
        task_id="task-1",
        user_id="user-1",
        title="MySQL integration",
        due_date=date.today(),
        description="Validate repository persistence",
        priority=TaskPriority.HIGH,
        label="School",
        status=TaskStatus.NOT_STARTED,
        created_at=datetime.now(timezone.utc),
    )

    saved = repo.save(task)
    fetched = repo.get_by_id("task-1")

    assert saved.task_id == "task-1"
    assert fetched is not None
    assert fetched.title == "MySQL integration"

    saved.status = TaskStatus.COMPLETED
    repo.save(saved)
    updated = repo.get_by_id("task-1")
    assert updated is not None
    assert updated.status == TaskStatus.COMPLETED

    all_tasks = repo.list_all()
    assert len(all_tasks) == 1

    repo.delete("task-1")
    assert repo.get_by_id("task-1") is None
