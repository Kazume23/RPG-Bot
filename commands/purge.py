from commands.utility import command_usage, has_admin_permissions


async def purge_command(ctx, args: str):
    if not has_admin_permissions(ctx):
        return "Nie masz uprawnień do tej komendy."

    if ctx.guild is None:
        return "Tej komendy można używać tylko na serwerze."

    if not args or not args.isdigit():
        return f"Użyj poprawnej składni: {command_usage('purge <1-100>')}"

    try:
        amount = int(args)
        if not 1 <= amount <= 100:
            return "Liczba wiadomości musi mieścić się w zakresie 1–100."
        await ctx.channel.purge(limit=amount + 1)
        return None
    except Exception as e:
        return f"Coś poszło nie tak: {e}"
