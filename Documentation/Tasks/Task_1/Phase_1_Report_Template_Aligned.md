# CMSC 495 Phase I Source Code

## Cover Page

Project Title: FocusFlow Productivity Application  
Course: CMSC 495 Section 6981  
Team: Group Around the World  
Team Members: Danil Podolskiy, Jean Richard Fenelon, Stefan Nikolov, Alphonso Williams  
Submission Date: July 5, 2026

## Introduction

This Phase I submission documents the first implementation milestone for FocusFlow, a Windows-focused productivity application intended to combine task management, calendar planning, reminders, and productivity tracking into one system. The Phase I objective is to establish a technically sound baseline with clear architecture, executable core services, and unit test coverage that can support later interface and database expansion.

During this phase, the team moved from planning artifacts to executable source code. The initial implementation includes authentication and task service modules, explicit domain models, validation/exception handling, repository abstractions, and a MySQL-ready persistence path. The work also includes automated tests and implementation notes required for maintainability and peer review.

## Objective

The objective of this Phase I implementation is to satisfy the source-code milestone by delivering:

1. A structured project setup for Python development and testing.
2. Initial core functionality that reflects planned product workflows.
3. Unit tests that validate behavior and error handling.
4. Technical documentation that supports collaboration and future phases.

The milestone demonstrates software design, object-oriented design, algorithmic workflow control, and test-driven quality checks while preserving a scope that is realistic for capstone scheduling.

## Instructions

### Review the Phase I

The Phase I requirements were interpreted from the project plan, project design document, and assignment guidance. Priority was given to foundational modules that are required by almost all future features: user authentication, task lifecycle rules, and data persistence boundaries.

### Design the Software Architecture

The implementation follows a layered design:

1. Business logic services for authentication and task operations.
2. Domain models and enums for status/priority consistency.
3. Repository interfaces and adapters to separate storage from service logic.

This architecture allows in-memory repositories for rapid testing and SQLAlchemy/MySQL repositories for persistent operation without rewriting service logic.

### Implement the Software

Implemented modules include:

- `src/focusflow/models.py` for entities and enums.
- `src/focusflow/exceptions.py` for typed application errors.
- `src/focusflow/auth.py` for secure registration and login checks.
- `src/focusflow/task_manager.py` for task CRUD and status transitions.
- `src/focusflow/repositories.py` for repository protocols and in-memory adapters.
- `src/focusflow/mysql_persistence.py` for SQLAlchemy/MySQL adapters.

Password security uses PBKDF2-SHA256 with random salt and iterative hashing. Task workflow transitions are validated through an allowed-transition matrix to prevent invalid state changes.

### Test the Software

Automated testing was implemented with pytest.

Current suites:

- `tests/test_auth.py`
- `tests/test_task_manager.py`
- `tests/integration/test_mysql_repositories.py`

The first two suites run by default and verify baseline behavior and edge cases. The MySQL integration suite is environment-gated and runs when `MYSQL_TEST_URL` is provided.

Default test result in local environment:

- 10 passed (unit suite)

Integration tests can be executed after starting the MySQL test profile described in the Task 1 documentation.

## Example Code

```python
from datetime import date

from focusflow.auth import AuthService
from focusflow.task_manager import TaskManager
from focusflow.models import TaskStatus


auth = AuthService()
user = auth.register_user("alice", "StrongPass123")

manager = TaskManager()
task = manager.create_task(
    user_id=user.user_id,
    title="Prepare phase report",
    due_date=date.today(),
)
manager.transition_status(task_id=task.task_id, user_id=user.user_id, new_status=TaskStatus.IN_PROGRESS)
manager.transition_status(task_id=task.task_id, user_id=user.user_id, new_status=TaskStatus.COMPLETED)
```

The snippet shows an end-to-end Phase I flow: account registration, task creation, and task completion using the service layer APIs.

## Conclusion

Phase I successfully established a maintainable backend foundation for FocusFlow. The codebase now supports secure account registration/login, task lifecycle management, explicit validation behavior, and repository-driven persistence boundaries. Unit tests confirm core behavior, and MySQL integration scaffolding is in place for persistent testing and expansion.

This baseline reduces technical risk for Phase II by keeping service contracts stable while allowing storage and interface layers to evolve independently.

## References

GitHub Docs. (n.d.). About Projects. https://docs.github.com/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects

OWASP Foundation. (n.d.). Password Storage Cheat Sheet. https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

Oracle. (n.d.). MySQL 8.4 Reference Manual. https://dev.mysql.com/doc/refman/8.4/en/

SQLAlchemy. (n.d.). SQLAlchemy Documentation. https://docs.sqlalchemy.org
