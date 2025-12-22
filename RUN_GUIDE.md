# Auto-Start Guide

## Local Development (One Command):

### Option 1: Bash Script
```bash
./start.sh
```

### Option 2: Python Script
```bash
python start.py
```

### Option 3: Manual (if scripts don't work)
```bash
# Terminal 1
python manage.py runserver

# Terminal 2  
python manage.py run_bot
```

## Heroku Deployment:
```bash
# Deploy
git push heroku main

# Scale services
heroku ps:scale web=1 bot=1
```

## What Happens:
- Django server starts on port 8000
- Telegram bot starts automatically
- Both run together
- Press Ctrl+C to stop both

## Bot Link:
https://t.me/bc_game_bilal_bot

Bot shows "🦪 Clam" button that opens:
https://bcgame-872e9009e2fa.herokuapp.com/