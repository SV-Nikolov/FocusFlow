FocusFlow
Project Overview

FocusFlow is a Windows-based productivity application designed to help users organize tasks, track progress, manage time, and review productivity patterns. The application is being developed as part of the CMSC 495 Computer Science Capstone course.

The goal of FocusFlow is to provide users with a simple but effective tool for planning their schedule, tracking ongoing work, and using productivity statistics to improve time management.

Purpose

Many users manage school, work, appointments, personal responsibilities, and long-term goals at the same time. FocusFlow is intended to help users stay organized by combining task management, calendar planning, progress tracking, reminders, and productivity reporting into one desktop application.

The application will allow users to:

Create and organize tasks
Assign tasks to labels or categories
Track task progress
Pause and resume active tasks
Mark tasks as completed
Set reminders
View tasks through a calendar-based interface
Analyze productivity data by label, date range, or custom criteria
Planned Functionality
1. User Account System

FocusFlow will include a user login system so each user can access their own tasks, labels, reminders, and statistics.

Planned features:

User registration
User login
Secure password storage
User-specific task data
Basic account management
2. Calendar-Based Task Management

The calendar will serve as one of the main parts of the application. Users will be able to create and view tasks based on dates.

Planned features:

Calendar view
Daily, weekly, or monthly task organization
Task creation from selected dates
Due date assignment
Upcoming task display
3. Task Creation and Organization

Users will be able to create tasks and organize them based on labels, priority, and status.

Planned features:

Create tasks
Edit tasks
Delete tasks
Add task descriptions
Assign due dates
Set task priority
Assign labels or categories
View task status

Possible task statuses:

Not Started
In Progress
Paused
Completed
Overdue
4. Labels and Categories

Labels will help users group related tasks and review productivity by category.

Example labels:

School
Work
Fitness
Personal
Appointments
Custom user-created labels

Planned features:

Create labels
Edit labels
Delete labels
Assign labels to tasks
Filter tasks by label
Generate statistics by label
5. Progress Tracking

FocusFlow will allow users to track the progress of their tasks over time.

Planned features:

Start task
Pause task
Resume task
Mark task as complete
Track total time spent on a task
Track completion date
Store task progress history
6. Reminder System

The application will include reminders to help users stay on schedule.

Planned features:

Set reminders for tasks
Display upcoming reminders
Notify users of upcoming deadlines
Mark reminders as triggered or completed
7. Productivity Statistics

FocusFlow will provide statistical data to help users understand how they spend their time and where they can improve.

Planned statistics:

Tasks completed by date range
Tasks completed by label
Time spent per label
Number of active, paused, overdue, and completed tasks
Completion rate
Most active productivity periods
Custom date range reports
8. Optional AWS Integration

If time allows, the team may explore AWS integration as a stretch goal.

Possible AWS features:

Cloud database hosting
User authentication through AWS services
Cloud backup of task data
Remote access to user productivity data

AWS integration is optional and will only be considered after the core application is functional.

Proposed Technology Stack

The final technology stack may be adjusted based on team decisions.

Possible technologies:

Application Type: Windows desktop application
Programming Language: C# or Java
User Interface: WPF, WinForms, or JavaFX
Database: SQLite, MySQL, or SQL Server
Version Control: Git and GitHub
Project Management: GitHub Projects, Trello, or similar tools
Database Concept

The application will require a database to store users, tasks, labels, reminders, and progress history.

Possible database tables:

Users
Tasks
Labels
Reminders
TaskProgressLog
Project Scope
Core Features

The core version of FocusFlow will include:

User login
Task creation
Task editing and deletion
Label assignment
Calendar-based task view
Task status tracking
Pause and resume functionality
Basic reminders
Database storage
Basic productivity statistics
Stretch Features

If time allows, additional features may include:

Advanced statistics dashboard
Data export
Windows notifications
Custom reports
AWS integration
Cloud backup
Improved user interface design
Project Goals

The main goals of this project are to:

Build a functional Windows productivity application
Apply software engineering principles
Practice team-based development
Use a database to manage application data
Create a usable interface for task and calendar management
Demonstrate project planning, testing, and documentation
Produce a realistic capstone project that can also serve as a portfolio piece
Team Collaboration

This project will be developed collaboratively as part of the CMSC 495 Computer Science Capstone course.

Planned collaboration tools:

GitHub for source control
GitHub Projects or Trello for task tracking
Microsoft Teams, Discord, or Zoom for communication
Google Docs or Microsoft 365 for shared documentation
Current Status

The project now has a working baseline desktop application and a reorganized repository structure for implementation and course deliverables.

Working Baseline Application

The repository now includes a working desktop baseline application with:

- Account registration and login
- Task creation, editing, deletion, and status transitions
- Calendar tab showing tasks by selected date
- Reminder tab with create, update, acknowledge, and delete actions
- Dashboard metrics (total, active, completed, overdue)
- Professional tabbed desktop UI with organized forms and panels
- Label and completion-rate summary panel

How to Run

1. Install dependencies:

	python -m pip install -r requirements.txt

2. Run the app from the repository root:

	set PYTHONPATH=src
	python -m focusflow

Persistence

- By default, the app uses a local SQLite database file named focusflow.db in the repository root.
- You can override the database connection by setting FOCUSFLOW_DB_URL before launch.
- If a configured database is unavailable, the app falls back to in-memory mode.

Example MySQL connection environment variable:

FOCUSFLOW_DB_URL=mysql+mysqlconnector://focusflow:focusflowpass@127.0.0.1:3307/focusflow_test

Windows Packaging

To build a Windows executable:

1. Open PowerShell in the repository root.
2. Run:

	powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1

3. Find the packaged app at:

	dist/FocusFlow/

Notes:

- The packaging script installs dependencies, clears previous build artifacts, and runs PyInstaller in windowed mode.
- Use the optional AppName parameter to generate a different executable name.

Repository Organization

- `src/focusflow/`: application source code.
- `tests/`: unit and integration tests.
- `scripts/`: automation scripts (build, integration test helper, document generation).
- `Documentation/Project/`: project-level planning and design documents.
- `Documentation/Tasks/Task_1/Resources/`: Task 1 template, instructions, and grading rubric.
- `Documentation/Tasks/Task_1/Submissions/`: Task 1 draft and final submission artifacts.

Task 1 Final Report

The final Phase I submission document is generated as an actual DOCX file at:

`Documentation/Tasks/Task_1/Submissions/Phase_1_Source_Report_Final.docx`
