import logging
from pyrogram import Client
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL
from utils import temp
from Script import script
from datetime import date, datetime
import pytz

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
        # Pre-start: load DB bans
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats

        # Pyrogram init
        await super().start()

        # Index MongoDB
        await Media.ensure_indexes()

        # Store bot info
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username

        # Logging
        logging.info(f"{me.first_name} started on {self.username}.")
        logging.info(script.LOGO)

        # Log startup in group
        tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(tz).strftime("%H:%M:%S %p")
        today = date.today()
        await self.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, now))

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped.")


# Main bot instance
app = Bot()

# Run via Pyrogram's internal runner (render-safe)
if __name__ == "__main__":
    app.run()
