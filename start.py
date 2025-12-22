#!/usr/bin/env python3
import subprocess
import sys
import time
import signal
import os

def start_services():
    print("🚀 Starting Django Project with Telegram Bot...")
    
    # Start Django server
    print("📡 Starting Django server...")
    django_process = subprocess.Popen([
        sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'
    ])
    
    # Wait for Django to start
    time.sleep(3)
    
    # Start Telegram bot
    print("🤖 Starting Telegram bot...")
    bot_process = subprocess.Popen([
        sys.executable, 'manage.py', 'run_bot'
    ])
    
    print("✅ Both services started!")
    print("📡 Django: http://localhost:8000")
    print("🤖 Bot: Running")
    print("\nPress Ctrl+C to stop both services")
    
    def signal_handler(sig, frame):
        print("\n🛑 Stopping services...")
        django_process.terminate()
        bot_process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        django_process.wait()
        bot_process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    start_services()