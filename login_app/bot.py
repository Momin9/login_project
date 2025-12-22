import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'  # Replace with your actual token
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start_command(message):
    """Show welcome message with Clam menu button"""

    # Create the persistent menu
    menu = ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=False
    )

    # Add Clam button to menu
    menu.add(KeyboardButton("🦪 Clam Button"))

    # Also show an inline button with direct link
    inline_markup = InlineKeyboardMarkup()
    inline_markup.add(
        InlineKeyboardButton(
            "🔗 Direct Link (Click Here)",
            url="https://bcgame-872e9009e2fa.herokuapp.com/"
        )
    )

    # Send welcome with inline button
    bot.send_message(
        message.chat.id,
        "✨ *Welcome to BC Game Bot!* ✨\n\n"
        "1. Use the **Clam Button** at the bottom 👇\n"
        "2. Or click the link below ⬇️",
        parse_mode='Markdown',
        reply_markup=inline_markup
    )

    # Send the persistent menu
    bot.send_message(
        message.chat.id,
        "👇 **Menu Options:**",
        parse_mode='Markdown',
        reply_markup=menu
    )


@bot.message_handler(func=lambda m: m.text == "🦪 Clam Button")
def clam_menu_handler(message):
    """When user clicks the Clam menu button"""

    # Send the redirect message
    bot.send_message(
        message.chat.id,
        "✅ *Redirecting to BC Game...*\n\n"
        "Link: https://bcgame-872e9009e2fa.herokuapp.com/\n\n"
        "Click the link above or wait for automatic redirect...",
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['link', 'clam'])
def direct_link_command(message):
    """/link or /clam command for direct URL"""

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


# Keep showing the menu button for any message
@bot.message_handler(func=lambda message: True)
def show_menu_always(message):
    if message.text not in ["🦪 Clam Button"]:
        menu = ReplyKeyboardMarkup(resize_keyboard=True)
        menu.add(KeyboardButton("🦪 Clam Button"))

        bot.send_message(
            message.chat.id,
            "Need the Clam link? Use the button below:",
            reply_markup=menu
        )


print("🤖 Bot is starting with Clam Button...")
bot.polling(none_stop=True)