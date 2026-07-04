"""Domain models for FocusFlow Phase I."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from uuid import uuid4


class TaskStatus(str, Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    OVERDUE = "Overdue"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


@dataclass(slots=True)
class User:
    username: str
    password_hash: str
    email: str | None = None
    user_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class Task:
    user_id: str
    title: str
    due_date: date
    description: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    label: str | None = None
    status: TaskStatus = TaskStatus.NOT_STARTED
    task_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    total_minutes_spent: int = 0


@dataclass(slots=True)
class Reminder:
    task_id: str
    remind_at: datetime
    message: str
    is_acknowledged: bool = False
    reminder_id: str = field(default_factory=lambda: str(uuid4()))
