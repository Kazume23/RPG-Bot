from services.rolls import roll_logic
from services.dm_sender import send_admin_dm


async def ukryty_command(ctx, args: str):
    if not args:
        return "Ty chuju. Pisz jak człowiek np: 5d6"

    result = roll_logic(args)
    if not result.startswith("Wyniki rzutów:"):
        return result

    await send_admin_dm(ctx.bot, f"User {ctx.author} rolled: {args}\n{result}")
    return "Rzuciłeś ukryty rzut lampucero"
