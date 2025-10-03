from services.character_aliver import *
from commands.utility import has_admin_permissions


async def npc_command(ctx):
    if not has_admin_permissions(ctx):
        return "Spierdalaj. Nie masz nade mną władzy śmiertelniku"
    parts = ctx.content.split(maxsplit=2)
    if len(parts) > 3:
        return "Wypierdalaj stary przyczłapie"

    return await character_randomizer(parts[1].lower(), parts[2].lower())
