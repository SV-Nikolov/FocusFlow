"""Task management tab for FocusFlow."""

from PySide6.QtCore import QDate, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)


class TasksView(QWidget):
    """Create, update, delete, and track task status."""

    data_changed = Signal()

    def __init__(self, store) -> None:
        super().__init__()
        self.store = store
        self.selected_task_id: int | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        title = QLabel("Tasks")
        title.setObjectName("TitleLabel")

        self.task_list = QListWidget()
        self.task_list.currentItemChanged.connect(self.load_selected_task)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Task title")

        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)
        self.due_date_input.setDate(QDate.currentDate())

        self.priority_input = QComboBox()
        self.priority_input.addItems(["Low", "Medium", "High"])
        self.priority_input.setCurrentText("Medium")

        self.status_input = QComboBox()
        self.status_input.addItems(["Pending", "In Progress", "Completed"])

        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("School, Work, Personal, etc.")

        self.notes_input = QPlainTextEdit()
        self.notes_input.setPlaceholderText("Optional task notes")
        self.notes_input.setMaximumHeight(90)

        add_button = QPushButton("Add Task")
        add_button.clicked.connect(self.add_task)

        update_button = QPushButton("Update Task")
        update_button.clicked.connect(self.update_task)

        clear_button = QPushButton("Clear")
        clear_button.setObjectName("SecondaryButton")
        clear_button.clicked.connect(self.clear_form)

        delete_button = QPushButton("Delete")
        delete_button.setObjectName("DangerButton")
        delete_button.clicked.connect(self.delete_task)

        form = QFormLayout()
        form.addRow("Title", self.title_input)
        form.addRow("Due Date", self.due_date_input)
        form.addRow("Priority", self.priority_input)
        form.addRow("Status", self.status_input)
        form.addRow("Label", self.label_input)
        form.addRow("Notes", self.notes_input)

        buttons = QHBoxLayout()
        buttons.addWidget(add_button)
        buttons.addWidget(update_button)
        buttons.addWidget(clear_button)
        buttons.addWidget(delete_button)

        form_card = QFrame()
        form_card.setObjectName("Card")
        form_layout = QVBoxLayout(form_card)
        form_layout.addWidget(QLabel("Task Details"))
        form_layout.addLayout(form)
        form_layout.addLayout(buttons)

        list_card = QFrame()
        list_card.setObjectName("Card")
        list_layout = QVBoxLayout(list_card)
        list_layout.addWidget(QLabel("Current Tasks"))
        list_layout.addWidget(self.task_list)

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

        current_id = self.selected_task_id
        self.task_list.blockSignals(True)
        self.task_list.clear()
        for task in self.store.list_tasks():
            item = QListWidgetItem(
                f"#{task.task_id} | {task.status} | {task.due_date:%b %d} | {task.priority} | {task.title}"
            )
            item.setData(1000, task.task_id)
            self.task_list.addItem(item)
            if current_id == task.task_id:
                self.task_list.setCurrentItem(item)
        self.task_list.blockSignals(False)

    def add_task(self) -> None:
        try:
            self.store.create_task(
                title=self.title_input.text(),
                due_date=self.due_date_input.date().toPython(),
                priority=self.priority_input.currentText(),
                label=self.label_input.text(),
                notes=self.notes_input.toPlainText(),
            )
        except ValueError as error:
            QMessageBox.warning(self, "Task Error", str(error))
            return

        self.clear_form()
        self.data_changed.emit()

    def update_task(self) -> None:
        if self.selected_task_id is None:
            QMessageBox.warning(self, "Task Error", "Select a task to update.")
            return
        try:
            self.store.update_task(
                task_id=self.selected_task_id,
                title=self.title_input.text(),
                due_date=self.due_date_input.date().toPython(),
                priority=self.priority_input.currentText(),
                status=self.status_input.currentText(),
                label=self.label_input.text(),
                notes=self.notes_input.toPlainText(),
            )
        except ValueError as error:
            QMessageBox.warning(self, "Task Error", str(error))
            return

        self.data_changed.emit()

    def delete_task(self) -> None:
        if self.selected_task_id is None:
            QMessageBox.warning(self, "Task Error", "Select a task to delete.")
            return
        self.store.delete_task(self.selected_task_id)
        self.clear_form()
        self.data_changed.emit()

    def load_selected_task(self, current, previous) -> None:
        if current is None:
            return
        task_id = current.data(1000)
        task = self.store.get_task(task_id)
        self.selected_task_id = task.task_id
        self.title_input.setText(task.title)
        self.due_date_input.setDate(QDate(task.due_date.year, task.due_date.month, task.due_date.day))
        self.priority_input.setCurrentText(task.priority)
        self.status_input.setCurrentText(task.status)
        self.label_input.setText(task.label)
        self.notes_input.setPlainText(task.notes)

    def clear_form(self) -> None:
        self.selected_task_id = None
        self.task_list.clearSelection()
        self.title_input.clear()
        self.due_date_input.setDate(QDate.currentDate())
        self.priority_input.setCurrentText("Medium")
        self.status_input.setCurrentText("Pending")
        self.label_input.clear()
        self.notes_input.clear()
