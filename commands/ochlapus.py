import random
from static.umiejki import ochlapus

ochlapus_copy = set(ochlapus)


async def ochlapus_command(message):
    global ochlapus_copy

    parts = message.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return "Użyj poprawnej składni: `>ochlapus X`, gdzie X to liczba Odp"

    user_value = int(parts[1])
    random_value = random.randint(1, 100)

    if not ochlapus_copy:
        ochlapus_copy = set(ochlapus)

    effect = random.choice(list(ochlapus_copy))
    ochlapus_copy.remove(effect)

    if user_value >= random_value:
        return f"🎲 Wylosowana wartość: **{random_value}** (twoja: {user_value}) (Efekty: {len(ochlapus_copy)}) \n{effect}"
    else:
        return f"🎲 Wylosowana wartość: **{random_value}** (twoja: {user_value})\nTym razem udało ci się nie najebać"
