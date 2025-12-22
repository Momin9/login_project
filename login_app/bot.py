import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from django.conf import settings
import threading

def create_bot():
    bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)
    
    @bot.message_handler(commands=['start', 'clam'])
    def send_clam_button(message):
        markup = InlineKeyboardMarkup()
        clam_button = InlineKeyboardButton("🦪 Click Clam", url="https://bcgame.bond")
        markup.add(clam_button)
        
        bot.reply_to(message, "Welcome! Click the Clam button below:", reply_markup=markup)
    
    @bot.message_handler(func=lambda message: True)
    def echo_with_button(message):
        markup = InlineKeyboardMarkup()
        clam_button = InlineKeyboardButton("🦪 Get Clam", url="https://bcgame.bond")
        markup.add(clam_button)
        
        bot.reply_to(message, f"You said: {message.text}\n\nClick below for Clam:", reply_markup=markup)
    
    return bot

def start_bot():
    bot = create_bot()
    print("🤖 Telegram Bot Starting...")
    bot.polling()

def run_bot_thread():
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()