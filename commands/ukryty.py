from services.rolls import roll_logic
from services.dm_sender import send_admin_dm


async def ukryty_command(ctx):
    parts = ctx.content.split(maxsplit=1)
    if len(parts) < 2:
        return "Ty chuju. Pisz jak człowiek np: 5d6"

    result = roll_logic(parts[1])
    await send_admin_dm(ctx.bot, f"User {ctx.author} rolled: {parts[1]}\n{result}")
    return f"Rzuciłeś ukryty rzut lampucero"
