import random
from services import data_manager
from services.character_formatter import (
    format_identity, format_appearance, format_stats, format_substats,
    format_skills, format_abilities, format_equipment
)


def apply_class(race_data: dict, class_data: dict) -> dict:
    merged = race_data.copy()

    merged_stats = {}
    for stat in race_data["stats"]:
        race_val = race_data["stats"][stat]
        class_val = class_data["stats"].get(stat, [0])
        chosen = random.choice(class_val) if isinstance(class_val, list) else class_val
        merged_stats[stat] = race_val + chosen
    merged["stats"] = merged_stats

    merged_substats = {}
    for sub in race_data["substats"]:
        race_val = race_data["substats"][sub]
        class_val = class_data["substats"].get(sub, [0])
        if isinstance(race_val, list):
            race_roll = random.choice(race_val)
            class_roll = random.choice(class_val) if isinstance(class_val, list) else class_val
            merged_substats[sub] = race_roll + class_roll
        elif isinstance(race_val, int):
            class_roll = random.choice(class_val) if isinstance(class_val, list) else class_val
            merged_substats[sub] = race_val + class_roll
        else:
            merged_substats[sub] = race_val
    merged["substats"] = merged_substats

    skills_final = [random.choice(skill) if isinstance(skill, list) else skill for skill in class_data.get("skills", [])]
    merged["skills"] = race_data.get("skills", []) + skills_final

    abilities_final = [random.choice(ability) if isinstance(ability, list) else ability for ability in class_data.get("abilities", [])]
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
    result.extend(format_equipment(character.get("equipment", [])))

    return "\n".join(result)
