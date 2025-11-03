#!/bin/bash
# Initialize the database by calling the setup functions inside Flask context
python -c "from app import app, db, populate_initial_data; with app.app_context(): db.create_all(); populate_initial_data()"
# Start the production web server
# Use PORT environment variable if set (for Render), otherwise default to 5000
gunicorn app:app --bind 0.0.0.0:${PORT:-5000}