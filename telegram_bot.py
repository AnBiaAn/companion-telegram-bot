import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

MORNING_MESSAGES = [
    "Good morning. You've got this today. 💛",
    "Rise and shine, beautiful soul. 🌅",
    "New day, new light. 🌅",
    "You're stronger than you think. 💪",
    "Good morning, love. You'll do great. 🌻",
]

NIGHT_MESSAGES = [
    "Sleep well, sweet soul. 🌙",
    "You did enough today. Rest now. 💤",
    "Tomorrow is a gift waiting. 🌙",
    "Rest restores you. 🌌",
    "Sleep deeply and well. 🤍",
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("📱 Test Message", callback_data='test')],
    ]
    await update.message.reply_text(
        "🌙 Welcome to Lovinow Bot!\n\nClick Test to see messages.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def test_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    morning = random.choice(MORNING_MESSAGES)
    night = random.choice(NIGHT_MESSAGES)
    
    text = f"🌅 Morning:\n{morning}\n\n🌙 Night:\n{night}"
    await query.edit_message_text(text)

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set")
    
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(test_message))
    
    app.run_polling()

if __name__ == '__main__':
    main()
