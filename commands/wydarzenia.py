from services.filemanager import handle_command

async def wydarzenia_command(message, ctx):
    return await handle_command(message, ctx, "wydarzenia")
