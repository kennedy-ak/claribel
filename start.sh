#!/bin/bash
set -e

mkdir -p logs/pids

echo "=== Activating virtual environment ==="
source env/bin/activate

echo "=== Running database migrations ==="
python manage.py migrate --noinput

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput --quiet

echo "=== Registering cron jobs ==="
python manage.py crontab add

echo "=== Starting Daphne ASGI server (port 8004, WebSocket-enabled) ==="
nohup daphne \
    -b 0.0.0.0 \
    -p 8004 \
    --access-log logs/daphne-access.log \
    mentorship_platform.asgi:application \
    > logs/daphne.log 2>&1 &

DAPHNE_PID=$!
echo $DAPHNE_PID > logs/pids/daphne.pid
echo "Daphne PID: $DAPHNE_PID"

echo ""
echo "=== All services started ==="
echo "  Daphne (HTTP + WebSocket): http://0.0.0.0:8004"
echo "  Logs: ./logs/"
echo ""
echo "To stop all services: ./stop.sh"
echo "To check logs:        tail -f logs/daphne.log"
echo "To check access log:  tail -f logs/daphne-access.log"
