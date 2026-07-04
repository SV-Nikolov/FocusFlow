"""Interactive FocusFlow desktop application baseline."""

from __future__ import annotations

import sys
from datetime import date, datetime, timezone

from PySide6.QtCore import QDate, QDateTime, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QCalendarWidget,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTabWidget,
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
        self._stats_text: QLabel | None = None

        self._calendar_widget: QCalendarWidget | None = None
        self._calendar_task_list: QListWidget | None = None

        self._reminder_list: QListWidget | None = None
        self._reminder_task_select: QComboBox | None = None
        self._reminder_datetime_input: QDateTimeEdit | None = None
        self._reminder_message_input: QLineEdit | None = None

        self._login_username: QLineEdit | None = None
        self._login_password: QLineEdit | None = None
        self._register_username: QLineEdit | None = None
        self._register_password: QLineEdit | None = None
        self._register_email: QLineEdit | None = None

        self._pages = QStackedWidget(self)
        self.setWindowTitle("FocusFlow")
        self.resize(1320, 820)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget(self)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self._pages)

        self._pages.addWidget(self._build_login_page())
        self._pages.addWidget(self._build_main_page())
        self._pages.setCurrentIndex(0)

        self.setCentralWidget(root)
        self._apply_professional_theme()

    def _apply_professional_theme(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                font-family: 'Segoe UI';
                color: #0f172a;
                background: #f5f7fb;
            }
            QMainWindow {
                background: #edf1f7;
            }
            QFrame[card='true'] {
                background: #ffffff;
                border: 1px solid #d7dfec;
                border-radius: 12px;
            }
            QFrame[metric='true'] {
                background: #e9f0ff;
                border: 1px solid #bfd0ff;
                border-radius: 12px;
            }
            QLabel#PageTitle {
                font-size: 30px;
                font-weight: 700;
                color: #0b1224;
            }
            QLabel#SectionTitle {
                font-size: 13px;
                font-weight: 650;
                color: #1e293b;
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QDateTimeEdit {
                background: #ffffff;
                border: 1px solid #c8d3e8;
                border-radius: 8px;
                padding: 6px 8px;
            }
            QListWidget, QCalendarWidget {
                background: #ffffff;
                border: 1px solid #c8d3e8;
                border-radius: 10px;
                padding: 4px;
            }
            QPushButton {
                background: #1f4eb0;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 7px 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #244f9c;
            }
            QPushButton:pressed {
                background: #1e3e78;
            }
            QTabWidget::pane {
                border: 1px solid #d7dfec;
                border-radius: 10px;
                background: #ffffff;
                top: -1px;
            }
            QTabBar::tab {
                background: #e2e8f5;
                border: 1px solid #d7dfec;
                padding: 8px 14px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom-color: #ffffff;
            }
            """
        )

    def _build_login_page(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(42, 36, 42, 36)
        layout.setSpacing(18)

        title = QLabel("FocusFlow")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Professional productivity desktop for tasks, calendar planning, and reminders")
        subtitle.setStyleSheet("color: #44526e;")

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
        root_layout.setContentsMargins(20, 18, 20, 20)
        root_layout.setSpacing(12)

        title = QLabel("FocusFlow")
        title.setObjectName("PageTitle")
        subtitle = QLabel(f"Workspace dashboard | Backend: {self._services.backend_name}")
        subtitle.setStyleSheet("color: #44526e;")

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
        cards.addWidget(self._metric_card("Active", "0", "active"), 0, 1)
        cards.addWidget(self._metric_card("Completed", "0", "completed"), 0, 2)
        cards.addWidget(self._metric_card("Overdue", "0", "overdue"), 0, 3)
        root_layout.addLayout(cards)

        tabs = QTabWidget()
        tabs.addTab(self._build_tasks_tab(), "Tasks")
        tabs.addTab(self._build_calendar_tab(), "Calendar")
        tabs.addTab(self._build_reminders_tab(), "Reminders")
        root_layout.addWidget(tabs)

        return page

    def _build_tasks_tab(self) -> QWidget:
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setSpacing(12)

        task_panel = self._panel("Task Workspace")

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

        actions = QGridLayout()
        add_button = QPushButton("Add")
        add_button.clicked.connect(self._on_add_task_clicked)
        load_button = QPushButton("Load")
        load_button.clicked.connect(self._on_load_selected_clicked)
        save_button = QPushButton("Save")
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

        buttons = [add_button, load_button, save_button, start_button, pause_button, complete_button, delete_button, refresh_button]
        for idx, button in enumerate(buttons):
            actions.addWidget(button, idx // 4, idx % 4)
        task_panel.layout().addLayout(actions)

        task_form = self._panel("Task Details")
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
        self._description_input.setFixedHeight(120)

        form_layout.addRow("Title", self._title_input)
        form_layout.addRow("Label", self._label_input)
        form_layout.addRow("Due Date", self._due_date_input)
        form_layout.addRow("Priority", self._priority_input)
        form_layout.addRow("Description", self._description_input)
        task_form.layout().addLayout(form_layout)

        clear_form_button = QPushButton("Clear Form")
        clear_form_button.clicked.connect(self._clear_form)
        task_form.layout().addWidget(clear_form_button)

        stats_panel = self._panel("Quick Stats")
        self._stats_text = QLabel("")
        self._stats_text.setAlignment(Qt.AlignmentFlag.AlignTop)
        stats_panel.layout().addWidget(self._stats_text)

        right_column = QVBoxLayout()
        right_column.addWidget(task_form)
        right_column.addWidget(stats_panel)

        splitter = QSplitter()
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(task_panel)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addLayout(right_column)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)
        return tab

    def _build_calendar_tab(self) -> QWidget:
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setSpacing(12)

        calendar_panel = self._panel("Calendar")
        self._calendar_widget = QCalendarWidget()
        self._calendar_widget.selectionChanged.connect(self._refresh_calendar_tasks)
        calendar_panel.layout().addWidget(self._calendar_widget)

        selected_panel = self._panel("Tasks on Selected Date")
        self._calendar_task_list = QListWidget()
        selected_panel.layout().addWidget(self._calendar_task_list)

        layout.addWidget(calendar_panel, 2)
        layout.addWidget(selected_panel, 2)
        return tab

    def _build_reminders_tab(self) -> QWidget:
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setSpacing(12)

        reminder_panel = self._panel("Reminder List")
        self._reminder_list = QListWidget()
        reminder_panel.layout().addWidget(self._reminder_list)

        action_row = QHBoxLayout()
        ack_button = QPushButton("Acknowledge")
        ack_button.clicked.connect(lambda: self._on_acknowledge_reminder(True))
        unack_button = QPushButton("Mark Active")
        unack_button.clicked.connect(lambda: self._on_acknowledge_reminder(False))
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self._on_delete_reminder)
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_view)
        action_row.addWidget(ack_button)
        action_row.addWidget(unack_button)
        action_row.addWidget(delete_button)
        action_row.addWidget(refresh_button)
        reminder_panel.layout().addLayout(action_row)

        form_panel = self._panel("Create or Update Reminder")
        form = QFormLayout()
        self._reminder_task_select = QComboBox()
        self._reminder_datetime_input = QDateTimeEdit()
        self._reminder_datetime_input.setCalendarPopup(True)
        self._reminder_datetime_input.setDateTime(QDateTime.currentDateTimeUtc().addSecs(3600))
        self._reminder_message_input = QLineEdit()
        form.addRow("Task", self._reminder_task_select)
        form.addRow("Remind At (UTC)", self._reminder_datetime_input)
        form.addRow("Message", self._reminder_message_input)
        form_panel.layout().addLayout(form)

        reminder_form_actions = QHBoxLayout()
        add_button = QPushButton("Create")
        add_button.clicked.connect(self._on_create_reminder)
        load_button = QPushButton("Load Selected")
        load_button.clicked.connect(self._on_load_reminder)
        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(self._on_save_reminder)
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self._clear_reminder_form)
        reminder_form_actions.addWidget(add_button)
        reminder_form_actions.addWidget(load_button)
        reminder_form_actions.addWidget(save_button)
        reminder_form_actions.addWidget(clear_button)
        form_panel.layout().addLayout(reminder_form_actions)

        layout.addWidget(reminder_panel, 3)
        layout.addWidget(form_panel, 2)
        return tab

    def _panel(self, title: str) -> QFrame:
        panel = QFrame()
        panel.setProperty("card", True)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        label = QLabel(title)
        label.setObjectName("SectionTitle")
        layout.addWidget(label)
        return panel

    def _metric_card(self, label: str, value: str, metric_key: str) -> QFrame:
        card = QFrame()
        card.setProperty("metric", True)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)
        metric = QLabel(value)
        metric.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self._metric_value_labels[metric_key] = metric
        text = QLabel(label)
        text.setStyleSheet("color: #334155;")
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

    def _selected_reminder_id(self) -> str | None:
        if self._reminder_list is None:
            return None
        item = self._reminder_list.currentItem()
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def _selected_task_from_reminder_form(self) -> str | None:
        if self._reminder_task_select is None:
            return None
        return self._reminder_task_select.currentData()

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

        self._clear_form()
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

    def _on_create_reminder(self) -> None:
        if self._current_user is None:
            return
        task_id = self._selected_task_from_reminder_form()
        if task_id is None or self._reminder_datetime_input is None or self._reminder_message_input is None:
            self._show_error("Select a task and enter reminder details.")
            return
        remind_at = self._reminder_datetime_input.dateTime().toPython().astimezone(timezone.utc)
        message = self._reminder_message_input.text().strip()
        try:
            self._services.reminders.create_reminder(
                user_id=self._current_user.user_id,
                task_id=task_id,
                remind_at=remind_at,
                message=message,
            )
        except FocusFlowError as exc:
            self._show_error(str(exc))
            return
        self._clear_reminder_form()
        self.refresh_view()

    def _on_load_reminder(self) -> None:
        if self._current_user is None:
            return
        reminder_id = self._selected_reminder_id()
        if reminder_id is None:
            self._show_error("Select a reminder first.")
            return
        if self._reminder_task_select is None or self._reminder_datetime_input is None or self._reminder_message_input is None:
            return
        try:
            reminder = self._services.reminders.get_reminder(
                user_id=self._current_user.user_id,
                reminder_id=reminder_id,
            )
        except FocusFlowError as exc:
            self._show_error(str(exc))
            return

        idx = self._reminder_task_select.findData(reminder.task_id)
        if idx >= 0:
            self._reminder_task_select.setCurrentIndex(idx)
        self._reminder_datetime_input.setDateTime(QDateTime(reminder.remind_at))
        self._reminder_message_input.setText(reminder.message)

    def _on_save_reminder(self) -> None:
        if self._current_user is None:
            return
        reminder_id = self._selected_reminder_id()
        if reminder_id is None:
            self._show_error("Select a reminder first.")
            return
        if self._reminder_datetime_input is None or self._reminder_message_input is None:
            return

        remind_at = self._reminder_datetime_input.dateTime().toPython().astimezone(timezone.utc)
        message = self._reminder_message_input.text().strip()
        try:
            self._services.reminders.update_reminder(
                user_id=self._current_user.user_id,
                reminder_id=reminder_id,
                remind_at=remind_at,
                message=message,
            )
        except FocusFlowError as exc:
            self._show_error(str(exc))
            return
        self.refresh_view()

    def _on_delete_reminder(self) -> None:
        if self._current_user is None:
            return
        reminder_id = self._selected_reminder_id()
        if reminder_id is None:
            self._show_error("Select a reminder first.")
            return
        try:
            self._services.reminders.delete_reminder(
                user_id=self._current_user.user_id,
                reminder_id=reminder_id,
            )
        except FocusFlowError as exc:
            self._show_error(str(exc))
            return
        self.refresh_view()

    def _on_acknowledge_reminder(self, acknowledged: bool) -> None:
        if self._current_user is None:
            return
        reminder_id = self._selected_reminder_id()
        if reminder_id is None:
            self._show_error("Select a reminder first.")
            return
        try:
            self._services.reminders.acknowledge(
                user_id=self._current_user.user_id,
                reminder_id=reminder_id,
                acknowledged=acknowledged,
            )
        except FocusFlowError as exc:
            self._show_error(str(exc))
            return
        self.refresh_view()

    def _clear_reminder_form(self) -> None:
        if self._reminder_message_input is not None:
            self._reminder_message_input.clear()
        if self._reminder_datetime_input is not None:
            self._reminder_datetime_input.setDateTime(QDateTime.currentDateTimeUtc().addSecs(3600))

    def _refresh_calendar_tasks(self) -> None:
        if self._current_user is None or self._calendar_widget is None or self._calendar_task_list is None:
            return
        selected_date = self._calendar_widget.selectedDate().toPython()
        all_tasks = self._services.tasks.list_tasks(user_id=self._current_user.user_id)
        day_tasks = [task for task in all_tasks if task.due_date == selected_date]
        self._calendar_task_list.clear()
        if not day_tasks:
            QListWidgetItem("No tasks scheduled for this date.", self._calendar_task_list)
            return
        for task in day_tasks:
            QListWidgetItem(f"{task.title} | {task.priority.value} | {task.status.value}", self._calendar_task_list)

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

        if self._reminder_task_select is not None:
            self._reminder_task_select.clear()
            for task in all_tasks:
                self._reminder_task_select.addItem(f"{task.title} ({task.due_date.isoformat()})", task.task_id)

        if self._reminder_list is not None:
            reminders = self._services.reminders.list_reminders(user_id=self._current_user.user_id)
            self._reminder_list.clear()
            if not reminders:
                QListWidgetItem("No reminders created yet.", self._reminder_list)
            for reminder in reminders:
                task = self._services.tasks.get_task(task_id=reminder.task_id, user_id=self._current_user.user_id)
                state = "Ack" if reminder.is_acknowledged else "Active"
                item = QListWidgetItem(
                    f"{reminder.remind_at.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} | {state} | {task.title} | {reminder.message}"
                )
                item.setData(Qt.ItemDataRole.UserRole, reminder.reminder_id)
                self._reminder_list.addItem(item)

        self._refresh_calendar_tasks()


def main() -> int:
    app = QApplication(sys.argv)
    services = create_service_bundle()
    window = FocusFlowWindow(services)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
