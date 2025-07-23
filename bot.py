import logging
import os
import asyncio
from flask import Flask
from threading import Thread
from datetime import date, datetime
import pytz
import requests

from apscheduler.schedulers.background import BackgroundScheduler
from pyrogram import Client, __version__
from pyrogram.raw.all import layer

from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR, LOG_CHANNEL, PORT
from database.ia_filterdb import Media
from database.users_chats_db import db
from utils import temp
from Script import script

# Bot class using Pyrogram
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
        now = datetime.now(tz)
        await self.send_message(
            chat_id=LOG_CHANNEL,
            text=script.RESTART_TXT.format(date.today(), now.strftime("%H:%M:%S %p"))
        )

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")

# Bot instance
app = Bot()

# Flask server (optional for uptime ping services like UptimeRobot)
flask_app = Flask(__name__)

@flask_app.route('/')
def alive():
    return "I am alive!"

def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

# Self-ping function for uptime monitors
def ping_self():
    url = "https://f-njat.onrender.com"
    try:
        res = requests.get(url)
        logging.info("Ping successful!" if res.status_code == 200 else f"Ping failed: {res.status_code}")
    except Exception as e:
        logging.error(f"Ping error: {e}")

# Main function using polling (no webhook!)
async def main():
    await app.run_polling()

if __name__ == "__main__":
    # Start optional uptime Flask server
    Thread(target=run_flask).start()

    # Start polling bot
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    # Ping every 1 min (optional)
    scheduler = BackgroundScheduler()
    scheduler.add_job(ping_self, "interval", minutes=1)
    scheduler.start()
