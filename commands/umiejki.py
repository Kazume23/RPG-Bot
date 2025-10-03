from services import data_manager


async def umiejki_command(args: str):
    skills = data_manager.get_skills()

    if not args:
        return "Dostępne umiejętności: " + ", ".join(skills.keys())

    skill_name = args.lower()
    normalized = {k.lower(): v for k, v in skills.items()}

    if skill_name in normalized:
        return normalized[skill_name]
    else:
        return "Naucz się kurwo szukać umiejek."
