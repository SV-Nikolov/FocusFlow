"""Task management services for FocusFlow Phase I."""

from __future__ import annotations

from datetime import date, datetime, timezone

from .exceptions import AuthorizationError, InvalidTransitionError, NotFoundError, ValidationError
from .models import Task, TaskPriority, TaskStatus
from .repositories import InMemoryTaskRepository, TaskRepository


_ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.NOT_STARTED: {TaskStatus.IN_PROGRESS, TaskStatus.OVERDUE},
    TaskStatus.IN_PROGRESS: {TaskStatus.PAUSED, TaskStatus.COMPLETED, TaskStatus.OVERDUE},
    TaskStatus.PAUSED: {TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED, TaskStatus.OVERDUE},
    TaskStatus.OVERDUE: {TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED},
    TaskStatus.COMPLETED: set(),
}


class TaskManager:
    """In-memory task CRUD and workflow transitions."""

    def __init__(self, task_repository: TaskRepository | None = None) -> None:
        self._tasks = task_repository or InMemoryTaskRepository()

    def create_task(
        self,
        *,
        user_id: str,
        title: str,
        due_date: date,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        label: str | None = None,
    ) -> Task:
        title = title.strip()
        if not title:
            raise ValidationError("Task title is required.")
        if not isinstance(due_date, date):
            raise ValidationError("Task due_date must be a date instance.")

        task = Task(
            user_id=user_id,
            title=title,
            due_date=due_date,
            description=description,
            priority=priority,
            label=label,
        )
        return self._tasks.save(task)

    def get_task(self, *, task_id: str, user_id: str) -> Task:
        task = self._tasks.get_by_id(task_id)
        if task is None:
            raise NotFoundError("Task not found.")
        if task.user_id != user_id:
            raise AuthorizationError("Task does not belong to this user.")
        return task

    def update_task(
        self,
        *,
        task_id: str,
        user_id: str,
        title: str | None = None,
        description: str | None = None,
        due_date: date | None = None,
        priority: TaskPriority | None = None,
        label: str | None = None,
    ) -> Task:
        task = self.get_task(task_id=task_id, user_id=user_id)
        if title is not None:
            new_title = title.strip()
            if not new_title:
                raise ValidationError("Task title cannot be empty.")
            task.title = new_title
        if description is not None:
            task.description = description
        if due_date is not None:
            if not isinstance(due_date, date):
                raise ValidationError("Task due_date must be a date instance.")
            task.due_date = due_date
        if priority is not None:
            task.priority = priority
        if label is not None:
            task.label = label
        return self._tasks.save(task)

    def delete_task(self, *, task_id: str, user_id: str) -> None:
        task = self.get_task(task_id=task_id, user_id=user_id)
        self._tasks.delete(task.task_id)

    def transition_status(self, *, task_id: str, user_id: str, new_status: TaskStatus) -> Task:
        task = self.get_task(task_id=task_id, user_id=user_id)
        if new_status == task.status:
            return task
        allowed = _ALLOWED_TRANSITIONS[task.status]
        if new_status not in allowed:
            raise InvalidTransitionError(
                f"Cannot move from '{task.status.value}' to '{new_status.value}'."
            )

        previous_status = task.status
        task.status = new_status
        now = datetime.now(timezone.utc)
        if previous_status == TaskStatus.NOT_STARTED and new_status == TaskStatus.IN_PROGRESS:
            task.started_at = now
        if new_status == TaskStatus.COMPLETED:
            task.completed_at = now
        return self._tasks.save(task)

    def list_tasks(
        self,
        *,
        user_id: str,
        status: TaskStatus | None = None,
        label: str | None = None,
    ) -> list[Task]:
        tasks = [task for task in self._tasks.list_all() if task.user_id == user_id]
        if status is not None:
            tasks = [task for task in tasks if task.status == status]
        if label is not None:
            tasks = [task for task in tasks if task.label == label]
        return sorted(tasks, key=lambda item: (item.due_date, item.created_at))

    def mark_overdue(self, *, reference_date: date) -> int:
        count = 0
        for task in self._tasks.list_all():
            if task.status == TaskStatus.COMPLETED:
                continue
            if task.due_date < reference_date and task.status != TaskStatus.OVERDUE:
                task.status = TaskStatus.OVERDUE
                self._tasks.save(task)
                count += 1
        return count
