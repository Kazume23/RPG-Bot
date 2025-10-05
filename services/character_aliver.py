import random
from services import data_manager


def format_identity(name: str, race: str, gender: str, char_class: str) -> list[str]:
    result = []
    result.append(f"Imię: {name}")
    result.append(f"Rasa: {race.capitalize()}")
    result.append(f"Płeć: {'Kobieta' if gender.lower() == 'f' else 'Mężczyzna'}")
    result.append(f"Obecna profesja: {char_class.capitalize()}")
    return result


def format_appearance(appearance: dict) -> list[str]:
    result = []
    result.append(f"Wiek: {appearance['age']}")
    result.append(f"Kolor oczu: {appearance['eyes']}")
    result.append(f"Kolor włosów: {appearance['hair']}")
    result.append(f"Wzrost: {appearance['height']} cm")
    result.append(f"Waga: {appearance['weight']} kg")
    result.append(f"Znaki szczególne: {', '.join(appearance['marks'])}")
    return result


def format_skills(skills: list[str]) -> list[str]:
    result = []
    result.append("Umiejętności:")
    for skill in skills:
        result.append(f"- {skill}")
    return result


def format_abilities(abilities: list[str]) -> list[str]:
    result = []
    result.append("Zdolności:")
    for ability in abilities:
        result.append(f"- {ability}")
    return result


def format_stats(stats: dict) -> tuple[list[str], dict]:
    result = []
    rolled = {}

    for stat, base in stats.items():
        roll = random.randint(2, 20)  # 2k10
        total = base + roll
        rolled[stat] = total
        result.append(f"{stat}: {total}")

    return result, rolled


def format_substats(substats: dict, rolled_stats: dict) -> list[str]:
    result = []

    for key, value in substats.items():
        if value == "S":
            total = rolled_stats["K"] // 10
            result.append(f"{key}: {total}")
        elif value == "Wt":
            total = rolled_stats["ODP"] // 10
            result.append(f"{key}: {total}")
        elif isinstance(value, list):
            chosen = random.choice(value)
            result.append(f"{key}: {chosen}")
        else:
            result.append(f"{key}: {value}")

    return result


import random
from services import data_manager


def apply_class(race_data: dict, class_data: dict) -> dict:
    merged = race_data.copy()

    merged_stats = {}
    for stat in race_data["stats"]:
        race_val = race_data["stats"][stat]
        class_val = class_data["stats"].get(stat, [0])

        if isinstance(class_val, list):
            chosen = random.choice(class_val)
        else:
            chosen = class_val

        merged_stats[stat] = race_val + chosen
    merged["stats"] = merged_stats

    merged_substats = {}
    for sub in race_data["substats"]:
        race_val = race_data["substats"][sub]
        class_val = class_data["substats"].get(sub, [0])

        if isinstance(race_val, list) and isinstance(class_val, list):
            race_roll = random.choice(race_val)
            class_roll = random.choice(class_val)
            merged_substats[sub] = race_roll + class_roll

        elif isinstance(race_val, list):
            race_roll = random.choice(race_val)
            merged_substats[sub] = race_roll + (class_val if isinstance(class_val, int) else random.choice(class_val))

        elif isinstance(race_val, int):
            chosen = random.choice(class_val) if isinstance(class_val, list) else class_val
            merged_substats[sub] = race_val + chosen
        else:
            merged_substats[sub] = race_val
    merged["substats"] = merged_substats

    skills_final = []
    for skill in class_data.get("skills", []):
        if isinstance(skill, list):
            skills_final.append(random.choice(skill))
        else:
            skills_final.append(skill)
    merged["skills"] = race_data.get("skills", []) + skills_final

    abilities_final = []
    for ability in class_data.get("abilities", []):
        if isinstance(ability, list):
            abilities_final.append(random.choice(ability))
        else:
            abilities_final.append(ability)
    merged["abilities"] = race_data.get("abilities", []) + abilities_final

    merged["equipment"] = race_data.get("equipment", []) + class_data.get("equipment", [])

    return merged


async def character_randomizer(race: str, gender: str, char_class: str):
    race_data = data_manager.get_race_data(race)
    class_data = data_manager.get_class_data(char_class)
    name_data = data_manager.get_names(race, gender)

    character = apply_class(race_data, class_data)

    stats_lines, rolled_stats = format_stats(character["stats"])
    substats_lines = format_substats(character["substats"], rolled_stats)
    skills = character.get("skills", [])
    abilities = character.get("abilities", [])
    looks = character["looks"]

    appearance = {
        "age": random.choice(looks["age"]),
        "eyes": random.choice(looks["eyes"]),
        "hair": random.choice(looks["hair"]),
        "marks": random.sample(looks["marks"], 3),
        "weight": random.choice(looks["weight"]),
        "height": random.choice(looks["height"][gender.lower()])
    }

    result = []
    result.extend(format_identity(random.choice(name_data), race, gender, char_class))
    result.append("")
    result.extend(format_appearance(appearance))
    result.append("")
    result.extend(stats_lines)
    result.append("")
    result.extend(substats_lines)
    result.append("")
    result.extend(format_skills(skills))
    result.append("")
    result.extend(format_abilities(abilities))
    result.append("")
    result.append("Ekwipunek:")
    for item in character.get("equipment", []):
        result.append(f"- {item}")

    return "\n".join(result)
