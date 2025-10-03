from services.rolls import roll_logic


async def roll_command(args: str):
    if not args:
        return "Ty chuju. Pisz jak człowiek np: 5d6"

    return roll_logic(args)
