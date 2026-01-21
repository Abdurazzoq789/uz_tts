#!/bin/bash
# Start Uzbek TTS Bot and Celery Worker

# Activate venv if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BOT_PID $CELERY_PID 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

echo "Starting Uzbek TTS Bot..."
echo "=========================="
echo ""

# Start bot in background
echo "[1/2] Starting bot..."
python main.py &
BOT_PID=$!

sleep 2

# Start Celery worker in background
echo "[2/2] Starting Celery worker..."
celery -A tasks worker --loglevel=info -Q tts --pool=solo &
CELERY_PID=$!

echo ""
echo "✓ Services started!"
echo "Bot PID: $BOT_PID"
echo "Celery PID: $CELERY_PID"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes
wait
