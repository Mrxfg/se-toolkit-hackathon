#!/bin/bash
set -e

echo "Waiting for database to be ready..."
sleep 5

echo "Running migrations..."
python migrate.py

echo "Starting backend server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
