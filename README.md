# Online Student Management System

![CI Status](https://github.com/YOUR_USERNAME/student-management-system/actions/workflows/ci.yml/badge.svg)

## Overview

The Online Student Management System is a web application
that allows authorized users to manage student records.

## Features

- Admin and staff login
- Add student records
- View student records
- Update student details
- Delete student records
- SQLite database
- REST API endpoints
- Automated testing using pytest
- Code quality checks using Ruff
- Test coverage reporting

## Technology Stack

- Python
- Flask
- SQLite
- pytest
- pytest-cov
- Ruff
- GitHub Actions

## Installation

Clone the repository:

    git clone https://github.com/Dhrithi123-collab/student_management.git

Navigate to the project:

    cd student_management

Create a virtual environment:

    python -m venv venv

Activate it on Windows:

    venv\Scripts\activate

Install dependencies:

    pip install -r requirements.txt

## Run the Application

    python app.py

Open http://127.0.0.1:5000 in your browser.

## Run Tests

    pytest

## Run Tests with Coverage

    pytest --cov=app --cov-report=term-missing

## Run Code Quality Checks

    ruff check .

## Continuous Integration

GitHub Actions automatically runs the CI workflow on every
push and pull request.

The workflow installs dependencies, checks code quality,
runs automated tests, enforces the minimum coverage threshold,
and uploads the coverage report.

A green check indicates that the workflow passed.
A red cross indicates that one or more checks failed.