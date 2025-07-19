import logging
import sys
import asyncio
import os
import requests
from flask import Flask, request
from threading import Thread
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR, LOG_CHANNEL, PORT
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types, filters
from Script import script
from datetime import date, datetime
import pytz
import shutil

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logging.info(f"🔧 Python Version: {sys.version}")

# Pyrogram Bot Class
class Bot(Client):
    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        await super().start()
        await Media.ensure_indexes()
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username
        logging.info(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
        logging.info(LOG_STR)
        logging.info(script.LOGO)
        tz = pytz.timezone('Asia/Kolkata')
        today = date.today()
        now = datetime.now(tz)
        current_time = now.strftime("%H:%M:%S %p")
        await self.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, current_time))

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")

    async def iter_messages(self, chat_id: Union[int, str], limit: int, offset: int = 0) -> Optional[AsyncGenerator["types.Message", None]]:
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current + new_diff + 1)))
            for message in messages:
                yield message
                current += 1

# Initialize bot
app = Bot()

# Flask app
flask_app = Flask(__name__)

@flask_app.route('/alive')
def alive():
    return "I am alive!"

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if update and app:
        logging.info(f"Received update: {update}")
        app.process_update(update)
    return "OK", 200

def run_flask():
    try:
        flask_app.run(host='0.0.0.0', port=10002)
    except OSError as e:
        if "Address already in use" in str(e):
            logging.error("Port 10002 in use! Trying alternate port 5000...")
            flask_app.run(host='0.0.0.0', port=5000)
        else:
            raise

# ✅ These used to be scheduled — now converted to commands:

def clear_cache_and_sessions():
    folders_to_clear = ['.cache', '__pycache__', '.git']
    for folder in folders_to_clear:
        logging.info(f"Checking folder: {folder}")
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                logging.info(f"✅ Cleared folder: {folder}")
            except Exception as e:
                logging.error(f"❌ Error clearing {folder}: {e}")
        else:
            logging.warning(f"⚠️ Folder not found: {folder}")

def self_ping():
    try:
        logging.info("🌐 Self-pinging...")
        response = requests.get("https://f-njat.onrender.com", timeout=10)
        if response.status_code == 200:
            logging.info("✅ Ping successful")
        else:
            logging.warning(f"⚠️ Ping failed: {response.status_code}")
    except Exception as e:
        logging.error(f"❌ Ping error: {e}")

# ✅ Add manual command to clear cache via Telegram
@app.on_message(filters.command("clear_cache") & filters.user([LOG_CHANNEL]))
async def clear_cache_command(_, message):
    clear_cache_and_sessions()
    await message.reply("✅ Cache folders cleared.")

# ✅ Add manual command to trigger self-ping via Telegram
@app.on_message(filters.command("self_ping") & filters.user([LOG_CHANNEL]))
async def self_ping_command(_, message):
    self_ping()
    await message.reply("✅ Self-ping triggered.")

# Main bot logic
async def main():
    await app.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    # Start Flask in a thread
    Thread(target=run_flask).start()

    # Use consistent event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
