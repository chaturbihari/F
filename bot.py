# bot.py

import pyromod.listen
from pyrogram import Client
from aiohttp import web
from config import API_ID, API_HASH, BOT_TOKEN, PORT
from plugins import web_server
import sys
from datetime import datetime

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins={"root": "plugins"}
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.username = me.username
        self.uptime = datetime.now()

        # Web server start
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()

        print(f"Bot started as @{self.username}")

    async def stop(self, *args):
        await super().stop()
        print("Bot stopped.")

bot = Bot()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(bot.start())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped manually")
