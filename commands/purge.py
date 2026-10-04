from commands.utility import has_admin_permissions
from config.settings import COMMAND_PREFIX


async def purge_command(ctx, args: str):
    if not has_admin_permissions(ctx):
        return "Spierdalaj. Nie masz uprawnień administratora do tej komendy."

    if ctx.guild is None:
        return "Tej komendy można używać tylko na serwerze."

    if not args or not args.isdigit():
        return f"Pisz jak człowiek, np: {COMMAND_PREFIX}purge 20"

    try:
        amount = int(args)
        if amount > 100:
            return "Nie możesz usunąć więcej niż 100 wiadomości naraz, debilu."
        if amount < 1:
            return "Nie możesz usunąć mniej niż jednej wiadomości, debilu."
        await ctx.channel.purge(limit=amount + 1)
        return None
    except Exception as e:
        return f"Coś poszło nie tak: {e}"
