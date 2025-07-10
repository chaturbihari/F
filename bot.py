import logging
import os
import asyncio
import requests
from flask import Flask
from threading import Thread
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from datetime import datetime, date
import pytz

from database.ia_filterdb import Media
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR, LOG_CHANNEL
from utils import temp
from Script import script

# ──────[ SETUP LOGGING ]──────
logging.basicConfig(level=logging.INFO)

# ──────[ FLASK SETUP FOR RENDER PING ]──────
flask_app = Flask(__name__)

@flask_app.route("/alive")
def alive():
    return "✅ Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

# ──────[ BOT CLIENT DEFINITION ]──────
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
        await super().start()
        await Media.ensure_indexes()

        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats

        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name

        tz = pytz.timezone("Asia/Kolkata")
        now = datetime.now(tz)
        today = date.today()
        current_time = now.strftime("%H:%M:%S %p")

        logging.info(f"{me.first_name} (v{__version__}, Layer {layer}) started.")
        logging.info(LOG_STR)
        logging.info(script.LOGO)

        await self.send_message(
            chat_id=LOG_CHANNEL,
            text=script.RESTART_TXT.format(today, current_time)
        )

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped.")

# ──────[ RUN EVERYTHING ]──────
async def main():
    bot = Bot()
    await bot.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    # Run Flask in background thread
    Thread(target=run_flask).start()

    # Start Pyrogram bot safely
    asyncio.run(main())
