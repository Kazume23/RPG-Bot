import discord
import openai
import os
from openai import OpenAI
from core import shadow
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

total_tokens_used = 0
TOKEN_LIMIT = 3000


async def get_response(message: discord.Message):
    p_message = message.content.strip()
    if p_message.upper().startswith("ARISE"):
        parts = p_message.split()

        if len(parts) == 1:
            return shadow.toggle_session("ARISE", "none", message)
        elif len(parts) == 2:
            return shadow.toggle_session("ARISE", parts[1], message)
        else:
            return "Użycie: ARISE <osobowość>. Dostępne: " + ", ".join(shadow.PERSONALITIES.keys())

    if p_message.upper() == "CEASE":
        return shadow.toggle_session("CEASE")

    if p_message.startswith('>'):
        return await process_commands(p_message, message)

    if shadow.is_session_active(message.channel.id):
        return await shadow.get_shadow_response(message)

    return None


async def process_commands(p_message, ctx):
    import commands

    if p_message.startswith(f'>dm'):
        return await commands.dm_command(ctx, p_message)

    if p_message.startswith(f'>sesja'):
        return await commands.sesja_command(ctx, p_message)

    if p_message.startswith(f'>purge'):
        return await commands.purge_command(ctx, p_message)

    if p_message == f'>hello':
        return await commands.hello_command()

    if p_message.startswith(f'>ochlapus'):
        return await commands.ochlapus_command(p_message)

    if p_message.startswith(f'>u') and len(p_message) <= 2:
        return await commands.umiejki_command(p_message)

    if p_message.startswith(f'>z'):
        return await commands.zdolnosci_command(p_message)

    if p_message.startswith(f'>roll'):
        return await commands.roll_command(p_message)

    if p_message.startswith(f'>ukryty'):
        return await commands.ukryty_command(p_message, ctx)

    if p_message.startswith(f'>klnij'):
        return await commands.klnij_command()

    if p_message.startswith(f'>help'):
        return await commands.help_command()

    if p_message.startswith(f'>wy') or p_message.startswith(f'>wydarzenia'):
        return await commands.wydarzenia_command(p_message, ctx)

    if p_message.startswith(f'>not') or p_message.startswith(f'>notatki'):
        return await commands.notatka_command(p_message, ctx)

    if p_message.startswith(f'>npc'):
        return await commands.npc_command(p_message, ctx)

    return "Naucz się w końcu tych komend KURWAAA"
