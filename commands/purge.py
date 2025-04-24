from commands.utility import has_admin_permissions

async def purge_command(ctx, message):
    if not has_admin_permissions(ctx):
        return "Spierdalaj. Nie masz uprawnień administratora do tej komendy."

    parts = message.split()
    if len(parts) == 2 and parts[1].isdigit():
        try:
            amount = int(parts[1])
            if amount > 100:
                return "Nie możesz usunąć więcej niż 100 wiadomości naraz, debilu."
            await ctx.channel.purge(limit=amount + 1)
            return None
        except Exception as e:
            return f"Coś poszło nie tak: {e}"
    else:
        return "Pisz jak człowiek, np: >purge 20"
