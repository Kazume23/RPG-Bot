from services.character_aliver import *


async def npc_command(ctx):
    parts = ctx.content.split(maxsplit=1)
    return await character_randomizer(parts[1].lower())
