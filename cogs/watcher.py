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
print("[Watcher] GAME_WHITELIST =", GAME_WHITELIST)


class WatcherCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.seen = set()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.monitor_loop.is_running():
            self.monitor_loop.start()

    @tasks.loop(seconds=10)
    async def monitor_loop(self):
        procs = {p.info['name'] for p in psutil.process_iter(['name'])}
        print(f"[Watcher] dostępne procesy (pierwsze 5): {list(procs)[:5]}")
        for game in GAME_WHITELIST:
            if game in procs and game not in self.seen:
                print(f"[Watcher] Uruchomiono grę: {game}")
                await manual_send(self.bot, ADMIN_ID, f"Shadow wykrył `{game}`.")
                self.seen.add(game)
            elif game not in procs and game in self.seen:
                self.seen.remove(game)


async def setup(bot):
    await bot.add_cog(WatcherCog(bot))
    print("[WatcherCog] załadowany, whitelist =", GAME_WHITELIST, "ADMIN_ID =", ADMIN_ID)
