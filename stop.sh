#!/bin/bash

echo "=== Stopping MentorFlow services ==="

PID_FILE="logs/pids/daphne.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping Daphne (PID $PID)..."
        kill "$PID"
        rm -f "$PID_FILE"
        echo "Daphne stopped."
    else
        echo "Daphne PID $PID not running. Cleaning up."
        rm -f "$PID_FILE"
    fi
else
    echo "No Daphne PID file found. Trying pkill..."
    pkill -f "daphne mentorship_platform.asgi:application" && echo "Daphne stopped." || echo "Daphne was not running."
fi

echo ""
echo "=== Removing cron jobs ==="
source .venv/bin/activate
python manage.py crontab remove

echo ""
echo "=== All services stopped ==="
