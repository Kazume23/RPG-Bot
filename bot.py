import os
import discord
import responses
from discord.ext import commands
from dotenv import load_dotenv

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

    # Wysłanie wiadomości do responses.py, by procesował komendy
    user_message = message.content
    response = await responses.get_response(user_message, message)

    if response:
        await message.channel.send(response)

    # Jeśli wiadomość nie jest komendą, przetwarzaj komendy Discorda
    await bot.process_commands(message)


bot.run(TOKEN)
