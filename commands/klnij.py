import random

from static import wyzwiska

klnij_copy = set(wyzwiska.przeklenstwa_ogolne)


async def klnij_command():
    global klnij_copy
    if not klnij_copy:
        klnij_copy = set(wyzwiska.przeklenstwa_ogolne)

    effect = random.choice(list(klnij_copy))
    klnij_copy.remove(effect)

    return f"{wyzwiska.losuj_przeklenstwo()} \nPozostało: {len(klnij_copy)}"
