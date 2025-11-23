# main.py
import os
import asyncio
from bot import run
from aiohttp import web

async def hello(request):
    return web.Response(text="Bot is running")

async def main():
    # Start your bot in background
    loop = asyncio.get_event_loop()
    loop.create_task(asyncio.to_thread(run))
    
    # Start tiny web server
    app = web.Application()
    app.add_routes([web.get("/", hello)])
    port = int(os.environ.get("PORT", 5000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
