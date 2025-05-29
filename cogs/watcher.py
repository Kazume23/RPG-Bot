# cogs/watcher.py

import os
from dotenv import load_dotenv
import psutil
from discord.ext import commands, tasks
from services.dm_sender import manual_send

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
GAME_WHITELIST = [
    exe.strip() for exe in os.getenv("GAME_WHITELIST", "").split(",")
    if exe.strip()
]


class WatcherCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.seen = set()
        self.monitor_loop.start()

    @tasks.loop(seconds=10)
    async def monitor_loop(self):
        for p in psutil.process_iter(['name', 'cmdline']):
            try:
                name = p.info.get('name') or ""
                cmd = p.info.get('cmdline') or []
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

            for game in GAME_WHITELIST:
                if name.lower() == game.lower():
                    detected = True
                elif name.lower() in ('java.exe', 'javaw.exe') and any(game.lower() in arg.lower() for arg in cmd):
                    detected = True
                else:
                    detected = False

                if detected and game not in self.seen:
                    print(f"[Watcher] Uruchomiono grę: {game}")
                    try:
                        await manual_send(self.bot, ADMIN_ID,
                                          f"Shadow wykrył uruchomienie gry `{game}`.")
                    except Exception as e:
                        print(f"[Watcher][ERROR] DM: {e}")
                    self.seen.add(game)

        current = set()
        for p in psutil.process_iter(['name', 'cmdline']):
            ni = p.info.get('name') or ""
            ci = p.info.get('cmdline') or []
            for game in GAME_WHITELIST:
                if ni.lower() == game.lower() or (
                        ni.lower() in ('java.exe', 'javaw.exe')
                        and any(game.lower() in arg.lower() for arg in ci)):
                    current.add(game)
        self.seen &= current

    @monitor_loop.before_loop
    async def before_monitor(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(WatcherCog(bot))
