"""
Simple Companion Bot for Telegram
Sends daily warm messages - morning and night
"""

import os
import json
import random
from datetime import time
from zoneinfo import ZoneInfo

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Message libraries
MESSAGES = {
    'morning': [
        "Good morning. You've got this today. 💛",
        "Rise and shine, beautiful soul. Today is yours. ☀️",
        "New day, new light. You're stronger than you think. 🌅",
        "Morning light. Your chance to create something good. 💫",
        "Wake up knowing you're capable of amazing things. 💪",
        "Good morning, love. You're going to do great. 🌻",
        "Another sunrise. Another chance. You're ready. 🌄",
        "Today is a blank page. Write something beautiful. ✨",
        "You're alive. You're here. That's enough to begin. 💚",
        "Morning brings possibility. Step into it. 🌸",
        "Fresh start. Fresh energy. Fresh hope. Let's go. 🔥",
        "Your presence matters today. Remember that. 💫",
        "Breathe in the morning. You've got what it takes. 🌬️",
        "New day, new chances. Be gentle with yourself. 🤍",
        "Light is returning. So are you. 🌟",
        "Good morning, brave heart. Let's do this. 💪",
        "Today is your canvas. Paint it with love. 🎨",
        "You woke up. You're showing up. That's the win. ✅",
        "Morning whispers: you are enough. 🌿",
        "Another day to be kind to yourself. Start now. 💛",
    ],
    'night': [
        "Sleep well, sweet soul. Tomorrow is a gift waiting for you. 🌙",
        "Close your eyes knowing you gave today your best. Dream peacefully. 💤",
        "Night time. Let your worries fade. Rest restores you. 🌌",
        "Tomorrow brings new light. Sleep now, heal now. 💫",
        "You're safe. You're loved. Sleep deeply and well. 🤍",
        "Night whispers: you're enough. Sleep, beautiful soul. 🌙",
        "You made it through another day. Rest now. 🌙",
        "Your body needs this. Your mind needs this. Sleep well. 💤",
        "Close your eyes. You did enough today. 🌜",
        "Dreams are calling. Answer them. Sleep tight. ✨",
        "Night is for rest, for healing, for peace. Embrace it. 🕯️",
        "Tomorrow waits. Tonight, just rest. 🌙",
        "You earned this sleep. Settle in. Breathe. 🌊",
        "Darkness brings peace. Let it in. 💫",
        "Another day behind you. You survived. You thrived. Sleep now. 🌟",
        "Night blankets you in safety. Sleep well, love. 🤍",
        "Rest is not laziness. Rest is love. Sleep peacefully. 💚",
        "Stars are watching over you. Dream well. ⭐",
        "This day is done. You're done. Rest. 🌙",
        "Sleep is your superpower. Use it. 💤",
    ]
}

# User settings (in memory - resets on restart)
user_settings = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message."""
    user_id = update.effective_user.id
    
    if user_id not in user_settings:
        user_settings[user_id] = {
            'name': 'Haven',
            'morning_time': '07:00',
            'night_time': '21:00',
            'enabled': True
        }
    
    keyboard = [
        [InlineKeyboardButton("⚙️ Settings", callback_data='settings')],
        [InlineKeyboardButton("📱 Test Message", callback_data='test')],
        [InlineKeyboardButton("❌ Stop Messages", callback_data='stop')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """🌙 Welcome to Lovinow Bot!

Every day you get two warm messages:
🌅 Morning - Encouragement to start your day
🌙 Night - Wisdom to help you rest

Each message is different every day. No repeats. Just genuine love and support.

Customize your times in Settings. 💛"""
    
    await update.message.reply_text(text, reply_markup=reply_markup)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button clicks."""
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    if query.data == 'settings':
        settings = user_settings.get(user_id, {})
        keyboard = [
            [InlineKeyboardButton(f"🌅 Morning: {settings.get('morning_time', '07:00')}", callback_data='set_morning')],
            [InlineKeyboardButton(f"🌙 Night: {settings.get('night_time', '21:00')}", callback_data='set_night')],
            [InlineKeyboardButton("← Back", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "⚙️ Settings\n\nClick any to change:"
        await query.edit_message_text(text, reply_markup=reply_markup)
    
    elif query.data == 'set_morning':
        await query.edit_message_text("Send morning time in HH:MM format (e.g., 07:00)")
        context.user_data['waiting_for'] = 'morning'
    
    elif query.data == 'set_night':
        await query.edit_message_text("Send night time in HH:MM format (e.g., 21:00)")
        context.user_data['waiting_for'] = 'night'
    
    elif query.data == 'test':
        morning = random.choice(MESSAGES['morning'])
        night = random.choice(MESSAGES['night'])
        text = f"🌅 Morning:\n{morning}\n\n🌙 Night:\n{night}"
        await query.edit_message_text(text)
    
    elif query.data == 'stop':
        user_settings[user_id]['enabled'] = False
        await query.edit_message_text("✅ Messages stopped. Use /start to enable again.")
    
    elif query.data == 'back':
        keyboard = [
            [InlineKeyboardButton("⚙️ Settings", callback_data='settings')],
            [InlineKeyboardButton("📱 Test Message", callback_data='test')],
            [InlineKeyboardButton("❌ Stop Messages", callback_data='stop')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "🌙 Lovinow Bot\n\nChoose an option:"
        await query.edit_message_text(text, reply_markup=reply_markup)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text input for settings."""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if user_id not in user_settings:
        user_settings[user_id] = {
            'name': 'Haven',
            'morning_time': '07:00',
            'night_time': '21:00',
            'enabled': True
        }
    
    waiting_for = context.user_data.get('waiting_for')
    
    if waiting_for == 'morning':
        try:
            time.fromisoformat(text)
            user_settings[user_id]['morning_time'] = text
            await update.message.reply_text(f"✅ Morning time set to {text}")
            context.user_data['waiting_for'] = None
        except:
            await update.message.reply_text("❌ Invalid format. Use HH:MM (e.g., 07:00)")
    
    elif waiting_for == 'night':
        try:
            time.fromisoformat(text)
            user_settings[user_id]['night_time'] = text
            await update.message.reply_text(f"✅ Night time set to {text}")
            context.user_data['waiting_for'] = None
        except:
            await update.message.reply_text("❌ Invalid format. Use HH:MM (e.g., 21:00)")


def main() -> None:
    """Start the bot."""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")
    
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Run the bot
    application.run_polling()


if __name__ == '__main__':
    main()
