from commands.utility import has_admin_permissions
from services.filemanager import handle_command


async def notatka_command(ctx, args: str):
    if not has_admin_permissions(ctx):
        return "Nie masz uprawnień do zarządzania notatkami MG."
    return await handle_command(args, "notatki")
