import logging
import asyncio
import os
import requests
from aiohttp import web
from datetime import datetime, date
import pytz

from pyrogram import Client, __version__, types
from pyrogram.raw.all import layer

from database.ia_filterdb import Media
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, LOG_STR
from utils import temp
from Script import script

logging.basicConfig(level=logging.INFO)

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

        logging.info(f"{me.first_name} | Pyrogram v{__version__} (Layer {layer}) | @{me.username}")
        logging.info(LOG_STR)
        logging.info(script.LOGO)

        tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(tz)
        today = date.today()
        await self.send_message(
            chat_id=LOG_CHANNEL,
            text=script.RESTART_TXT.format(today, now.strftime("%H:%M:%S %p"))
        )

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")


# ----------- Render Port Server ------------ #
async def handle_alive(request):
    return web.Response(text="Bot is alive!")

def run_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle_alive)])
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, port=port)


# ------------- Start Everything ------------- #
async def main():
    bot = Bot()
    await bot.start()
    
    # Start aiohttp in background
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, run_web_server)

    # Keep alive forever
    await asyncio.Event().wait()

if __name__ == "__main__":
    import uvicorn

    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.start())
    print("Bot started")
    loop.run_until_complete(asyncio.Event().wait())  # Keeps bot alive
