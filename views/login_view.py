"""Login and registration screen for FocusFlow."""

from tkinter import dialog

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
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

        self.security_question_input = QComboBox()
        self.security_question_input.addItems(
            [
                "What is your favorite color?",
                "What is your mother's maiden name?",
                "What was the name of your first pet?",
                "What city were you born in?",
            ]
        )
        self.security_answer_input = QLineEdit()
        self.security_answer_input.setPlaceholderText(
            "Security answer for registration"
        )
        self.security_answer_input.setEchoMode(QLineEdit.Password)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)

        register_button = QPushButton("Register")
        register_button.setObjectName("SecondaryButton")
        register_button.clicked.connect(self.register)
        forgot_password_button = QPushButton("Forgot Password?")
        forgot_password_button.setObjectName("SecondaryButton")
        forgot_password_button.clicked.connect(
        self.open_password_recovery_dialog
        )

        form = QGridLayout()
        form.addWidget(QLabel("Username"), 0, 0)
        form.addWidget(self.username_input, 0, 1)
        form.addWidget(QLabel("Email"), 1, 0)
        form.addWidget(self.email_input, 1, 1)
        form.addWidget(QLabel("Password"), 2, 0)
        form.addWidget(self.password_input, 2, 1)
        form.addWidget(QLabel("Security Question"), 3, 0)
        form.addWidget(self.security_question_input, 3, 1)
        form.addWidget(QLabel("Security Answer"), 4, 0)
        form.addWidget(self.security_answer_input, 4, 1)

        buttons = QHBoxLayout()
        buttons.addWidget(login_button)
        buttons.addWidget(register_button)
        buttons.addWidget(forgot_password_button)

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
                username=self.username_input.text(),
                password=self.password_input.text(),
                email=self.email_input.text(),
                security_question=self.security_question_input.currentText(),
                security_answer=self.security_answer_input.text(),
            )
            self.store.current_user = user.username
        except ValueError as error:
            QMessageBox.warning(self, "Registration Failed", str(error))
            return

        QMessageBox.information(self, "Account Created", "Your FocusFlow account was created.")
        self.login_success.emit(user.username)

    def open_password_recovery_dialog(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Recover FocusFlow Account")
        dialog.setMinimumWidth(440)

        username_input = QLineEdit()
        username_input.setPlaceholderText("Enter your username")

        question_label = QLabel(
            "Enter your username and select Find Question."
        )
        question_label.setWordWrap(True)

        answer_input = QLineEdit()
        answer_input.setPlaceholderText("Security answer")
        answer_input.setEchoMode(QLineEdit.Password)

        new_password_input = QLineEdit()
        new_password_input.setPlaceholderText("New password")
        new_password_input.setEchoMode(QLineEdit.Password)

        confirm_password_input = QLineEdit()
        confirm_password_input.setPlaceholderText(
            "Confirm new password"
        )
        confirm_password_input.setEchoMode(QLineEdit.Password)

        form = QFormLayout()
        form.addRow("Username", username_input)
        form.addRow("Security Question", question_label)
        form.addRow("Security Answer", answer_input)
        form.addRow("New Password", new_password_input)
        form.addRow("Confirm Password", confirm_password_input)

        find_question_button = QPushButton("Find Question")
        reset_button = QPushButton("Reset Password")
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("SecondaryButton")

        def find_question() -> None:
            username = username_input.text().strip()

            if not username:
                QMessageBox.warning(
                    dialog,
                    "Recovery Error",
                    "Enter your username.",
                )
                return

            try:
                question = self.store.get_security_question(
                    username
                )
            except ValueError as error:
                QMessageBox.warning(
                    dialog,
                    "Recovery Error",
                    str(error),
                )
                return

            question_label.setText(question)

        def reset_password() -> None:
            username = username_input.text().strip()
            answer = answer_input.text()
            new_password = new_password_input.text()
            confirmation = confirm_password_input.text()

            if new_password != confirmation:
                QMessageBox.warning(
                    dialog,
                    "Recovery Error",
                    "The new passwords do not match.",
                )
                return

            try:
                self.store.reset_password(
                    username=username,
                    security_answer=answer,
                    new_password=new_password
                )
            except ValueError as error:
                QMessageBox.warning(
                    dialog,
                "Recovery Error",
                str(error),
            )
            return

            QMessageBox.information(
                dialog,
                    "Password Reset",
                "Your password was reset successfully.",
            )

            self.username_input.setText(username)
            self.password_input.clear()
            dialog.accept()

        find_question_button.clicked.connect(find_question)
        reset_button.clicked.connect(reset_password)
        cancel_button.clicked.connect(dialog.reject)

        buttons = QHBoxLayout()
        buttons.addWidget(find_question_button)
        buttons.addWidget(reset_button)
        buttons.addWidget(cancel_button)

        layout = QVBoxLayout(dialog)
        layout.addLayout(form)
        layout.addLayout(buttons)

        dialog.exec()

    def clear_password(self) -> None:
        self.password_input.clear()
        self.security_answer_input.clear()
