from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, filters
import json
import logging
import os
import asyncio
import nest_asyncio
import re
from src.core.managers.json_file_handler import get_json_path
from httpx import ConnectTimeout

# Apply nest_asyncio
nest_asyncio.apply()

# States for conversation
PASSWORD_CHECK = 1

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants
CHAT_IDS_FILE = get_json_path("chat_ids.json")
BOT_TOKEN_FILE = get_json_path("telegram_config.json")

# Helper Functions
def load_bot_config() -> dict:
    with open(BOT_TOKEN_FILE, 'r') as f:
        return json.load(f)

def load_chat_ids() -> list:
    try:
        if not os.path.exists(CHAT_IDS_FILE):
            with open(CHAT_IDS_FILE, 'w') as f:
                json.dump([], f)
            return []

        with open(CHAT_IDS_FILE, 'r') as f:
            chat_ids = json.load(f)
        return chat_ids
    except Exception as e:
        logger.error(f"Error loading chat IDs: {e}")
        return []

def save_new_user(chat_id, username, firt_name,last_name):
   try:
       # Load existing users
       chat_ids = load_chat_ids()
       
       # Add new user
       new_user = {
           'chat_id': chat_id,
           'username': username,
           'first_name': firt_name,
           'last_name':last_name
       }
       chat_ids.append(new_user)
       
       # Save updated list
       with open(CHAT_IDS_FILE, 'w') as f:
           json.dump(chat_ids, f, indent=4)
           
   except Exception as e:
       logger.error(f"Error saving new user: {e}")

# Command Handlers
async def start(update: Update, context: CallbackContext) -> int:
    """Handle the /start command"""
    try:
        chat_id = update.message.chat.id
        user_name = update.message.from_user.username or "Unknown"
        first_name = update.message.from_user.first_name or "Unknown"

        
        logger.info(f"Start command received from user {user_name} (ID: {chat_id})")
        await update.message.reply_text(f"🔒 Welcome! {first_name}\n\n To receive product notifications, please enter the access password.\n\n")
        
        return PASSWORD_CHECK
    
    except Exception as e:
        logger.error(f"Error processing start command: {e}")
        await update.message.reply_text(
            "Sorry, there was an error processing your request. Please try again later."
        )
        return ConversationHandler.END

def clean_name(name):
    # Remove emojis and other unicode characters
    if name is None:
        return ""
    return re.sub(r'[^\x00-\x7F]+', '', name).strip()

async def check_password(update: Update, context: CallbackContext) -> int:
    try:
        chat_id = update.message.chat.id
        username = update.message.from_user.username or "Unknown"
        first_name = clean_name(update.message.from_user.first_name) or "Unknown"
        last_name = clean_name(update.message.from_user.last_name) or ""
        entered_password = update.message.text
        
        config = load_bot_config()
        correct_password = config.get('password', '')
        print(f'Password is :{correct_password}')
        
        if entered_password == correct_password:
            chat_ids = load_chat_ids()
            
            # Check if user already exists
            if not any(user['chat_id'] == chat_id for user in chat_ids):
                save_new_user(chat_id, username, first_name,last_name)
                welcome_message = (
                    f"🎉 Welcome {first_name} {last_name}!\n\n"
                    "You've been successfully added to the product notification list.\n\n"
                    "You will receive alerts when products become available.\n\n"
                    "Use /end to stop receiving notifications."
                )
                await update.message.reply_text(welcome_message)
                logger.info(f"New user {username} (ID: {chat_id}) added")
            else:
                already_subscribed_message = (
                    f"✅ Welcome back {first_name} {last_name}!\n\n"
                    "You're already subscribed to product notifications.\n\n"
                    "Use /end to stop receiving notifications."
                )
                await update.message.reply_text(already_subscribed_message)
                
        else:
            await update.message.reply_text("Incorrect password. Use /start to try again.")
            
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error checking password: {e}")
        await update.message.reply_text("Error processing request. Please try again.")
        return ConversationHandler.END

def remove_user(chat_id):
   try:
       chat_ids = load_chat_ids()
       chat_ids = [user for user in chat_ids if user['chat_id'] != chat_id]
       with open(CHAT_IDS_FILE, 'w') as f:
           json.dump(chat_ids, f, indent=4)
       return True
   except Exception as e:
       logger.error(f"Error removing user: {e}")
       return False

async def end(update: Update, context: CallbackContext) -> None:
   try:
       chat_id = update.message.chat.id
       user_name = update.message.from_user.username or "Unknown"
       first_name = clean_name(update.message.from_user.first_name) or "Unknown"
       last_name = clean_name(update.message.from_user.last_name) or ""

       
       chat_ids = load_chat_ids()
       # Check if user exists in chat_ids
       if any(user['chat_id'] == chat_id for user in chat_ids):
           remove_user(chat_id)
           goodbye_message = (
               f"👋 Goodbye {first_name} {last_name}!\n\n"
               "You've been removed from notifications list.\n"
               "Use /start to subscribe again."
           )
           await update.message.reply_text(goodbye_message)
           logger.info(f"User {user_name} ({chat_id}) removed")
       else:
           await update.message.reply_text(
               f"Hi {first_name}!\n"
               "You're not subscribed.\n"
               "Use /start to subscribe."
           )
           
   except Exception as e:
       logger.error(f"Error in end command: {e}")
       await update.message.reply_text("Error processing request. Try again later.")

async def error_handler(update: Update, context: CallbackContext) -> None:
    logger.error(f"Update {update} caused error {context.error}")

# Main Function
async def run_bot():
    try:
        bot_config = load_bot_config()
        bot_token = bot_config.get('bot_token', '')

        app = ApplicationBuilder().token(bot_token).build()
        app.add_handler(ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={PASSWORD_CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_password)]},
            fallbacks=[CommandHandler("end", end)]
        ))
        app.add_handler(CommandHandler("end", end))
        app.add_error_handler(error_handler)

        await app.bot.delete_webhook(drop_pending_updates=True)
        logger.info("Bot started successfully.")
        await app.run_polling()
    except ConnectTimeout:
        logger.error("Connection timed out. Retrying...")
        await asyncio.sleep(5)
        await run_bot()
    except Exception as e:
        logger.error(f"Critical error in bot: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Bot stopped manually.")
