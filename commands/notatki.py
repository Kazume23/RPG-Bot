from services.filemanager import handle_command


async def notatka_command(message, ctx):
    return await handle_command(message, ctx, "notatki")
