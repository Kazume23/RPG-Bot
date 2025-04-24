from static.umiejki import skills


async def umiejki_command(message):
    parts = message.split(maxsplit=1)

    if len(parts) == 1:
        return "Dostępne umiejętności: " + ", ".join(skills.keys())

    if len(parts) < 2:
        return "Użyj poprawnej składni: >u {nazwa_umiejętności}"

    skill_name = parts[1].lower()
    if skill_name in skills:
        return skills[skill_name]
    else:
        return "Naucz się kurwo szukać umiejek."
