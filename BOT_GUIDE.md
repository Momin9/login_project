# Telegram Bot Integration

## Bot Features
- Responds to `/start` and `/clam` commands with Clam button
- Shows Clam button in every message reply
- Button links to: https://bcgame.bond

## Running the Bot

### Development (Local):
```bash
# Terminal 1 - Django server
python manage.py runserver

# Terminal 2 - Telegram bot
python manage.py run_bot
```

### Production (Heroku):

Add to your Procfile:
```
web: gunicorn login_project.wsgi --log-file -
bot: python manage.py run_bot
```

Then scale the bot dyno:
```bash
heroku ps:scale bot=1
```

## Environment Variables
Make sure these are set:
- `TELEGRAM_BOT_TOKEN` - Your bot token from @BotFather
- `TELEGRAM_CHAT_ID` - Your chat ID

## Bot Commands
- `/start` - Welcome message with Clam button
- `/clam` - Show Clam button
- Any text - Echo with Clam button