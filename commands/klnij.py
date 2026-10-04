import random

from static import wyzwiska

klnij_copy = set(wyzwiska.przeklenstwa_ogolne)


async def klnij_command():
    global klnij_copy
    if not klnij_copy:
        klnij_copy = set(wyzwiska.przeklenstwa_ogolne)

    insult = random.choice(list(klnij_copy))
    klnij_copy.remove(insult)

    return f"{insult} \nPozostało: {len(klnij_copy)}"
