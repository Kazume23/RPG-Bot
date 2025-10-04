from services.character_aliver import *
from commands.utility import has_admin_permissions


async def npc_command(ctx):
    if not has_admin_permissions(ctx):
        return "Spierdalaj. Nie masz nade mną władzy śmiertelniku"

    parts = ctx.content.split(maxsplit=3)

    if len(parts) < 4:
        return "Użyj poprawnej składni: `>npc [rasa] [płeć: m/f] [klasa]`"

    race = parts[1].lower()
    gender = parts[2].lower()
    char_class = parts[3].lower()

    return await character_randomizer(race, gender, char_class)
