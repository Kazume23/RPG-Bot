from services.rolls import roll_logic
from services.dm_sender import send_admin_dm
from commands.utility import command_usage


async def ukryty_command(ctx, args: str):
    if not args:
        return f"Użyj poprawnej składni, np. {command_usage('ukryty 5d6')}"

    result = roll_logic(args)
    if result.startswith("Niepoprawny rzut"):
        return result

    await send_admin_dm(ctx.bot, f"User {ctx.author} rolled: {args}\n{result}")
    return "Rzut został wysłany do MG."
