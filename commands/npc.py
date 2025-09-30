from services.filemanager import handle_command


async def npc_command(message, ctx):
    return await handle_command(message, ctx, "npc")
