#!/bin/bash
# Simple start script - no database initialization
# Database will be created on first request
exec gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --timeout 120 --access-logfile - --error-logfile -

