from django.core.management.base import BaseCommand
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from django.conf import settings


class Command(BaseCommand):
    help = 'Run the Telegram bot with Clam button'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🤖 Starting Telegram Bot with Clam Button...'))

        # Get bot token from Django settings
        # Make sure to add TELEGRAM_BOT_TOKEN to your settings.py
        BOT_TOKEN = getattr(settings, 'TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

        if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
            self.stdout.write(self.style.ERROR('❌ Please set TELEGRAM_BOT_TOKEN in settings.py'))
            return

        bot = telebot.TeleBot(BOT_TOKEN)

        @bot.message_handler(commands=['start'])
        def start_command(message):
            """Show welcome message with Clam menu button"""

            # Create the persistent menu (appears at bottom of chat)
            menu = ReplyKeyboardMarkup(
                resize_keyboard=True,
                one_time_keyboard=False
            )

            # Add Clam button to menu - this is what users see at bottom
            menu.add(KeyboardButton("🦪 Clam"))

            # Also show an inline button with direct link
            inline_markup = InlineKeyboardMarkup()
            inline_markup.add(
                InlineKeyboardButton(
                    "🔗 Open BC Game",
                    url="https://bcgame-872e9009e2fa.herokuapp.com/"
                )
            )

            # Send welcome with inline button
            bot.send_message(
                message.chat.id,
                "✨ *Welcome to BC Game Bot!* ✨\n\n"
                "1. Use the **🦪 Clam button** at the bottom 👇\n"
                "2. Or click the link below ⬇️\n"
                "3. Type /link for direct URL",
                parse_mode='Markdown',
                reply_markup=inline_markup
            )

            # Send the persistent menu (Clam button at bottom)
            bot.send_message(
                message.chat.id,
                "👇 **Click the Clam button below:**",
                parse_mode='Markdown',
                reply_markup=menu
            )

        @bot.message_handler(func=lambda m: m.text == "🦪 Clam")
        def clam_menu_handler(message):
            """When user clicks the Clam menu button"""

            # Create inline button with direct URL
            inline_markup = InlineKeyboardMarkup()
            inline_markup.add(
                InlineKeyboardButton(
                    "🦪 Click to Visit BC Game",
                    url="https://bcgame-872e9009e2fa.herokuapp.com/"
                )
            )

            bot.send_message(
                message.chat.id,
                "✅ *Redirecting to BC Game...*\n\n"
                "Click the button below to visit:",
                parse_mode='Markdown',
                reply_markup=inline_markup
            )

        @bot.message_handler(commands=['link', 'clamlink'])
        def direct_link_command(message):
            """/link or /clamlink command for direct URL"""

            inline_markup = InlineKeyboardMarkup()
            inline_markup.add(
                InlineKeyboardButton(
                    "🦪 Visit BC Game Now",
                    url="https://bcgame-872e9009e2fa.herokuapp.com/"
                )
            )

            bot.send_message(
                message.chat.id,
                "🌐 *Direct BC Game Link*\n\n"
                "Click the button below:",
                parse_mode='Markdown',
                reply_markup=inline_markup
            )

        # For any other message, remind about Clam button
        @bot.message_handler(func=lambda message: True)
        def show_menu_always(message):
            # Only respond if not a command and not the Clam button
            if not message.text.startswith('/') and message.text != "🦪 Clam":
                menu = ReplyKeyboardMarkup(resize_keyboard=True)
                menu.add(KeyboardButton("🦪 Clam"))

                bot.send_message(
                    message.chat.id,
                    f"You said: '{message.text}'\n\nNeed the Clam link? Use the button below:",
                    reply_markup=menu
                )

        self.stdout.write(self.style.SUCCESS(f'✅ Bot started successfully! Token: {BOT_TOKEN[:10]}...'))
        self.stdout.write(self.style.WARNING('🔄 Bot is now polling for messages...'))
        self.stdout.write(self.style.WARNING('⚠️  Press Ctrl+C to stop the bot'))

        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\n🛑 Bot stopped by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Bot error: {e}'))