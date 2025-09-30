import os
import asyncio
from discord.ext import commands, tasks
from services.voice_assistant import (
    record_chunk, transcribe, is_speech, is_wake, handle_command
)
from dotenv import load_dotenv

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
WAKE_DURATION = 3
CMD_DURATION = 3


class VoiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_loop.start()

    @tasks.loop(seconds=5)
    async def voice_loop(self):
        # 1) Nagryj próbkę – fraza wake-word
        wake_file = await asyncio.to_thread(record_chunk, WAKE_DURATION, "wake.wav")
        # 2) Sprawdź, czy jest mowa (VAD)
        if not await asyncio.to_thread(is_speech, wake_file):
            return
        # 3) Transkrypcja
        wake_text = await asyncio.to_thread(transcribe, wake_file)
        if not is_wake(wake_text):
            return

        # 4) Wake-word wykryty → pobierz komendę
        cmd_file = await asyncio.to_thread(record_chunk, CMD_DURATION, "cmd.wav")
        cmd_text = await asyncio.to_thread(transcribe, cmd_file)

        # 5) Wyślij DM do ADMIN_ID z komendą
        user = await self.bot.fetch_user(ADMIN_ID)
        await user.send(f"**Voice Command** → `{cmd_text}`")

        # 6) (Opcjonalnie) wykonaj lokalną akcję
        await asyncio.to_thread(handle_command, cmd_text)

    @voice_loop.before_loop
    async def before_voice(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(VoiceCog(bot))
