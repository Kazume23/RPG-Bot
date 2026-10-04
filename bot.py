import asyncio
import logging
from discord.ext import commands
from pathlib import Path

import discord
import command_router
from config.settings import settings
from services.dm_sender import send_startup_dm

logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=settings.command_prefix, intents=intents, help_command=None)
_startup_complete = False


@bot.event
async def on_ready():
    global _startup_complete

    if not _startup_complete:
        await send_startup_dm(bot)
        _startup_complete = True

    print(f"{bot.user} jest online!")
    await bot.change_presence(activity=discord.Game(name="Cooking dogs"))


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if (
        message.guild is not None
        and settings.allowed_guild_ids
        and message.guild.id not in settings.allowed_guild_ids
    ):
        return

    if isinstance(message.channel, discord.DMChannel):
        print(f"[DM] {message.author}: {message.content}")

    if not command_router.should_handle(message):
        return

    try:
        async with message.channel.typing():
            response = await command_router.process_message(message, bot)
        if response:
            for chunk in _split_message(response):
                await message.channel.send(chunk)
    except Exception:
        logger.exception("Nieobsłużony błąd podczas przetwarzania wiadomości")
        await message.channel.send("Coś poszło nie tak. Błąd został zapisany w logach.")


def _split_message(content: str, limit: int = 2000):
    if len(content) <= limit:
        return [content]

    chunks = []
    remaining = content
    while remaining:
        split_at = remaining.rfind("\n", 0, limit + 1)
        if split_at <= 0:
            split_at = limit
        chunks.append(remaining[:split_at])
        remaining = remaining[split_at:].lstrip("\n")
    return chunks


async def main():
    cogs_path = Path(__file__).parent / "cogs"
    for file in cogs_path.iterdir():
        if file.suffix == ".py" and file.stem != "__init__":
            ext = f"cogs.{file.stem}"
            print(f"[bot] ładuję extension {ext}")
            await bot.load_extension(ext)
    await bot.start(settings.require_discord_token())


if __name__ == "__main__":
    asyncio.run(main())
