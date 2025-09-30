import discord
import openai
import os
from openai import OpenAI
from core import shadow
from dotenv import load_dotenv
from core.shadow_context import ShadowContext

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

    if p_message.startswith(">"):
        ctx = ShadowContext(message._state._get_client(), message)
        return await process_commands(ctx)

    if shadow.is_session_active(message.channel.id):
        return await shadow.get_shadow_response(message)

    return None


async def process_commands(ctx: ShadowContext):
    import commands
    content = ctx.content

    if content.startswith(">dm"):
        return await commands.dm_command(ctx)

    if content.startswith(">sesja"):
        return await commands.sesja_command(ctx)

    if content.startswith(">purge"):
        return await commands.purge_command(ctx)

    if content == ">hello":
        return await commands.hello_command()

    if content.startswith(">ochlapus"):
        return await commands.ochlapus_command(content)

    if content.startswith(">u") and len(content) <= 2:
        return await commands.umiejki_command(content)

    if content.startswith(">z"):
        return await commands.zdolnosci_command(content)

    if content.startswith(">roll"):
        return await commands.roll_command(content)

    if content.startswith(">ukryty"):
        return await commands.ukryty_command(ctx)

    if content.startswith(">klnij"):
        return await commands.klnij_command()

    if content.startswith(">help"):
        return await commands.help_command()

    if content.startswith(">wy") or content.startswith(">wydarzenia"):
        return await commands.wydarzenia_command(ctx)

    if content.startswith(">not") or content.startswith(">notatki"):
        return await commands.notatka_command(ctx)

    if content.startswith(">npc"):
        return await commands.npc_command(ctx)

    return "Naucz się w końcu tych komend KURWAAA"
