from commands.utility import has_admin_permissions


async def purge_command(ctx, args: str):
    if not has_admin_permissions(ctx):
        return "Spierdalaj. Nie masz uprawnień administratora do tej komendy."

    if not args or not args.isdigit():
        return "Pisz jak człowiek, np: >purge 20"

    try:
        amount = int(args)
        if amount > 100:
            return "Nie możesz usunąć więcej niż 100 wiadomości naraz, debilu."
        await ctx.channel.purge(limit=amount + 1)
        return None
    except Exception as e:
        return f"Coś poszło nie tak: {e}"
