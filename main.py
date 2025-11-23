# main.py
import os
import asyncio
from bot import run
from aiohttp import web

# Simple HTTP endpoint to satisfy Render
async def hello(request):
    return web.Response(text="Bot is running")

async def main():
    # Run your Discord bot in background
    loop = asyncio.get_event_loop()
    loop.create_task(asyncio.to_thread(run))
    
    # Start small web server on port 5000
    app = web.Application()
    app.add_routes([web.get("/", hello)])
    port = 5000  # use Render-friendly port
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    # Keep process alive
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
