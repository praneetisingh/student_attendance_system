#!/bin/bash
# Simple start script - initialize database and update student names
python -c "
from app import app, db, populate_initial_data
with app.app_context():
    db.create_all()
    populate_initial_data()
    print('Database initialized and student names updated.')
"
exec gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --timeout 120 --access-logfile - --error-logfile -
