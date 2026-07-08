"""Main window, in-memory store, and shell layout for FocusFlow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from views.calendar_view import CalendarView
from views.dashboard_view import DashboardView
from views.login_view import LoginView
from views.reminders_view import RemindersView
from views.tasks_view import TasksView


@dataclass
class User:
    """A registered FocusFlow user."""

    username: str
    password: str
    email: str = ""


@dataclass
class Task:
    """A task managed by a FocusFlow user."""

    task_id: int
    username: str
    title: str
    due_date: date
    priority: str = "Medium"
    status: str = "Pending"
    label: str = "General"
    notes: str = ""


@dataclass
class Reminder:
    """A reminder attached to a task."""

    reminder_id: int
    username: str
    task_id: int
    remind_at: datetime
    message: str
    acknowledged: bool = False


class FocusFlowStore:
    """
    Small in-memory data store used by the GUI scaffold.

    In the full capstone project, these methods can be swapped to call the service layer
    and repository layer described in the Phase I source-code design.
    """

    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.tasks: list[Task] = []
        self.reminders: list[Reminder] = []
        self.current_user: Optional[str] = None
        self._next_task_id = 1
        self._next_reminder_id = 1
        self._seed_demo_data()

    def _seed_demo_data(self) -> None:
        """Create a demo account so the app has useful data on first launch."""
        self.register_user("student", "StrongPass123", "student@example.com")
        self.current_user = "student"
        self.create_task(
            title="Finish Phase I source code report",
            due_date=date.today(),
            priority="High",
            label="School",
            notes="Review GUI, tests, and documentation before submission.",
        )
        self.create_task(
            title="Review team pull request",
            due_date=date.today() + timedelta(days=1),
            priority="Medium",
            label="Capstone",
            notes="Check readability, naming, and task/reminder workflows.",
        )
        self.create_task(
            title="Prepare Phase II enhancement list",
            due_date=date.today() + timedelta(days=3),
            priority="Low",
            label="Planning",
            notes="Add analytics and notification improvements.",
        )
        self.create_reminder(
            task_id=1,
            remind_at=datetime.now(timezone.utc) + timedelta(hours=4),
            message="Review implementation and tests.",
        )
        self.current_user = None

    def register_user(self, username: str, password: str, email: str = "") -> User:
        username = username.strip()
        email = email.strip()
        if not username:
            raise ValueError("Username is required.")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if username in self.users:
            raise ValueError("That username already exists.")

        user = User(username=username, password=password, email=email)
        self.users[username] = user
        return user

    def authenticate(self, username: str, password: str) -> User:
        user = self.users.get(username.strip())
        if user is None or user.password != password:
            raise ValueError("Invalid username or password.")
        self.current_user = user.username
        return user

    def require_user(self) -> str:
        if not self.current_user:
            raise RuntimeError("No user is currently logged in.")
        return self.current_user

    def create_task(
        self,
        title: str,
        due_date: date,
        priority: str,
        label: str,
        notes: str = "",
    ) -> Task:
        username = self.require_user()
        title = title.strip()
        if not title:
            raise ValueError("Task title is required.")

        task = Task(
            task_id=self._next_task_id,
            username=username,
            title=title,
            due_date=due_date,
            priority=priority,
            label=label.strip() or "General",
            notes=notes.strip(),
        )
        self._next_task_id += 1
        self.tasks.append(task)
        return task

    def update_task(
        self,
        task_id: int,
        title: str,
        due_date: date,
        priority: str,
        status: str,
        label: str,
        notes: str,
    ) -> Task:
        task = self.get_task(task_id)
        title = title.strip()
        if not title:
            raise ValueError("Task title is required.")
        task.title = title
        task.due_date = due_date
        task.priority = priority
        task.status = status
        task.label = label.strip() or "General"
        task.notes = notes.strip()
        return task

    def delete_task(self, task_id: int) -> None:
        self.get_task(task_id)
        self.tasks = [task for task in self.tasks if task.task_id != task_id]
        self.reminders = [rem for rem in self.reminders if rem.task_id != task_id]

    def get_task(self, task_id: int) -> Task:
        username = self.require_user()
        for task in self.tasks:
            if task.task_id == task_id and task.username == username:
                return task
        raise ValueError("Task not found.")

    def list_tasks(self) -> list[Task]:
        username = self.require_user()
        return sorted(
            [task for task in self.tasks if task.username == username],
            key=lambda task: (task.due_date, task.priority, task.title.lower()),
        )

    def tasks_for_date(self, target_date: date) -> list[Task]:
        return [task for task in self.list_tasks() if task.due_date == target_date]

    def task_summary(self) -> dict[str, int]:
        tasks = self.list_tasks()
        today = date.today()
        return {
            "total": len(tasks),
            "completed": sum(1 for task in tasks if task.status == "Completed"),
            "pending": sum(1 for task in tasks if task.status == "Pending"),
            "in_progress": sum(1 for task in tasks if task.status == "In Progress"),
            "overdue": sum(
                1
                for task in tasks
                if task.due_date < today and task.status != "Completed"
            ),
        }

    def create_reminder(self, task_id: int, remind_at: datetime, message: str) -> Reminder:
        username = self.require_user()
        self.get_task(task_id)
        message = message.strip()
        if not message:
            raise ValueError("Reminder message is required.")
        if remind_at <= datetime.now(timezone.utc):
            raise ValueError("Reminder must be scheduled for the future.")

        reminder = Reminder(
            reminder_id=self._next_reminder_id,
            username=username,
            task_id=task_id,
            remind_at=remind_at,
            message=message,
        )
        self._next_reminder_id += 1
        self.reminders.append(reminder)
        return reminder

    def update_reminder(self, reminder_id: int, task_id: int, remind_at: datetime, message: str) -> Reminder:
        reminder = self.get_reminder(reminder_id)
        self.get_task(task_id)
        message = message.strip()
        if not message:
            raise ValueError("Reminder message is required.")
        if remind_at <= datetime.now(timezone.utc):
            raise ValueError("Reminder must be scheduled for the future.")
        reminder.task_id = task_id
        reminder.remind_at = remind_at
        reminder.message = message
        return reminder

    def acknowledge_reminder(self, reminder_id: int) -> Reminder:
        reminder = self.get_reminder(reminder_id)
        reminder.acknowledged = True
        return reminder

    def delete_reminder(self, reminder_id: int) -> None:
        self.get_reminder(reminder_id)
        self.reminders = [rem for rem in self.reminders if rem.reminder_id != reminder_id]

    def get_reminder(self, reminder_id: int) -> Reminder:
        username = self.require_user()
        for reminder in self.reminders:
            if reminder.reminder_id == reminder_id and reminder.username == username:
                return reminder
        raise ValueError("Reminder not found.")

    def list_reminders(self, include_acknowledged: bool = True) -> list[Reminder]:
        username = self.require_user()
        reminders = [rem for rem in self.reminders if rem.username == username]
        if not include_acknowledged:
            reminders = [rem for rem in reminders if not rem.acknowledged]
        return sorted(reminders, key=lambda rem: rem.remind_at)


class MainShell(QWidget):
    """Authenticated application shell that hosts the FocusFlow tabs."""

    def __init__(self, store: FocusFlowStore, on_logout) -> None:
        super().__init__()
        self.store = store
        self.on_logout = on_logout

        self.header_label = QLabel()
        self.header_label.setObjectName("TitleLabel")

        logout_button = QPushButton("Logout")
        logout_button.setObjectName("SecondaryButton")
        logout_button.clicked.connect(self.on_logout)

        header = QFrame()
        header.setObjectName("Card")
        header_layout = QHBoxLayout(header)
        header_layout.addWidget(self.header_label)
        header_layout.addStretch()
        header_layout.addWidget(logout_button)

        self.tabs = QTabWidget()
        self.dashboard_view = DashboardView(store)
        self.tasks_view = TasksView(store)
        self.calendar_view = CalendarView(store)
        self.reminders_view = RemindersView(store)

        self.tabs.addTab(self.dashboard_view, "Dashboard")
        self.tabs.addTab(self.tasks_view, "Tasks")
        self.tabs.addTab(self.calendar_view, "Calendar")
        self.tabs.addTab(self.reminders_view, "Reminders")

        self.tasks_view.data_changed.connect(self.refresh_all)
        self.reminders_view.data_changed.connect(self.refresh_all)
        self.tabs.currentChanged.connect(lambda _: self.refresh_all())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)
        layout.addWidget(header)
        layout.addWidget(self.tabs)

    def refresh_all(self) -> None:
        username = self.store.current_user or "User"
        self.header_label.setText(f"FocusFlow — Welcome, {username}")
        self.dashboard_view.refresh()
        self.tasks_view.refresh()
        self.calendar_view.refresh()
        self.reminders_view.refresh()


class FocusFlowApp(QMainWindow):
    """Top-level FocusFlow application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("FocusFlow Productivity Dashboard")
        self.resize(1100, 760)

        self.store = FocusFlowStore()
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_view = LoginView(self.store)
        self.login_view.login_success.connect(self.show_main_shell)
        self.stack.addWidget(self.login_view)

        self.main_shell: Optional[MainShell] = None

    def show_main_shell(self, username: str) -> None:
        if self.main_shell is not None:
            self.stack.removeWidget(self.main_shell)
            self.main_shell.deleteLater()

        self.main_shell = MainShell(self.store, self.logout)
        self.stack.addWidget(self.main_shell)
        self.stack.setCurrentWidget(self.main_shell)
        self.main_shell.refresh_all()
        QMessageBox.information(self, "FocusFlow", f"Welcome back, {username}.")

    def logout(self) -> None:
        self.store.current_user = None
        self.login_view.clear_password()
        self.stack.setCurrentWidget(self.login_view)
