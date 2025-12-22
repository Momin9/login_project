# login_app/management/commands/run_bot.py
from django.core.management.base import BaseCommand
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from django.conf import settings


class Command(BaseCommand):
    help = 'Run Telegram bot - Only shows Clam button'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🤖 Starting Clam Button Bot...'))

        BOT_TOKEN = getattr(settings, 'TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

        if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
            self.stdout.write(self.style.ERROR('❌ Please set TELEGRAM_BOT_TOKEN in settings.py'))
            return

        bot = telebot.TeleBot(BOT_TOKEN)

        @bot.message_handler(commands=['start'])
        def show_clam_button_only(message):
            """Show ONLY the Clam button - nothing else"""
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton(
                    "🦪 Clam",
                    url="https://bcgame-872e9009e2fa.herokuapp.com/"
                )
            )
            bot.send_message(message.chat.id, "", reply_markup=markup)

        @bot.message_handler(func=lambda message: True)
        def show_button_for_any_message(message):
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton(
                    "🦪 Clam",
                    url="https://bcgame-872e9009e2fa.herokuapp.com/"
                )
            )
            bot.send_message(message.chat.id, "", reply_markup=markup)

        self.stdout.write(self.style.SUCCESS('✅ Bot running...'))
        bot.polling(none_stop=True)