# Online Student Management System

![CI Status](https://github.com/Dhrithi123-collab/student_management_system/actions/workflows/ci.yml/badge.svg)

A Flask and SQLite web application for viewing and managing student records, with admin/staff roles and automated CI checks.

## Features

- Login for admin and staff users
- Add, list, and edit student records
- Delete student records (admin only)
- Search student records by name, email, or course
- Responsive login and dashboard pages
- JSON API backed by SQLite
- Automated tests with pytest and coverage
- Ruff lint checks and GitHub Actions CI

## Requirements

- Python 3.11 or later
- pip

## Setup on Windows PowerShell

```powershell
git clone https://github.com/Dhrithi123-collab/student_management_system.git
cd student_management_system
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Demo accounts

For local coursework/testing only:

- Admin: `admin` / `Admin123!`
- Staff: `staff` / `Staff123!`

The demo users are created automatically when the database is initialized. Do not use these demo credentials or the development secret in a public production deployment. Set a strong `SECRET_KEY` environment variable and configure real accounts before deployment.

## Tests and quality checks

```powershell
python -m pytest -v
python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=70
ruff check .
```

## Continuous Integration

GitHub Actions runs on every push and pull request. It installs dependencies, runs Ruff, executes pytest with coverage enforcement, and uploads `coverage.xml` as a workflow artifact.
