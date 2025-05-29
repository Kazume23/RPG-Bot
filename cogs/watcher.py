# cogs/watcher.py

import os
from dotenv import load_dotenv
import psutil, asyncio
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
        proc_list = await asyncio.to_thread(
            lambda: list(psutil.process_iter(['name', 'cmdline', 'pid']))
        )

        for p in proc_list:
            try:
                name = p.info.get('name') or ""
                cmd = p.info.get('cmdline') or []
                path = ""
                try:
                    path = p.exe() or ""
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue

            for game in GAME_WHITELIST:
                gl = game.lower()
                nl = name.lower()
                nl = name.lower()
                detected = False

                if nl == gl:
                    detected = True

                elif nl in ('java.exe', 'jawav.exe') and any(gl in arg.lower() for arg in cmd):
                    detected = True

                elif gl in path.lower():
                    detected = True

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
                            f"Shadow: wyłączyłem '{game}' po {TEST_THRESHOLD} sek stary chuju."
                        )
                    except Exception as e:
                        print(f"[Watcher][ERROR] kill dm: {e}")
                    finally:
                        del self.start_times[game]

            running_names = {p.info.get('name', '').lower() for p in proc_list}
            exe_paths = []
            for p in proc_list:
                try:
                    path = p.exe() or ""
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    path = ""
                exe_paths.append(path.lower())

            new_start_times = {}
            for game, ts in self.start_times.items():
                gl = game.lower()
                if gl in running_names or any(gl in ep for ep in exe_paths):
                    new_start_times[game] = ts
            self.start_times = new_start_times

    @monitor_loop.before_loop
    async def before_monitor(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(WatcherCog(bot))
