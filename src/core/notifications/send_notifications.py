import asyncio
import json
import requests
from typing import Dict
from src.core.managers.json_file_handler import get_json_path
# Load Bot Token from the JSON file
BOT_TOKEN_FILE = get_json_path("telegram_config.json")

def load_bot_config() -> Dict:
    with open(BOT_TOKEN_FILE, 'r') as f:
        return json.load(f)

# Load token from configuration
bot_token_config = load_bot_config()
BOT_TOKEN = bot_token_config.get('bot_token','')
print(f"bot_token is {BOT_TOKEN}")

# Load chat IDs from file
CHAT_IDS_FILE = get_json_path("chat_ids.json")

def load_chat_ids():
    """Load chat IDs of users who initiated a chat with the bot."""
    try:
        with open(CHAT_IDS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

async def send_message_async(chat_id, product_title, product_url,formatted_products):
    """Send a notification to a single Telegram user."""
    message_body = (
        f"🔔 *Product Alert!*\n\n"
        f"*Product Name:* \n\n{product_title}\n\n"
        f"*Status:* Available now\n\n"
        f"*Available Stocks:*\n\n{formatted_products}\n\n"
        f"[Click here to buy the product]({product_url})"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_body,
        "parse_mode": "Markdown",
    }
    try:
        response = await asyncio.to_thread(requests.post, url, json=payload)
        if response.status_code == 200:
            return {"chat_id": chat_id, "success": True, "message_id": response.json().get("result", {}).get("message_id")}
        else:
            return {"chat_id": chat_id, "success": False, "error": response.json().get("description", "Unknown error")}
    except Exception as e:
        return {"chat_id": chat_id, "success": False, "error": str(e)}

async def send_notifications(product_title, product_url, formatted_products):
    chat_ids_list = load_chat_ids()  # Loads list of user dictionaries
    if not chat_ids_list:
        print("No users available")
        return []

    # Extract just the chat_ids from user dictionaries
    chat_ids = [user['chat_id'] for user in chat_ids_list]
    
    tasks = [
        send_message_async(chat_id, product_title, product_url, formatted_products)
        for chat_id in chat_ids
    ]
    
    results = await asyncio.gather(*tasks)
    
    for result in results:
        if result["success"]:
            print(f"Message sent to {result['chat_id']}")
        else:
            print(f"Failed to send to {result['chat_id']}: {result['error']}")
            
    return results