"""MySQL-backed SQLAlchemy persistence adapters for FocusFlow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text, create_engine, inspect, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from .models import Reminder, Task, TaskPriority, TaskStatus, User
from .repositories import ReminderRepository, TaskRepository, UserRepository


class Base(DeclarativeBase):
    pass


class UserRow(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    security_question: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    security_answer_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

class TaskRow(Base):
    __tablename__ = "tasks"

    task_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    priority: Mapped[str] = mapped_column(String(10), nullable=False)
    label: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_minutes_spent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class ReminderRow(Base):
    __tablename__ = "reminders"

    reminder_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_acknowledged: Mapped[bool] = mapped_column(nullable=False, default=False)


@dataclass(slots=True)
class MySQLConfig:
    host: str = "localhost"
    port: int = 3306
    database: str = "focusflow"
    username: str = "root"
    password: str = ""

    def connection_url(self) -> str:
        return (
            f"mysql+mysqlconnector://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
        )


class SqlAlchemyContext:
    def __init__(self, connection_url: str) -> None:
        self.engine = create_engine(connection_url, future=True)
        self._session_factory = sessionmaker(bind=self.engine, future=True)

    def create_schema(self) -> None:
        Base.metadata.create_all(self.engine)
        self._upgrade_user_security_columns()

    def _upgrade_user_security_columns(self) -> None:
        """Add recovery columns to databases created before this feature existed."""
        inspector = inspect(self.engine)
        if "users" not in inspector.get_table_names():
            return

        column_names = {column["name"] for column in inspector.get_columns("users")}
        statements: list[str] = []
        if "security_question" not in column_names:
            statements.append(
                "ALTER TABLE users ADD COLUMN security_question VARCHAR(255) NOT NULL DEFAULT ''"
            )
        if "security_answer_hash" not in column_names:
            statements.append(
                "ALTER TABLE users ADD COLUMN security_answer_hash VARCHAR(255) NOT NULL DEFAULT ''"
            )

        if statements:
            with self.engine.begin() as connection:
                for statement in statements:
                    connection.execute(text(statement))

    def session(self) -> Session:
        return self._session_factory()


class SqlUserRepository(UserRepository):
    def __init__(self, context: SqlAlchemyContext) -> None:
        self._context = context

    def get_by_username(self, username: str) -> User | None:
        with self._context.session() as session:
            row = session.scalar(select(UserRow).where(UserRow.username == username))
            return _user_from_row(row) if row is not None else None

    def save(self, user: User) -> User:
        with self._context.session() as session:
            row = session.get(UserRow, user.user_id)
            if row is None:
                row = UserRow(user_id=user.user_id)
                session.add(row)
            row.username = user.username
            row.password_hash = user.password_hash
            row.email = user.email
            row.security_question = user.security_question
            row.security_answer_hash = user.security_answer_hash
            row.created_at = user.created_at
            session.commit()
            return _user_from_row(row)


class SqlTaskRepository(TaskRepository):
    def __init__(self, context: SqlAlchemyContext) -> None:
        self._context = context

    def get_by_id(self, task_id: str) -> Task | None:
        with self._context.session() as session:
            row = session.get(TaskRow, task_id)
            return _task_from_row(row) if row is not None else None

    def save(self, task: Task) -> Task:
        with self._context.session() as session:
            row = session.get(TaskRow, task.task_id)
            if row is None:
                row = TaskRow(task_id=task.task_id)
                session.add(row)
            row.user_id = task.user_id
            row.title = task.title
            row.due_date = task.due_date
            row.description = task.description
            row.priority = task.priority.value
            row.label = task.label
            row.status = task.status.value
            row.created_at = task.created_at
            row.started_at = task.started_at
            row.completed_at = task.completed_at
            row.total_minutes_spent = task.total_minutes_spent
            session.commit()
            return _task_from_row(row)

    def delete(self, task_id: str) -> None:
        with self._context.session() as session:
            row = session.get(TaskRow, task_id)
            if row is not None:
                session.delete(row)
                session.commit()

    def list_all(self) -> list[Task]:
        with self._context.session() as session:
            rows = session.scalars(select(TaskRow)).all()
            return [_task_from_row(row) for row in rows]


class SqlReminderRepository(ReminderRepository):
    def __init__(self, context: SqlAlchemyContext) -> None:
        self._context = context

    def get_by_id(self, reminder_id: str) -> Reminder | None:
        with self._context.session() as session:
            row = session.get(ReminderRow, reminder_id)
            return _reminder_from_row(row) if row is not None else None

    def save(self, reminder: Reminder) -> Reminder:
        with self._context.session() as session:
            row = session.get(ReminderRow, reminder.reminder_id)
            if row is None:
                row = ReminderRow(reminder_id=reminder.reminder_id)
                session.add(row)
            row.task_id = reminder.task_id
            row.remind_at = reminder.remind_at
            row.message = reminder.message
            row.is_acknowledged = reminder.is_acknowledged
            session.commit()
            return _reminder_from_row(row)

    def delete(self, reminder_id: str) -> None:
        with self._context.session() as session:
            row = session.get(ReminderRow, reminder_id)
            if row is not None:
                session.delete(row)
                session.commit()

    def list_all(self) -> list[Reminder]:
        with self._context.session() as session:
            rows = session.scalars(select(ReminderRow)).all()
            return [_reminder_from_row(row) for row in rows]


def _user_from_row(row: UserRow) -> User:
    return User(
        user_id=row.user_id,
        username=row.username,
        password_hash=row.password_hash,
        security_question=row.security_question,
        security_answer_hash=row.security_answer_hash,
        email=row.email,
        created_at=row.created_at,
    )


def _task_from_row(row: TaskRow) -> Task:
    return Task(
        task_id=row.task_id,
        user_id=row.user_id,
        title=row.title,
        due_date=row.due_date,
        description=row.description,
        priority=TaskPriority(row.priority),
        label=row.label,
        status=TaskStatus(row.status),
        created_at=row.created_at,
        started_at=row.started_at,
        completed_at=row.completed_at,
        total_minutes_spent=row.total_minutes_spent,
    )


def _reminder_from_row(row: ReminderRow) -> Reminder:
    return Reminder(
        reminder_id=row.reminder_id,
        task_id=row.task_id,
        remind_at=row.remind_at,
        message=row.message,
        is_acknowledged=row.is_acknowledged,
    )
