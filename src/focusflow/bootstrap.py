"""Application service bootstrap and persistence selection."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

from .auth import AuthService
from .mysql_persistence import SqlAlchemyContext, SqlReminderRepository, SqlTaskRepository, SqlUserRepository
from .reminder_manager import ReminderManager
from .repositories import InMemoryReminderRepository, InMemoryTaskRepository, InMemoryUserRepository
from .task_manager import TaskManager


@dataclass(slots=True)
class ServiceBundle:
    auth: AuthService
    tasks: TaskManager
    reminders: ReminderManager
    backend_name: str


def default_database_url() -> str:
    root = Path(__file__).resolve().parents[2]
    db_path = root / "focusflow.db"
    return f"sqlite+pysqlite:///{db_path.as_posix()}"


def create_service_bundle(
    database_url: str | None = None,
    *,
    fallback_to_in_memory: bool = True,
) -> ServiceBundle:
    resolved_url = database_url or os.getenv("FOCUSFLOW_DB_URL") or default_database_url()

    try:
        context = SqlAlchemyContext(resolved_url)
        context.create_schema()
        user_repo = SqlUserRepository(context)
        task_repo = SqlTaskRepository(context)
        reminder_repo = SqlReminderRepository(context)
        return ServiceBundle(
            auth=AuthService(user_repository=user_repo),
            tasks=TaskManager(task_repository=task_repo),
            reminders=ReminderManager(reminder_repository=reminder_repo, task_repository=task_repo),
            backend_name=resolved_url,
        )
    except SQLAlchemyError:
        if not fallback_to_in_memory:
            raise
        task_repo = InMemoryTaskRepository()
        return ServiceBundle(
            auth=AuthService(user_repository=InMemoryUserRepository()),
            tasks=TaskManager(task_repository=task_repo),
            reminders=ReminderManager(
                reminder_repository=InMemoryReminderRepository(),
                task_repository=task_repo,
            ),
            backend_name="in-memory",
        )
