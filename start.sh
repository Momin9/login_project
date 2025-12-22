#!/bin/bash

echo "🚀 Starting Django Project with Telegram Bot..."

# Start Django server in background
echo "📡 Starting Django server..."
python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# Wait a moment for Django to start
sleep 3

# Start Telegram bot
echo "🤖 Starting Telegram bot..."
python manage.py run_bot &
BOT_PID=$!

echo "✅ Both services started!"
echo "📡 Django: http://localhost:8000"
echo "🤖 Bot: Running with PID $BOT_PID"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for user to stop
trap 'echo "🛑 Stopping services..."; kill $DJANGO_PID $BOT_PID; exit' INT
wait