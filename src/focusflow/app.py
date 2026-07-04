"""Interactive FocusFlow desktop application baseline."""

from __future__ import annotations

import sys
from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .bootstrap import ServiceBundle, create_service_bundle
from .exceptions import FocusFlowError
from .models import TaskPriority, TaskStatus, User


STATUS_FILTER_OPTIONS = [
    "All",
    TaskStatus.NOT_STARTED.value,
    TaskStatus.IN_PROGRESS.value,
    TaskStatus.PAUSED.value,
    TaskStatus.COMPLETED.value,
    TaskStatus.OVERDUE.value,
]


def _priority_from_text(priority_text: str) -> TaskPriority:
    return {
        TaskPriority.LOW.value: TaskPriority.LOW,
        TaskPriority.MEDIUM.value: TaskPriority.MEDIUM,
        TaskPriority.HIGH.value: TaskPriority.HIGH,
    }[priority_text]


def _status_from_text(status_text: str) -> TaskStatus:
    return {
        TaskStatus.NOT_STARTED.value: TaskStatus.NOT_STARTED,
        TaskStatus.IN_PROGRESS.value: TaskStatus.IN_PROGRESS,
        TaskStatus.PAUSED.value: TaskStatus.PAUSED,
        TaskStatus.COMPLETED.value: TaskStatus.COMPLETED,
        TaskStatus.OVERDUE.value: TaskStatus.OVERDUE,
    }[status_text]


class FocusFlowWindow(QMainWindow):
    def __init__(self, services: ServiceBundle) -> None:
        super().__init__()
        self._services = services
        self._current_user: User | None = None
        self._metric_value_labels: dict[str, QLabel] = {}
        self._task_list: QListWidget | None = None
        self._status_filter: QComboBox | None = None
        self._title_input: QLineEdit | None = None
        self._label_input: QLineEdit | None = None
        self._due_date_input: QDateEdit | None = None
        self._priority_input: QComboBox | None = None
        self._description_input: QTextEdit | None = None
        self._reminder_list: QListWidget | None = None
        self._stats_text: QLabel | None = None

        self._login_username: QLineEdit | None = None
        self._login_password: QLineEdit | None = None
        self._register_username: QLineEdit | None = None
        self._register_password: QLineEdit | None = None
        self._register_email: QLineEdit | None = None

        self._pages = QStackedWidget(self)
        self.setWindowTitle("FocusFlow")
        self.resize(1240, 760)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget(self)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.addWidget(self._pages)

        self._pages.addWidget(self._build_login_page())
        self._pages.addWidget(self._build_main_page())
        self._pages.setCurrentIndex(0)
        self.setCentralWidget(root)

    def _build_login_page(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("FocusFlow")
        title.setFont(QFont("Segoe UI", 30, QFont.Weight.Bold))
        subtitle = QLabel("Sign in or create an account to manage your tasks")
        subtitle.setStyleSheet("color: #555;")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        forms = QHBoxLayout()
        forms.setSpacing(16)

        login_panel = self._panel("Login")
        login_form = QFormLayout()
        self._login_username = QLineEdit()
        self._login_password = QLineEdit()
        self._login_password.setEchoMode(QLineEdit.EchoMode.Password)
        login_form.addRow("Username", self._login_username)
        login_form.addRow("Password", self._login_password)
        login_panel.layout().addLayout(login_form)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self._on_login_clicked)
        login_panel.layout().addWidget(login_button)

        register_panel = self._panel("Create Account")
        register_form = QFormLayout()
        self._register_username = QLineEdit()
        self._register_password = QLineEdit()
        self._register_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._register_email = QLineEdit()
        register_form.addRow("Username", self._register_username)
        register_form.addRow("Password", self._register_password)
        register_form.addRow("Email", self._register_email)
        register_panel.layout().addLayout(register_form)

        register_button = QPushButton("Register")
        register_button.clicked.connect(self._on_register_clicked)
        register_panel.layout().addWidget(register_button)

        forms.addWidget(login_panel)
        forms.addWidget(register_panel)
        layout.addLayout(forms)
        layout.addStretch(1)

        return page

    def _build_main_page(self) -> QWidget:
        page = QWidget(self)
        root_layout = QVBoxLayout(page)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(14)

        title = QLabel("FocusFlow")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        subtitle = QLabel(f"Task dashboard | Backend: {self._services.backend_name}")
        subtitle.setStyleSheet("color: #555;")

        top_actions = QHBoxLayout()
        top_actions.addStretch(1)
        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self._on_logout_clicked)
        top_actions.addWidget(logout_button)

        header = QVBoxLayout()
        header.addWidget(title)
        header.addWidget(subtitle)
        header.addLayout(top_actions)

        root_layout.addLayout(header)

        cards = QGridLayout()
        cards.setHorizontalSpacing(12)
        cards.setVerticalSpacing(12)

        cards.addWidget(self._metric_card("Total Tasks", "0", "total"), 0, 0)
        cards.addWidget(self._metric_card("Active Tasks", "0", "active"), 0, 1)
        cards.addWidget(self._metric_card("Completed", "0", "completed"), 0, 2)
        cards.addWidget(self._metric_card("Overdue", "0", "overdue"), 0, 3)

        root_layout.addLayout(cards)

        content = QHBoxLayout()
        content.setSpacing(12)

        task_panel = self._panel("Tasks")
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Status"))
        self._status_filter = QComboBox()
        self._status_filter.addItems(STATUS_FILTER_OPTIONS)
        self._status_filter.currentIndexChanged.connect(self.refresh_view)
        filter_row.addWidget(self._status_filter)
        filter_row.addStretch(1)
        task_panel.layout().addLayout(filter_row)

        self._task_list = QListWidget()
        task_panel.layout().addWidget(self._task_list)

        actions = QHBoxLayout()
        add_button = QPushButton("Add Task")
        add_button.clicked.connect(self._on_add_task_clicked)
        load_button = QPushButton("Load")
        load_button.clicked.connect(self._on_load_selected_clicked)
        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(self._on_save_changes_clicked)
        start_button = QPushButton("Start")
        start_button.clicked.connect(lambda: self._transition_selected(TaskStatus.IN_PROGRESS))
        pause_button = QPushButton("Pause")
        pause_button.clicked.connect(lambda: self._transition_selected(TaskStatus.PAUSED))
        complete_button = QPushButton("Complete")
        complete_button.clicked.connect(lambda: self._transition_selected(TaskStatus.COMPLETED))
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self._on_delete_task_clicked)
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_view)

        actions.addWidget(add_button)
        actions.addWidget(load_button)
        actions.addWidget(save_button)
        actions.addWidget(start_button)
        actions.addWidget(pause_button)
        actions.addWidget(complete_button)
        actions.addWidget(delete_button)
        actions.addWidget(refresh_button)
        task_panel.layout().addLayout(actions)

        task_form = self._panel("Create Task")
        form_layout = QFormLayout()
        self._title_input = QLineEdit()
        self._label_input = QLineEdit()
        self._due_date_input = QDateEdit()
        self._due_date_input.setCalendarPopup(True)
        self._due_date_input.setDate(QDate.currentDate())
        self._priority_input = QComboBox()
        self._priority_input.addItems([TaskPriority.LOW.value, TaskPriority.MEDIUM.value, TaskPriority.HIGH.value])
        self._priority_input.setCurrentText(TaskPriority.MEDIUM.value)
        self._description_input = QTextEdit()
        self._description_input.setFixedHeight(90)

        form_layout.addRow("Title", self._title_input)
        form_layout.addRow("Label", self._label_input)
        form_layout.addRow("Due Date", self._due_date_input)
        form_layout.addRow("Priority", self._priority_input)
        form_layout.addRow("Description", self._description_input)
        task_form.layout().addLayout(form_layout)

        clear_form_button = QPushButton("Clear Form")
        clear_form_button.clicked.connect(self._clear_form)
        task_form.layout().addWidget(clear_form_button)

        reminder_panel = self._panel("Upcoming Reminders")
        self._reminder_list = QListWidget()
        reminder_panel.layout().addWidget(self._reminder_list)

        stats_panel = self._panel("Quick Stats")
        self._stats_text = QLabel("")
        self._stats_text.setAlignment(Qt.AlignmentFlag.AlignTop)
        stats_panel.layout().addWidget(self._stats_text)

        left_stack = QVBoxLayout()
        left_stack.addWidget(task_panel, 3)
        left_stack.addWidget(task_form, 2)

        content.addLayout(left_stack, 2)
        right_stack = QVBoxLayout()
        right_stack.addWidget(reminder_panel)
        right_stack.addWidget(stats_panel)
        content.addLayout(right_stack, 1)

        root_layout.addLayout(content)
        return page

    def _panel(self, title: str) -> QFrame:
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setStyleSheet("QFrame { background: #fafafa; border: 1px solid #dcdcdc; border-radius: 8px; }")

        layout = QVBoxLayout(panel)
        label = QLabel(title)
        label.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        layout.addWidget(label)
        return panel

    def _metric_card(self, label: str, value: str, metric_key: str) -> QFrame:
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet("QFrame { background: #f0f4ff; border: 1px solid #cdd8ff; border-radius: 8px; }")

        layout = QVBoxLayout(card)
        metric = QLabel(value)
        metric.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self._metric_value_labels[metric_key] = metric
        text = QLabel(label)
        text.setStyleSheet("color: #3a3a3a;")
        layout.addWidget(metric)
        layout.addWidget(text)
        return card

    def _show_error(self, message: str) -> None:
        QMessageBox.critical(self, "FocusFlow", message)

    def _show_info(self, message: str) -> None:
        QMessageBox.information(self, "FocusFlow", message)

    def _selected_task_id(self) -> str | None:
        if self._task_list is None:
            return None
        item = self._task_list.currentItem()
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def _on_login_clicked(self) -> None:
        if self._login_username is None or self._login_password is None:
            return
        username = self._login_username.text().strip()
        password = self._login_password.text()
        if not username or not password:
            self._show_error("Enter username and password.")
            return

        user = self._services.auth.authenticate_user(username, password)
        if user is None:
            self._show_error("Invalid username or password.")
            return

        self._current_user = user
        self._pages.setCurrentIndex(1)
        self.refresh_view()

    def _on_register_clicked(self) -> None:
        if self._register_username is None or self._register_password is None or self._register_email is None:
            return
        username = self._register_username.text().strip()
        password = self._register_password.text()
        email = self._register_email.text().strip() or None
        try:
            self._services.auth.register_user(username, password, email)
        except FocusFlowError as exc:
            self._show_error(str(exc))
            return
        self._show_info("Account created. You can now log in.")
        if self._login_username is not None:
            self._login_username.setText(username)
        if self._register_password is not None:
            self._register_password.clear()

    def _on_logout_clicked(self) -> None:
        self._current_user = None
        self._pages.setCurrentIndex(0)

    def _on_add_task_clicked(self) -> None:
        if self._current_user is None:
            return
        if (
            self._title_input is None
            or self._label_input is None
            or self._due_date_input is None
            or self._priority_input is None
            or self._description_input is None
        ):
            return
        title = self._title_input.text().strip()
        label = self._label_input.text().strip() or None
        due = self._due_date_input.date().toPython()
        priority = _priority_from_text(self._priority_input.currentText())
        description = self._description_input.toPlainText().strip()

        try:
            self._services.tasks.create_task(
                user_id=self._current_user.user_id,
                title=title,
                due_date=due,
                label=label,
                priority=priority,
                description=description,
            )
        except FocusFlowError as exc:
            self._show_error(str(exc))
            return

        self._title_input.clear()
        self._label_input.clear()
        self._description_input.clear()
        self.refresh_view()

    def _on_load_selected_clicked(self) -> None:
        if self._current_user is None:
            return
        task_id = self._selected_task_id()
        if task_id is None:
            self._show_error("Select a task first.")
            return
        try:
            task = self._services.tasks.get_task(task_id=task_id, user_id=self._current_user.user_id)
        except FocusFlowError as exc:
            self._show_error(str(exc))
            return
        if (
            self._title_input is None
            or self._label_input is None
            or self._due_date_input is None
            or self._priority_input is None
            or self._description_input is None
        ):
            return
        self._title_input.setText(task.title)
        self._label_input.setText(task.label or "")
        self._due_date_input.setDate(QDate(task.due_date.year, task.due_date.month, task.due_date.day))
        self._priority_input.setCurrentText(task.priority.value)
        self._description_input.setPlainText(task.description)

    def _on_save_changes_clicked(self) -> None:
        if self._current_user is None:
            return
        task_id = self._selected_task_id()
        if task_id is None:
            self._show_error("Select a task first.")
            return
        if (
            self._title_input is None
            or self._label_input is None
            or self._due_date_input is None
            or self._priority_input is None
            or self._description_input is None
        ):
            return
        try:
            self._services.tasks.update_task(
                task_id=task_id,
                user_id=self._current_user.user_id,
                title=self._title_input.text().strip(),
                label=self._label_input.text().strip() or None,
                due_date=self._due_date_input.date().toPython(),
                priority=_priority_from_text(self._priority_input.currentText()),
                description=self._description_input.toPlainText().strip(),
            )
        except FocusFlowError as exc:
            self._show_error(str(exc))
            return
        self.refresh_view()

    def _clear_form(self) -> None:
        if self._title_input is not None:
            self._title_input.clear()
        if self._label_input is not None:
            self._label_input.clear()
        if self._description_input is not None:
            self._description_input.clear()
        if self._priority_input is not None:
            self._priority_input.setCurrentText(TaskPriority.MEDIUM.value)
        if self._due_date_input is not None:
            self._due_date_input.setDate(QDate.currentDate())

    def _on_delete_task_clicked(self) -> None:
        if self._current_user is None:
            return
        task_id = self._selected_task_id()
        if task_id is None:
            self._show_error("Select a task first.")
            return
        try:
            self._services.tasks.delete_task(task_id=task_id, user_id=self._current_user.user_id)
        except FocusFlowError as exc:
            self._show_error(str(exc))
            return
        self.refresh_view()

    def _transition_selected(self, new_status: TaskStatus) -> None:
        if self._current_user is None:
            return
        task_id = self._selected_task_id()
        if task_id is None:
            self._show_error("Select a task first.")
            return
        try:
            self._services.tasks.transition_status(
                task_id=task_id,
                user_id=self._current_user.user_id,
                new_status=new_status,
            )
        except FocusFlowError as exc:
            self._show_error(str(exc))
            return
        self.refresh_view()

    def refresh_view(self) -> None:
        if self._current_user is None:
            return

        self._services.tasks.mark_overdue(reference_date=date.today())
        all_tasks = self._services.tasks.list_tasks(user_id=self._current_user.user_id)
        selected_filter = self._status_filter.currentText() if self._status_filter is not None else "All"
        if selected_filter != "All":
            filtered_tasks = [task for task in all_tasks if task.status == _status_from_text(selected_filter)]
        else:
            filtered_tasks = all_tasks

        if self._task_list is not None:
            self._task_list.clear()
            for task in filtered_tasks:
                item = QListWidgetItem(
                    f"{task.title} | Due: {task.due_date.isoformat()} | {task.priority.value} | {task.status.value}"
                )
                item.setData(Qt.ItemDataRole.UserRole, task.task_id)
                self._task_list.addItem(item)

        total = len(all_tasks)
        active = len([task for task in all_tasks if task.status in {TaskStatus.NOT_STARTED, TaskStatus.IN_PROGRESS, TaskStatus.PAUSED}])
        completed = len([task for task in all_tasks if task.status == TaskStatus.COMPLETED])
        overdue = len([task for task in all_tasks if task.status == TaskStatus.OVERDUE])

        self._metric_value_labels["total"].setText(str(total))
        self._metric_value_labels["active"].setText(str(active))
        self._metric_value_labels["completed"].setText(str(completed))
        self._metric_value_labels["overdue"].setText(str(overdue))

        if self._reminder_list is not None:
            self._reminder_list.clear()
            upcoming = [task for task in all_tasks if task.status != TaskStatus.COMPLETED]
            upcoming.sort(key=lambda task: task.due_date)
            for task in upcoming[:8]:
                QListWidgetItem(f"{task.due_date.isoformat()} - {task.title}", self._reminder_list)

        if self._stats_text is not None:
            labels: dict[str, int] = {}
            for task in all_tasks:
                key = task.label or "Unlabeled"
                labels[key] = labels.get(key, 0) + 1
            labels_summary = "\n".join([f"{name}: {count} tasks" for name, count in sorted(labels.items())]) or "No labels yet"
            completion_rate = 0.0 if total == 0 else (completed / total) * 100
            self._stats_text.setText(
                f"User: {self._current_user.username}\n"
                f"Completion rate: {completion_rate:.1f}%\n\n"
                f"By label:\n{labels_summary}"
            )


def main() -> int:
    app = QApplication(sys.argv)
    services = create_service_bundle()
    window = FocusFlowWindow(services)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
