#!/bin/bash
# Simple start script - database will be initialized on first request via /health endpoint
exec gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --timeout 120 --access-logfile - --error-logfile -
