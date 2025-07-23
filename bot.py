# bot.py

import logging
import asyncio
import os
import requests
from aiohttp import web, ClientSession
from pyrogram import Client, __version__, types
from pyrogram.raw.all import layer
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR, LOG_CHANNEL, PORT
from utils import temp
from Script import script
from datetime import datetime, date
from typing import Union, Optional, AsyncGenerator
import pytz

logging.basicConfig(level=logging.INFO)

# Bot Class
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

        logging.info(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on @{me.username}.")
        logging.info(LOG_STR)
        logging.info(script.LOGO)

        # Log Restart
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

app = Bot()

# AIOHTTP Web Server
async def handle_alive(request):
    return web.Response(text="I am alive!")

async def web_server():
    server = web.Application()
    server.router.add_get("/", handle_alive)
    return server

# Ping function (replaces Flask + thread)
def ping_self():
    try:
        url = "https://f-njat.onrender.com"  # Replace with actual Render URL
        response = requests.get(url)
        if response.status_code == 200:
            logging.info("Ping successful.")
        else:
            logging.warning(f"Ping failed with status: {response.status_code}")
    except Exception as e:
        logging.error(f"Ping error: {e}")

# Main runner
async def main():
    await app.start()

    # Start web server on Render
    runner = web.AppRunner(await web_server())
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(PORT))
    await site.start()

    # Start scheduler for self-ping
    scheduler = AsyncIOScheduler()
    scheduler.add_job(ping_self, "interval", minutes=1)
    scheduler.start()

    # Wait forever
    await asyncio.Event().wait()

# Entry point
if __name__ == "__main__":
    asyncio.run(main())
