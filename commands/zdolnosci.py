from static.umiejki import abilities


async def zdolnosci_command(message):
    parts = message.split(maxsplit=1)

    if len(parts) == 1:
        return "Dostępne zdolności: " + ", ".join(abilities.keys())

    if len(parts) < 2:
        return "Użyj poprawnej składni: >z {nazwa_zdolności}"

    ability_name = parts[1].lower()
    if ability_name in abilities:
        return abilities[ability_name]
    else:
        return "Weź ty kurwa się naucz wpisywać dobrze te gówna."
