# Heroku Deployment Guide

## Prerequisites
1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Create a [Heroku account](https://signup.heroku.com/)

## Deployment Steps

### 1. Login to Heroku
```bash
heroku login
```

### 2. Create Heroku App
```bash
heroku create your-app-name
# Or let Heroku generate a name:
heroku create
```

### 3. Set Environment Variables
```bash
heroku config:set SECRET_KEY="your-secret-key-here"
heroku config:set DEBUG=False
heroku config:set TELEGRAM_BOT_TOKEN="8576917162:AAHTHUBy3yuIdIcEOiXlM72nccjYAvZIwBs"
heroku config:set TELEGRAM_CHAT_ID="6631764790"
```

### 4. Deploy to Heroku
```bash
git add .
git commit -m "Prepare for Heroku deployment"
git push heroku main
```

### 5. Open Your App
```bash
heroku open
```

## Environment Variables Required
- `SECRET_KEY`: Django secret key (auto-generated)
- `DEBUG`: Set to `False` for production
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_CHAT_ID`: Your Telegram chat ID

## Optional Environment Variables
- `EMAIL_HOST_USER`: Gmail address for email functionality
- `EMAIL_HOST_PASSWORD`: Gmail app password
- `ADMIN_EMAIL`: Admin email address

## Troubleshooting

### View Logs
```bash
heroku logs --tail
```

### Run Commands
```bash
heroku run python manage.py shell
heroku run python manage.py collectstatic
```

### Scale Dynos
```bash
heroku ps:scale web=1
```

## Files Added for Heroku
- `Procfile`: Tells Heroku how to run the app
- `runtime.txt`: Specifies Python version
- `requirements.txt`: Updated with gunicorn, whitenoise, dj-database-url
- `app.json`: App configuration for Heroku
- `release-tasks.sh`: Release phase tasks (migrations, static files)

## Database
The app uses SQLite by default but will automatically use PostgreSQL on Heroku if DATABASE_URL is provided.