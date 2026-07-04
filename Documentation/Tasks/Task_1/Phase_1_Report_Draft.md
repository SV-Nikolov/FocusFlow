# FocusFlow Phase I Source Code Report

## Cover Page

**Project Title:** FocusFlow Productivity Application  
**Course:** CMSC 495 Section 6981  
**Submission:** Phase I Source Code Report  
**Team:** Group Around the World  
**Team Members:** Danil Podolskiy, Jean Richard Fenelon, Stefan Nikolov, Alphonso Williams  
**Date:** July 5, 2026

---

## 1. Introduction

FocusFlow is a Windows-focused productivity application intended to consolidate individual task planning, schedule visibility, reminders, progress tracking, and productivity reporting in one desktop experience. The central problem the team is addressing is fragmentation: most users currently rely on separate apps or tools for scheduling, task tracking, and reminders. This creates context switching and inconsistent tracking behavior. FocusFlow addresses this by creating one integrated workflow from account login to task completion analytics.

Phase I represents the first software implementation milestone. Its purpose is to establish a reliable technical baseline, prove that core workflows are feasible, and reduce risk ahead of richer interface and integration work. In this phase, the team implemented foundational backend services and tests for user authentication and task management workflows. The implementation also introduces a persistence strategy that supports immediate in-memory development and a migration path to MySQL-backed storage through SQLAlchemy adapters.

The goal of this report is to document what was built in Phase I, how the architecture was structured, how testing was performed, and how the team aligned implementation decisions with the project plan and design constraints. This document also identifies risks and immediate next steps for Phase II.

## 2. Phase I Scope and Objectives

Phase I focused on four outcomes required by the assignment and project plan:

1. Project setup and development environment baseline.
2. Implementation of core functionality required for end-to-end workflows.
3. Unit testing for correctness and robustness of core modules.
4. Documentation sufficient for maintainability, code review, and continuation.

The implementation intentionally prioritized internal quality attributes over interface polish:

- Clear service boundaries.
- Explicit validation and domain rules.
- Reusable data models.
- Deterministic unit tests.
- Storage abstraction to avoid hard-coding one persistence mechanism too early.

This scope matches the Project Plan and Project Design deliverables that emphasize authentication, task lifecycle management, reminders/statistics readiness, and secure handling of account data.

## 3. Project Setup and Environment

### 3.1 Repository and Structure

A Python package structure was created to support modular development:

- `src/focusflow/` for application modules.
- `tests/` for unit tests.
- `Documentation/Tasks/Task_1/` for assignment artifacts.

This structure allows IDE indexing, isolated testing, and straightforward expansion into GUI and database integration modules.

### 3.2 Tooling and Dependency Baseline

The following setup files were introduced:

- `pyproject.toml` for project metadata and pytest settings.
- `requirements.txt` for dependency pinning.
- `.gitignore` for cache and local environment exclusions.

Current baseline dependencies include:

- `pytest` for unit testing.
- `SQLAlchemy` for ORM and persistence abstraction.
- `mysql-connector-python` as the MySQL driver.

This setup is deliberately small to keep build reproducibility high while avoiding unnecessary dependencies during early-phase development.

### 3.3 Coding Standards and Conventions

Phase I source uses the following conventions:

- Domain-first module design (models and service APIs before GUI logic).
- Explicit custom exceptions for expected application errors.
- Type annotations throughout service interfaces.
- UTC-aware timestamps for portability and correctness.
- Small, testable methods with predictable input validation behavior.

These practices were chosen to support maintainability and reduce integration friction as additional team members contribute new modules.

## 4. Software Architecture and Design

### 4.1 Layered Approach

Phase I follows the three-layer architecture described in the design document:

1. Presentation layer (planned UI integration in later phases).
2. Business logic layer (implemented in this phase).
3. Data layer (implemented with in-memory adapters and MySQL-ready SQLAlchemy adapters).

The current implementation focuses on the second and third layers. This creates a stable service API that the future UI can call without embedding business rules into interface code.

### 4.2 Domain Model

The `models.py` module defines core entities and enums:

- `User` includes username, password hash, optional email, and creation metadata.
- `Task` includes title, due date, status, label, priority, tracking timestamps, and ownership.
- `TaskStatus` supports `Not Started`, `In Progress`, `Paused`, `Completed`, `Overdue`.
- `TaskPriority` supports `Low`, `Medium`, `High`.

These structures align with the planned schema and provide enough fields to support dashboard and statistics features in later phases.

### 4.3 Business Services

Two main services were implemented.

#### Authentication Service

`AuthService` handles:

- Registration with required username validation.
- Duplicate username prevention.
- Password hashing through `PasswordHasher`.
- Login/authentication by verifying hashed credentials.

`PasswordHasher` uses PBKDF2-SHA256 with random salt and configurable iteration count. Passwords are never stored in plain text, meeting project security requirements and aligning with OWASP guidance.

#### Task Management Service

`TaskManager` handles:

- Task creation, retrieval, update, and deletion.
- Ownership checks to enforce per-user data isolation.
- Status transition enforcement to prevent invalid workflows.
- Overdue status updates based on reference date.
- Filtering by status and label.

A transition matrix defines allowed state changes to keep behavior consistent across endpoints and future UI actions.

### 4.4 Repository Abstraction and MySQL Persistence

A repository abstraction was introduced to avoid direct coupling between business logic and storage implementation.

- `repositories.py` defines `UserRepository` and `TaskRepository` protocols.
- In-memory repository implementations are used by default for fast local development and tests.
- `mysql_persistence.py` implements SQLAlchemy-backed adapters:
  - `SqlAlchemyContext`
  - `SqlUserRepository`
  - `SqlTaskRepository`
  - ORM rows `UserRow` and `TaskRow`
  - `MySQLConfig` for connection URL generation

This design allows the services to keep stable APIs while persistence changes under the hood, reducing risk as the team transitions to full database-backed workflows.

## 5. Core Functionality Delivered in Phase I

The following foundational features are complete:

1. User registration with secure password hashing.
2. User login verification against stored hashes.
3. Task creation with required title and due-date validation.
4. Task update and deletion operations.
5. Status workflow: start, pause, resume, complete, overdue.
6. User ownership checks for task access control.
7. Label and status filtering for list queries.
8. Overdue identification for pending tasks past due date.
9. Storage adapters that support in-memory and MySQL paths.

This functionality constitutes a working service-layer baseline that can support UI forms, calendar integration, reminders, and reporting in later phases.

## 6. Testing Strategy and Results

### 6.1 Unit Test Scope

Phase I includes automated tests in two modules:

- `test_auth.py`
- `test_task_manager.py`

Test cases cover expected behavior and error scenarios.

Authentication tests include:

- Passwords are hashed on registration.
- Duplicate usernames are rejected.
- Short passwords are rejected.
- Login succeeds with correct credentials and fails otherwise.

Task service tests include:

- Task creation/listing behavior.
- Required field validation.
- Valid and invalid status transitions.
- Cross-user access prevention.
- Overdue status update behavior.

### 6.2 Test Execution and Outcome

The suite was executed with pytest and completed successfully:

- Total tests: 10
- Passed: 10
- Failed: 0

A warning cleanup step was also applied during development by replacing deprecated naive UTC calls with timezone-aware UTC timestamps.

### 6.3 Quality Implications

The tests do not yet cover full database integration or GUI-driven workflows, but they validate the most important behavioral contracts at the service layer. This improves confidence that future UI and persistence work can proceed without introducing regressions in core business rules.

## 7. Collaboration, Version Control, and Process

The team workflow aligns with the project plan’s Agile-light approach:

- Work is organized in iterative slices.
- Version control is managed through Git and GitHub.
- Incremental updates are committed and pushed frequently.
- Documentation artifacts are stored with source for traceability.

During this phase, source code, tests, and assignment documentation were committed and pushed to the remote repository. This enables peer review, reproducibility, and integration with subsequent deliverables.

Planned collaboration practices for upcoming iterations include:

- Pull request-based code review for feature branches.
- Shared naming conventions for models/services/repositories.
- Priority-based issue tracking in GitHub.
- Structured defect tracking for failed test scenarios.

## 8. Risks, Constraints, and Mitigation

### 8.1 Observed Risks in Phase I

1. Persistence complexity could slow feature development if introduced too early.
2. Schema drift risk between domain models and actual database tables.
3. Team integration risk if module boundaries are unclear.
4. Potential inconsistency in state transitions if rules become duplicated.

### 8.2 Mitigation Applied

- Repository abstraction keeps business rules separate from storage details.
- Explicit transition matrix prevents ad hoc status logic.
- Unit tests lock down expected behavior.
- Clear module boundaries reduce merge conflicts and ambiguity.

### 8.3 Remaining Constraints

- Full GUI integration is not yet implemented.
- Reminder scheduling and statistics aggregation are not yet database-backed.
- Integration tests against a live MySQL instance are pending.
- Deployment and packaging workflows for Windows are pending.

These constraints are expected at this milestone and are addressed in planned Phase II sequencing.

## 9. Alignment with Project Requirements

Phase I implementation maps directly to the project plan/design goals:

- **Security requirement:** password hashing implemented.
- **User separation requirement:** authorization checks enforce task ownership.
- **Task lifecycle requirement:** core task CRUD and status transitions implemented.
- **Maintainability requirement:** modular architecture and typed service APIs implemented.
- **Testing requirement:** unit tests with pass results delivered.
- **Technical direction requirement:** Python foundation with MySQL-ready persistence path delivered.

The current milestone therefore satisfies the assignment expectation to deliver code foundation, tested functionality, and supporting documentation.

## 10. Phase II Readiness and Next Steps

With the Phase I baseline complete, the immediate Phase II plan is:

1. Connect services to a real MySQL instance and finalize schema migrations.
2. Add integration tests for SQL repositories and transaction behavior.
3. Begin PySide6 interface for login, dashboard, and task management screens.
4. Implement reminder scheduling and acknowledgment flow.
5. Implement statistics aggregation queries by date range and label.
6. Expand test coverage for edge cases and regression prevention.

This sequence keeps risk controlled by preserving the tested core while incrementally adding database and UI complexity.

## 11. Conclusion

Phase I successfully establishes the technical foundation for FocusFlow. The codebase now includes modular service logic, secure authentication handling, task lifecycle management, unit tests, and a MySQL-ready persistence layer through SQLAlchemy adapters. This implementation reflects the design constraints and scope boundaries defined in the project documentation while remaining flexible for future expansion.

Most importantly, the project has moved from planning to executable software with measurable quality signals. The successful test run and clear module boundaries provide confidence that the team can now proceed to deeper database integration, UI implementation, and feature expansion in Phase II without sacrificing maintainability.

---

## References

GitHub Docs. (n.d.). *About Projects*. https://docs.github.com/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects

Group Around the World. (2026). *Project Plan Group Around the World: FocusFlow* [Course project plan]. University of Maryland Global Campus.

OWASP Foundation. (n.d.). *Password Storage Cheat Sheet*. https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

Oracle. (n.d.). *MySQL 8.4 Reference Manual*. https://dev.mysql.com/doc/refman/8.4/en/

Qt Company. (n.d.). *Model/View Programming: Qt for Python*. https://doc.qt.io/qtforpython-6/overviews/qtwidgets-model-view-programming.htm

SQLAlchemy. (n.d.). *SQLAlchemy Documentation*. https://docs.sqlalchemy.org
