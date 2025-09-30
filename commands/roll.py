from services.rolls import roll_logic


async def roll_command(message):
    parts = message.split(maxsplit=1)
    if len(parts) < 2:
        return "Ty chuju. Pisz jak człowiek np: 5d6"

    return roll_logic(parts[1])
