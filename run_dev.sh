#!/bin/bash
# Simple development mode runner
# This doesn't require gunicorn

echo "Activating virtual environment..."
source venv/Scripts/activate

echo "Running Flask in development mode..."
python app.py

