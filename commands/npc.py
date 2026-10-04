from commands.utility import command_usage, has_admin_permissions
from services.character_aliver import character_randomizer


async def npc_command(ctx, args: str):
    if not has_admin_permissions(ctx):
        return "Nie masz uprawnień do tej komendy."

    parts = args.split(maxsplit=2)

    if len(parts) != 3:
        return f"Użyj poprawnej składni: {command_usage('npc <rasa> <m/f> <klasa>')}"

    race, gender, char_class = (part.strip().lower() for part in parts)
    if gender not in {"m", "f"}:
        return "Płeć musi mieć wartość `m` albo `f`."

    try:
        return await character_randomizer(race, gender, char_class)
    except KeyError as exc:
        return str(exc.args[0])
