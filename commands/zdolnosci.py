from services import data_manager


async def zdolnosci_command(args: str):
    abilities = data_manager.get_abilities()

    if not args:
        return "Dostępne zdolności:\n " + "\n".join(abilities.keys())

    ability_name = args.lower()
    normalized = {k.lower(): v for k, v in abilities.items()}

    if ability_name in normalized:
        ability = normalized[ability_name]
        return (
            f"**{ability['name']}**\n"
            f"Opis: {ability['desc']}\n"
            f"Efekt: {ability['effect']}"
        )
    else:
        return "Weź ty kurwa się naucz wpisywać dobrze te gówna."
