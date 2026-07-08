"""Calendar tab for date-based task viewing."""

from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCalendarWidget,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QVBoxLayout,
    QWidget,
)


class CalendarView(QWidget):
    """Displays tasks assigned to the selected calendar date."""

    def __init__(self, store) -> None:
        super().__init__()
        self.store = store
        self._build_ui()

    def _build_ui(self) -> None:
        title = QLabel("Calendar")
        title.setObjectName("TitleLabel")

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar.selectionChanged.connect(self.refresh)

        self.date_label = QLabel()
        self.date_label.setObjectName("SectionTitle")

        self.tasks_for_day = QListWidget()

        calendar_card = QFrame()
        calendar_card.setObjectName("Card")
        calendar_layout = QVBoxLayout(calendar_card)
        calendar_layout.addWidget(QLabel("Select a Date"))
        calendar_layout.addWidget(self.calendar)

        tasks_card = QFrame()
        tasks_card.setObjectName("Card")
        tasks_layout = QVBoxLayout(tasks_card)
        tasks_layout.addWidget(self.date_label)
        tasks_layout.addWidget(self.tasks_for_day)

        body = QHBoxLayout()
        body.addWidget(calendar_card, 2)
        body.addWidget(tasks_card, 3)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addLayout(body)

    def refresh(self) -> None:
        if not self.store.current_user:
            return

        selected = self.calendar.selectedDate().toPython()
        self.date_label.setText(f"Tasks for {selected:%A, %B %d, %Y}")
        self.tasks_for_day.clear()

        tasks = self.store.tasks_for_date(selected)
        if not tasks:
            self.tasks_for_day.addItem("No tasks scheduled for this date.")
            return

        for task in tasks:
            self.tasks_for_day.addItem(
                f"{task.status} | {task.priority} | {task.title} | Label: {task.label}"
            )
