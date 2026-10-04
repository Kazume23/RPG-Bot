from commands.utility import has_admin_permissions
from services.filemanager import handle_command


async def wydarzenia_command(ctx, args: str):
    if not has_admin_permissions(ctx):
        return "Spierdalaj. Nie masz nade mną władzy śmiertelniku"
    return await handle_command(args, "wydarzenia")
