from aiohttp import web

async def web_server():
    app = web.Application()
    async def home(request):
        return web.Response(text="Bot is alive.")
    app.router.add_get("/", home)
    return app
