from services.rolls import roll_logic
from services.dm_sender import send_admin_dm


async def ukryty_command(message, ctx):
    parts = message.split(maxsplit=1)
    if len(parts) < 2:
        return "Ty chuju. Pisz jak człowiek np: 5d6"

    print(ctx)
    print(type(ctx))

    result = roll_logic(parts[1])
    await send_admin_dm(ctx.bot, f"User {ctx.author} rolled: {parts[1]}\n{result}")
