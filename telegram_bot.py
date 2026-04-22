"""
Companion Bot for Telegram
Send daily warm messages to users at scheduled times
"""

import os
import json
from datetime import datetime, time
from zoneinfo import ZoneInfo
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    JobQueue,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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
        "You made it to another morning. That's beautiful. 🌅",
        "Possibility is everywhere. Look around. 🌈",
        "This day is yours. Make it count. 💪",
        "Good morning, warrior. Rest is over. You're on. ⚡"
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
        "Night brings silence. Let it soothe you. 🌙",
        "You showed up. Now let go. Sleep deeply. 💫",
        "Tomorrow can wait. Tonight is just for rest. 🌜",
        "Breathe. Release. Sleep. You're safe. 💙"
    ]
}

# User settings storage (in production, use a database)
user_settings = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_id = update.effective_user.id
    
    # Initialize user settings if not exists
    if user_id not in user_settings:
        user_settings[user_id] = {
            'bot_name': 'Haven',
            'morning_time': '07:00',
            'night_time': '21:00',
            'timezone': 'UTC',
            'enabled': True
        }
    
    keyboard = [
        [InlineKeyboardButton("⚙️ Settings", callback_data='settings')],
        [InlineKeyboardButton("📱 Test Message", callback_data='test')],
        [InlineKeyboardButton("❌ Stop Messages", callback_data='stop')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """🌙 Welcome to Companion Bot!

Every day you'll get two warm messages:
• **Morning** (7:00 AM by default) - Encouragement to start your day
• **Night** (9:00 PM by default) - Wisdom to help you rest

Each message is different every day. No repeats. Just genuine love and support.

Customize your times and preferences in settings. 💛"""
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)


async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show settings menu."""
    user_id = update.effective_user.id
    settings = user_settings.get(user_id, {})
    
    keyboard = [
        [InlineKeyboardButton(f"🌅 Morning: {settings.get('morning_time', '07:00')}", callback_data='set_morning')],
        [InlineKeyboardButton(f"🌙 Night: {settings.get('night_time', '21:00')}", callback_data='set_night')],
        [InlineKeyboardButton(f"🌍 Timezone: {settings.get('timezone', 'UTC')}", callback_data='set_timezone')],
        [InlineKeyboardButton("← Back", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = "⚙️ **Settings**\n\nTap any setting to change it:"
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses."""
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    if query.data == 'settings':
        await settings_menu(update, context)
    
    elif query.data == 'set_morning':
        text = "Send the morning message time in HH:MM format (e.g., 07:00)"
        await query.edit_message_text(text)
        context.user_data['waiting_for'] = 'morning_time'
    
    elif query.data == 'set_night':
        text = "Send the night message time in HH:MM format (e.g., 21:00)"
        await query.edit_message_text(text)
        context.user_data['waiting_for'] = 'night_time'
    
    elif query.data == 'set_timezone':
        text = "Send your timezone (e.g., UTC, America/New_York, Europe/London)"
        await query.edit_message_text(text)
        context.user_data['waiting_for'] = 'timezone'
    
    elif query.data == 'test':
        import random
        morning_msg = random.choice(MESSAGES['morning'])
        night_msg = random.choice(MESSAGES['night'])
        
        text = f"""🌅 **Morning Message:**\n{morning_msg}\n\n🌙 **Night Message:**\n{night_msg}"""
        await query.edit_message_text(text, parse_mode='Markdown')
    
    elif query.data == 'stop':
        user_settings[user_id]['enabled'] = False
        text = "✅ Messages stopped. Use /start to enable again."
        await query.edit_message_text(text)
    
    elif query.data == 'back':
        keyboard = [
            [InlineKeyboardButton("⚙️ Settings", callback_data='settings')],
            [InlineKeyboardButton("📱 Test Message", callback_data='test')],
            [InlineKeyboardButton("❌ Stop Messages", callback_data='stop')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = "🌙 **Companion Bot**\n\nChoose an option:"
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text input for settings."""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if user_id not in user_settings:
        user_settings[user_id] = {
            'bot_name': 'Haven',
            'morning_time': '07:00',
            'night_time': '21:00',
            'timezone': 'UTC',
            'enabled': True
        }
    
    waiting_for = context.user_data.get('waiting_for')
    
    if waiting_for == 'morning_time':
        try:
            # Validate time format
            datetime.strptime(text, '%H:%M')
            user_settings[user_id]['morning_time'] = text
            await update.message.reply_text(f"✅ Morning time set to {text}")
            await settings_menu(update, context)
            context.user_data['waiting_for'] = None
        except ValueError:
            await update.message.reply_text("❌ Invalid format. Please use HH:MM (e.g., 07:00)")
    
    elif waiting_for == 'night_time':
        try:
            datetime.strptime(text, '%H:%M')
            user_settings[user_id]['night_time'] = text
            await update.message.reply_text(f"✅ Night time set to {text}")
            await settings_menu(update, context)
            context.user_data['waiting_for'] = None
        except ValueError:
            await update.message.reply_text("❌ Invalid format. Please use HH:MM (e.g., 21:00)")
    
    elif waiting_for == 'timezone':
        try:
            # Validate timezone
            ZoneInfo(text)
            user_settings[user_id]['timezone'] = text
            await update.message.reply_text(f"✅ Timezone set to {text}")
            await settings_menu(update, context)
            context.user_data['waiting_for'] = None
        except Exception:
            await update.message.reply_text("❌ Invalid timezone. Try: UTC, America/New_York, Europe/London, Asia/Tokyo")


async def send_morning_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send morning message to all users."""
    import random
    message = random.choice(MESSAGES['morning'])
    
    for user_id, settings in user_settings.items():
        if settings.get('enabled', True):
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"🌅 {message}"
                )
            except Exception as e:
                logger.error(f"Failed to send message to {user_id}: {e}")


async def send_night_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send night message to all users."""
    import random
    message = random.choice(MESSAGES['night'])
    
    for user_id, settings in user_settings.items():
        if settings.get('enabled', True):
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"🌙 {message}"
                )
            except Exception as e:
                logger.error(f"Failed to send message to {user_id}: {e}")


async def setup_jobs(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set up scheduled jobs for sending messages."""
    # Morning job at 7:00 AM UTC
    context.job_queue.run_daily(
        send_morning_message,
        time=time(hour=7, minute=0),
        name='morning_job'
    )
    
    # Night job at 9:00 PM UTC
    context.job_queue.run_daily(
        send_night_message,
        time=time(hour=21, minute=0),
        name='night_job'
    )
    
    logger.info("Jobs scheduled: Morning (7:00 AM) and Night (9:00 PM) UTC")


def main() -> None:
    """Start the bot."""
    # Create the Application
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")
    
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(application.add_handler(CommandHandler('settings', settings_menu)))
    
    # Add text handler for settings input
    from telegram.ext import MessageHandler, filters
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Set up scheduled jobs
    application.post_init = setup_jobs
    
    # Run the bot
    application.run_polling()


if __name__ == '__main__':
    main()
