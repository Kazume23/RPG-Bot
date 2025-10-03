from services import data_manager


async def umiejki_command(args: str):
    skills = data_manager.get_skills()

    if not args:
        return "Dostępne umiejętności: \n" + "\n".join(skills.keys())

    skill_name = args.lower()
    normalized = {k.lower(): v for k, v in skills.items()}

    if skill_name in normalized:
        skill = normalized[skill_name]
        return (
            f"**{skill['name']}**\n"
            f"Opis: {skill['desc']}\n"
            f"Test: {skill['test']}"
        )
    else:
        return "Naucz się kurwo szukać umiejek."
