"""Reminder management tab for FocusFlow."""

from datetime import datetime, timezone

from PySide6.QtCore import QDateTime, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDateTimeEdit,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class RemindersView(QWidget):
    """Create, update, acknowledge, and delete reminders tied to tasks."""

    data_changed = Signal()

    def __init__(self, store) -> None:
        super().__init__()
        self.store = store
        self.selected_reminder_id: int | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        title = QLabel("Reminders")
        title.setObjectName("TitleLabel")

        self.reminder_list = QListWidget()
        self.reminder_list.currentItemChanged.connect(self.load_selected_reminder)

        self.task_input = QComboBox()

        self.remind_at_input = QDateTimeEdit()
        self.remind_at_input.setCalendarPopup(True)
        self.remind_at_input.setDateTime(QDateTime.currentDateTime().addSecs(3600))

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Reminder message")
        self.message_input.setMaximumHeight(90)

        add_button = QPushButton("Add Reminder")
        add_button.clicked.connect(self.add_reminder)

        update_button = QPushButton("Update Reminder")
        update_button.clicked.connect(self.update_reminder)

        acknowledge_button = QPushButton("Acknowledge")
        acknowledge_button.setObjectName("SecondaryButton")
        acknowledge_button.clicked.connect(self.acknowledge_reminder)

        clear_button = QPushButton("Clear")
        clear_button.setObjectName("SecondaryButton")
        clear_button.clicked.connect(self.clear_form)

        delete_button = QPushButton("Delete")
        delete_button.setObjectName("DangerButton")
        delete_button.clicked.connect(self.delete_reminder)

        form = QFormLayout()
        form.addRow("Task", self.task_input)
        form.addRow("Reminder Time", self.remind_at_input)
        form.addRow("Message", self.message_input)

        buttons = QHBoxLayout()
        buttons.addWidget(add_button)
        buttons.addWidget(update_button)
        buttons.addWidget(acknowledge_button)
        buttons.addWidget(clear_button)
        buttons.addWidget(delete_button)

        form_card = QFrame()
        form_card.setObjectName("Card")
        form_layout = QVBoxLayout(form_card)
        form_layout.addWidget(QLabel("Reminder Details"))
        form_layout.addLayout(form)
        form_layout.addLayout(buttons)

        list_card = QFrame()
        list_card.setObjectName("Card")
        list_layout = QVBoxLayout(list_card)
        list_layout.addWidget(QLabel("Current Reminders"))
        list_layout.addWidget(self.reminder_list)

        body = QHBoxLayout()
        body.addWidget(list_card, 2)
        body.addWidget(form_card, 3)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addLayout(body)

    def refresh(self) -> None:
        if not self.store.current_user:
            return

        current_reminder_id = self.selected_reminder_id
        current_task_id = self.task_input.currentData()

        self.task_input.blockSignals(True)
        self.task_input.clear()
        for task in self.store.list_tasks():
            self.task_input.addItem(f"#{task.task_id} — {task.title}", task.task_id)
            if current_task_id == task.task_id:
                self.task_input.setCurrentIndex(self.task_input.count() - 1)
        self.task_input.blockSignals(False)

        self.reminder_list.blockSignals(True)
        self.reminder_list.clear()
        for reminder in self.store.list_reminders(include_acknowledged=True):
            task = self.store.get_task(reminder.task_id)
            status = "Acknowledged" if reminder.acknowledged else "Active"
            local_time = reminder.remind_at.astimezone().strftime("%b %d, %Y %I:%M %p")
            item = QListWidgetItem(
                f"#{reminder.reminder_id} | {status} | {local_time} | {task.title}: {reminder.message}"
            )
            item.setData(1000, reminder.reminder_id)
            self.reminder_list.addItem(item)
            if current_reminder_id == reminder.reminder_id:
                self.reminder_list.setCurrentItem(item)
        self.reminder_list.blockSignals(False)

    def add_reminder(self) -> None:
        task_id = self.task_input.currentData()
        if task_id is None:
            QMessageBox.warning(self, "Reminder Error", "Create a task before adding reminders.")
            return
        try:
            self.store.create_reminder(
                task_id=task_id,
                remind_at=self._selected_datetime_utc(),
                message=self.message_input.toPlainText(),
            )
        except ValueError as error:
            QMessageBox.warning(self, "Reminder Error", str(error))
            return

        self.clear_form()
        self.data_changed.emit()

    def update_reminder(self) -> None:
        if self.selected_reminder_id is None:
            QMessageBox.warning(self, "Reminder Error", "Select a reminder to update.")
            return
        try:
            self.store.update_reminder(
                reminder_id=self.selected_reminder_id,
                task_id=self.task_input.currentData(),
                remind_at=self._selected_datetime_utc(),
                message=self.message_input.toPlainText(),
            )
        except ValueError as error:
            QMessageBox.warning(self, "Reminder Error", str(error))
            return

        self.data_changed.emit()

    def acknowledge_reminder(self) -> None:
        if self.selected_reminder_id is None:
            QMessageBox.warning(self, "Reminder Error", "Select a reminder to acknowledge.")
            return
        self.store.acknowledge_reminder(self.selected_reminder_id)
        self.data_changed.emit()

    def delete_reminder(self) -> None:
        if self.selected_reminder_id is None:
            QMessageBox.warning(self, "Reminder Error", "Select a reminder to delete.")
            return
        self.store.delete_reminder(self.selected_reminder_id)
        self.clear_form()
        self.data_changed.emit()

    def load_selected_reminder(self, current, previous) -> None:
        if current is None:
            return
        reminder_id = current.data(1000)
        reminder = self.store.get_reminder(reminder_id)
        self.selected_reminder_id = reminder.reminder_id

        for index in range(self.task_input.count()):
            if self.task_input.itemData(index) == reminder.task_id:
                self.task_input.setCurrentIndex(index)
                break

        local_dt = reminder.remind_at.astimezone().replace(tzinfo=None)
        self.remind_at_input.setDateTime(QDateTime(local_dt))
        self.message_input.setPlainText(reminder.message)

    def clear_form(self) -> None:
        self.selected_reminder_id = None
        self.reminder_list.clearSelection()
        self.remind_at_input.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        self.message_input.clear()

    def _selected_datetime_utc(self) -> datetime:
        selected = self.remind_at_input.dateTime().toPython()
        if selected.tzinfo is None:
            selected = selected.astimezone()
        return selected.astimezone(timezone.utc)
