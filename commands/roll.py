from services.rolls import roll_logic
from commands.utility import command_usage


async def roll_command(args: str):
    if not args:
        return f"Użyj poprawnej składni, np. {command_usage('roll 5d6')}"

    return roll_logic(args)
