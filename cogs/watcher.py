# cogs/watcher.py

import os
from dotenv import load_dotenv
import psutil
from discord.ext import commands, tasks
from services.dm_sender import manual_send
import time

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
GAME_WHITELIST = [
    exe.strip() for exe in os.getenv("GAME_WHITELIST", "").split(",")
    if exe.strip()
]

TEST_THRESHOLD = 5


class WatcherCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.seen = set()
        self.start_times = {}
        self.monitor_loop.start()

    @tasks.loop(seconds=10)
    async def monitor_loop(self):
        now = time.time()
        for p in psutil.process_iter(['name', 'cmdline']):
            try:
                name = p.info.get('name') or ""
                cmd = p.info.get('cmdline') or []
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            for p in psutil.process_iter(['name', 'cmdline']):
                name = p.info.get('name', '').lower()
                if name in ('java.exe', 'javaw.exe'):
                    print("[DEBUG] java pid", p.pid, "cmdline:", p.info.get('cmdline'))
                if 'slaythespire' in name:
                    print("[DEBUG] wrapper pid", p.pid, "name:", name)
            for game in GAME_WHITELIST:
                detected = (
                        name.lower() == game.lower()
                        or (
                                name.lower() in ('java.exe', 'javaw.exe')
                                and any(game.lower() in arg.lower() for arg in cmd)
                        )
                )
                if not detected:
                    continue

                if game not in self.start_times:
                    self.start_times[game] = now
                    print(f"[Watcher] Uruchomiono grę: {game}")
                elif now - self.start_times[game] >= TEST_THRESHOLD:
                    try:
                        p.kill()
                        await manual_send(
                            self.bot,
                            ADMIN_ID,
                            f"Shadow: Wyłączyłem '{game} po {TEST_THRESHOLD}sec."
                        )
                    except Exception as e:
                        print(f"[Watcher][ERROR] kill DM: {e}")
                    del self.start_times[game]

            active_games = {
                game for game, start in self.start_times.items()
                if any(
                    (p.info.get('name') or "").lower() == game.lower()
                    for p in psutil.process_iter(['name'])
                )
            }
            self.start_times = {g: t for g, t in self.start_times.items() if g in active_games}

    @monitor_loop.before_loop
    async def before_monitor(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(WatcherCog(bot))
