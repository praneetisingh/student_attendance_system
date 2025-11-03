@echo off
REM Windows batch script for starting the application
echo Initializing database...
python -c "from app import app, db, populate_initial_data; with app.app_context(): db.create_all(); populate_initial_data()"
echo Starting server...
gunicorn app:app --bind 0.0.0.0:5000

