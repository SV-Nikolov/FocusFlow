"""Repository abstractions and in-memory implementations."""

from __future__ import annotations

from dataclasses import replace
from typing import Protocol

from .models import Task, User


class UserRepository(Protocol):
    def get_by_username(self, username: str) -> User | None: ...
    def save(self, user: User) -> User: ...


class TaskRepository(Protocol):
    def get_by_id(self, task_id: str) -> Task | None: ...
    def save(self, task: Task) -> Task: ...
    def delete(self, task_id: str) -> None: ...
    def list_all(self) -> list[Task]: ...


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users_by_username: dict[str, User] = {}

    def get_by_username(self, username: str) -> User | None:
        user = self._users_by_username.get(username)
        return replace(user) if user is not None else None

    def save(self, user: User) -> User:
        self._users_by_username[user.username] = replace(user)
        return replace(user)


class InMemoryTaskRepository(TaskRepository):
    def __init__(self) -> None:
        self._tasks_by_id: dict[str, Task] = {}

    def get_by_id(self, task_id: str) -> Task | None:
        task = self._tasks_by_id.get(task_id)
        return replace(task) if task is not None else None

    def save(self, task: Task) -> Task:
        self._tasks_by_id[task.task_id] = replace(task)
        return replace(task)

    def delete(self, task_id: str) -> None:
        self._tasks_by_id.pop(task_id, None)

    def list_all(self) -> list[Task]:
        return [replace(task) for task in self._tasks_by_id.values()]
