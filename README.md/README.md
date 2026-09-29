# Student Attendance System

A Flask web application for managing students, courses, and daily attendance. It includes a browser interface, JSON endpoints, and a relational data model that prevents duplicate attendance marks for the same student, course, and date.

## Features

- Faculty sign-in, student and course lists, attendance marking, and student reports.
- Flask-SQLAlchemy persistence with SQLite for local use and PostgreSQL through `DATABASE_URL`.
- Health endpoint for deployment monitoring.

## Run locally

Requirements: Python 3.10+.

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). The app creates its SQLite database and demo records on startup.

## API

- `GET /health` — health check
- `POST /api/login` — demo faculty sign-in
- `POST /api/mark_attendance` — record attendance
- `GET /api/report/{enroll_no}` — view a student report
- `GET /api/list_students` and `GET /api/list_courses` — list records

## Security note

This is a learning project. Do not use built-in demo login values or the default secret key in a public deployment. Set a strong random `SECRET_KEY` and a production database URL in the hosting environment; the demo authentication is not production-grade.

## Stack

Python, Flask, Flask-SQLAlchemy, SQLite/PostgreSQL, HTML, CSS, and JavaScript.
