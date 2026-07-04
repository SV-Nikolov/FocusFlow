"""Reminder management services for FocusFlow."""

from __future__ import annotations

from datetime import datetime, timezone

from .exceptions import AuthorizationError, NotFoundError, ValidationError
from .models import Reminder
from .repositories import ReminderRepository, TaskRepository


class ReminderManager:
    def __init__(self, *, reminder_repository: ReminderRepository, task_repository: TaskRepository) -> None:
        self._reminders = reminder_repository
        self._tasks = task_repository

    def create_reminder(
        self,
        *,
        user_id: str,
        task_id: str,
        remind_at: datetime,
        message: str,
    ) -> Reminder:
        self._validate_task_owner(user_id=user_id, task_id=task_id)
        normalized_message = message.strip()
        if not normalized_message:
            raise ValidationError("Reminder message is required.")
        if remind_at.tzinfo is None:
            raise ValidationError("Reminder datetime must include timezone info.")
        if remind_at < datetime.now(timezone.utc):
            raise ValidationError("Reminder datetime cannot be in the past.")

        reminder = Reminder(task_id=task_id, remind_at=remind_at, message=normalized_message)
        return self._reminders.save(reminder)

    def update_reminder(
        self,
        *,
        user_id: str,
        reminder_id: str,
        remind_at: datetime,
        message: str,
    ) -> Reminder:
        reminder = self.get_reminder(user_id=user_id, reminder_id=reminder_id)
        normalized_message = message.strip()
        if not normalized_message:
            raise ValidationError("Reminder message is required.")
        if remind_at.tzinfo is None:
            raise ValidationError("Reminder datetime must include timezone info.")

        reminder.remind_at = remind_at
        reminder.message = normalized_message
        return self._reminders.save(reminder)

    def get_reminder(self, *, user_id: str, reminder_id: str) -> Reminder:
        reminder = self._reminders.get_by_id(reminder_id)
        if reminder is None:
            raise NotFoundError("Reminder not found.")
        self._validate_task_owner(user_id=user_id, task_id=reminder.task_id)
        return reminder

    def delete_reminder(self, *, user_id: str, reminder_id: str) -> None:
        reminder = self.get_reminder(user_id=user_id, reminder_id=reminder_id)
        self._reminders.delete(reminder.reminder_id)

    def acknowledge(self, *, user_id: str, reminder_id: str, acknowledged: bool = True) -> Reminder:
        reminder = self.get_reminder(user_id=user_id, reminder_id=reminder_id)
        reminder.is_acknowledged = acknowledged
        return self._reminders.save(reminder)

    def list_reminders(self, *, user_id: str, include_acknowledged: bool = True) -> list[Reminder]:
        reminders: list[Reminder] = []
        for reminder in self._reminders.list_all():
            if not include_acknowledged and reminder.is_acknowledged:
                continue
            task = self._tasks.get_by_id(reminder.task_id)
            if task is None:
                continue
            if task.user_id != user_id:
                continue
            reminders.append(reminder)
        return sorted(reminders, key=lambda item: item.remind_at)

    def _validate_task_owner(self, *, user_id: str, task_id: str) -> None:
        task = self._tasks.get_by_id(task_id)
        if task is None:
            raise NotFoundError("Task for reminder was not found.")
        if task.user_id != user_id:
            raise AuthorizationError("Task does not belong to this user.")
