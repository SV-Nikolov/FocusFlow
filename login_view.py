"""Login and registration screen for FocusFlow."""

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class LoginView(QWidget):
    """Allows users to register or log in before reaching the main app."""

    login_success = Signal(str)

    def __init__(self, store) -> None:
        super().__init__()
        self.store = store
        self._build_ui()

    def _build_ui(self) -> None:
        title = QLabel("FocusFlow")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Plan tasks, track reminders, and stay focused from one desktop dashboard.")
        subtitle.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("Card")
        card.setMaximumWidth(520)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setText("student")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email for registration only")
        self.email_input.setText("student@example.com")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText("StrongPass123")
        self.password_input.returnPressed.connect(self.login)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)

        register_button = QPushButton("Register")
        register_button.setObjectName("SecondaryButton")
        register_button.clicked.connect(self.register)

        form = QGridLayout()
        form.addWidget(QLabel("Username"), 0, 0)
        form.addWidget(self.username_input, 0, 1)
        form.addWidget(QLabel("Email"), 1, 0)
        form.addWidget(self.email_input, 1, 1)
        form.addWidget(QLabel("Password"), 2, 0)
        form.addWidget(self.password_input, 2, 1)

        buttons = QHBoxLayout()
        buttons.addWidget(login_button)
        buttons.addWidget(register_button)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(8)
        card_layout.addLayout(form)
        card_layout.addLayout(buttons)
        card_layout.addWidget(QLabel("Demo account: student / StrongPass123"))

        page_layout = QVBoxLayout(self)
        page_layout.addStretch()
        page_layout.addWidget(card, alignment=Qt.AlignCenter)
        page_layout.addStretch()

    def login(self) -> None:
        try:
            user = self.store.authenticate(
                self.username_input.text(),
                self.password_input.text(),
            )
        except ValueError as error:
            QMessageBox.warning(self, "Login Failed", str(error))
            return

        self.login_success.emit(user.username)

    def register(self) -> None:
        try:
            user = self.store.register_user(
                self.username_input.text(),
                self.password_input.text(),
                self.email_input.text(),
            )
            self.store.current_user = user.username
        except ValueError as error:
            QMessageBox.warning(self, "Registration Failed", str(error))
            return

        QMessageBox.information(self, "Account Created", "Your FocusFlow account was created.")
        self.login_success.emit(user.username)

    def clear_password(self) -> None:
        self.password_input.clear()
