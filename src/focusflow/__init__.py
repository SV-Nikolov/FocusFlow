"""FocusFlow package."""

from .auth import AuthService, PasswordHasher
from .bootstrap import ServiceBundle, create_service_bundle, default_database_url
from .models import Reminder, Task, TaskPriority, TaskStatus, User
from .mysql_persistence import (
    MySQLConfig,
    SqlAlchemyContext,
    SqlReminderRepository,
    SqlTaskRepository,
    SqlUserRepository,
)
from .reminder_manager import ReminderManager
from .repositories import InMemoryReminderRepository, InMemoryTaskRepository, InMemoryUserRepository
from .task_manager import TaskManager

__all__ = [
    "AuthService",
    "PasswordHasher",
    "ServiceBundle",
    "create_service_bundle",
    "default_database_url",
    "MySQLConfig",
    "SqlAlchemyContext",
    "SqlReminderRepository",
    "SqlTaskRepository",
    "SqlUserRepository",
    "Reminder",
    "ReminderManager",
    "InMemoryReminderRepository",
    "Task",
    "InMemoryTaskRepository",
    "InMemoryUserRepository",
    "TaskPriority",
    "TaskStatus",
    "TaskManager",
    "User",
]
