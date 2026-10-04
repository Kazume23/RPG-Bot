import random
from commands.utility import command_usage
from services.data_manager import get_ochlapus_effects

ochlapus_copy = set(get_ochlapus_effects())


async def ochlapus_command(args: str):
    global ochlapus_copy

    if not args or not args.isdigit():
        return f"Użyj poprawnej składni: {command_usage('ochlapus <Odp>')}"

    user_value = int(args)
    if not 1 <= user_value <= 100:
        return "Wartość Odp musi mieścić się w zakresie 1–100."

    random_value = random.randint(1, 100)

    if user_value >= random_value:
        if not ochlapus_copy:
            ochlapus_copy = set(get_ochlapus_effects())
        effect = random.choice(list(ochlapus_copy))
        ochlapus_copy.remove(effect)
        return f"🎲 Wylosowana wartość: **{random_value}** (twoja: {user_value}) (Efekty: {len(ochlapus_copy)}) \n{effect}"

    return f"🎲 Wylosowana wartość: **{random_value}** (twoja: {user_value})\nTym razem udało ci się nie najebać"
