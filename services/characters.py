import json


def load_characters():
    with open('data/postacie.json', 'r', encoding='utf-8') as file:
        return json.load(file)


def display_character_stats(character_name, characters, username=None):
    character = characters.get(character_name.lower())
    if not character:
        return f"Postać {character_name} nie istnieje."

    response = f"Statystyki postaci {character_name}:\n"
    for key, value in character.items():
        if key != 'statystyki' and key != 'punkty':
            response += f"{key}: {value}\n"
        elif key == 'statystyki':
            response += "Statystyki:\n"
            for stat, stat_value in value.items():
                response += f"  {stat}: {stat_value}\n"
        elif key == 'punkty':
            response += "Punkty:\n"
            for point, point_value in value.items():
                response += f"  {point}: {point_value}\n"

    return response


def edit_character_stats(character_name, field, new_value, admin=False, characters=None):
    if not admin:
        return "Brak uprawnień do edytowania statystyk!"

    character = characters.get(character_name.lower())
    if not character:
        return f"Postać {character_name} nie istnieje."

    if field in character['statystyki']:
        character['statystyki'][field] = new_value
    elif field in character['punkty']:
        character['punkty'][field] = new_value
    else:
        return f"Niepoprawne pole: {field}"

    # Zapisz zmiany do pliku JSON
    with open('characters_data.json', 'w') as file:
        json.dump(characters, file, indent=4)

    return f"Statystyki postaci {character_name} zostały zaktualizowane."
