#!/bin/bash
set -e  # Exit on error

# Initialize the database by calling the setup functions inside Flask context
echo "Initializing database..."
python -c "
from app import app, db, populate_initial_data
try:
    with app.app_context():
        db.create_all()
        populate_initial_data()
    print('Database initialized successfully')
except Exception as e:
    print(f'Database initialization error: {e}')
    import sys
    sys.exit(1)
"

# Start the production web server
echo "Starting Gunicorn..."
# Use PORT environment variable if set (for Render), otherwise default to 5000
exec gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --timeout 120