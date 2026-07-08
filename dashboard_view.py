"""Dashboard tab for FocusFlow summary metrics and daily focus."""

from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class DashboardView(QWidget):
    """Shows the user's daily task list, reminders, and productivity metrics."""

    def __init__(self, store) -> None:
        super().__init__()
        self.store = store
        self.metric_labels: dict[str, QLabel] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        title = QLabel("Dashboard")
        title.setObjectName("TitleLabel")

        self.today_tasks = QListWidget()
        self.upcoming_reminders = QListWidget()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)

        metrics = QGridLayout()
        for index, label in enumerate(["Total", "Completed", "Pending", "In Progress", "Overdue"]):
            card = self._metric_card(label)
            metrics.addWidget(card, index // 3, index % 3)

        left_card = self._list_card("Today's Focus", self.today_tasks)
        right_card = self._list_card("Upcoming Reminders", self.upcoming_reminders)

        progress_card = QFrame()
        progress_card.setObjectName("Card")
        progress_layout = QVBoxLayout(progress_card)
        progress_title = QLabel("Completion Progress")
        progress_title.setObjectName("SectionTitle")
        progress_layout.addWidget(progress_title)
        progress_layout.addWidget(self.progress_bar)

        lists = QHBoxLayout()
        lists.addWidget(left_card)
        lists.addWidget(right_card)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addLayout(metrics)
        layout.addWidget(progress_card)
        layout.addLayout(lists)
        layout.addStretch()

    def _metric_card(self, label: str) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        title = QLabel(label)
        title.setObjectName("CardTitle")
        value = QLabel("0")
        value.setObjectName("MetricValue")
        value.setAlignment(Qt.AlignCenter)
        self.metric_labels[label] = value

        layout = QVBoxLayout(card)
        layout.addWidget(title)
        layout.addWidget(value)
        return card

    def _list_card(self, title_text: str, list_widget: QListWidget) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        title = QLabel(title_text)
        title.setObjectName("SectionTitle")
        layout = QVBoxLayout(card)
        layout.addWidget(title)
        layout.addWidget(list_widget)
        return card

    def refresh(self) -> None:
        if not self.store.current_user:
            return

        summary = self.store.task_summary()
        label_map = {
            "Total": "total",
            "Completed": "completed",
            "Pending": "pending",
            "In Progress": "in_progress",
            "Overdue": "overdue",
        }
        for label, key in label_map.items():
            self.metric_labels[label].setText(str(summary[key]))

        completion = 0
        if summary["total"]:
            completion = round((summary["completed"] / summary["total"]) * 100)
        self.progress_bar.setValue(completion)

        self.today_tasks.clear()
        tasks_today = self.store.tasks_for_date(date.today())
        if not tasks_today:
            self.today_tasks.addItem("No tasks due today. Nice breathing room.")
        for task in tasks_today:
            item = QListWidgetItem(f"{task.status}: {task.title}  |  {task.priority}  |  {task.label}")
            self.today_tasks.addItem(item)

        self.upcoming_reminders.clear()
        reminders = self.store.list_reminders(include_acknowledged=False)[:6]
        if not reminders:
            self.upcoming_reminders.addItem("No upcoming reminders.")
        for reminder in reminders:
            task = self.store.get_task(reminder.task_id)
            remind_time = reminder.remind_at.astimezone().strftime("%b %d, %I:%M %p")
            self.upcoming_reminders.addItem(f"{remind_time} — {task.title}: {reminder.message}")
