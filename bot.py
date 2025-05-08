import os
import discord
import responses
from discord.ext import commands
from dotenv import load_dotenv
from core.shadow import process_commands, is_session_active

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=">", intents=intents, help_command=None)


@bot.event
async def on_ready():
    print(f"{bot.user} jest online!")
    await bot.change_presence(activity=discord.Game(name="Cooking dogs"))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    p_message = message.content

    if p_message.startswith(">"):
        await bot.process_commands(message)
        return

    result = await process_commands(p_message, message)
    if result:
        await message.channel.send(result)
        return

    if is_session_active(message.channel.id):
        async with message.channel.typing():
            response = await responses.get_response(message)
        if response:
            await message.channel.send(response)


bot.run(TOKEN)
