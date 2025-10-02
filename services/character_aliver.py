import random
from services import data_manager


def format_identity(name: str, race: str, gender: str) -> list[str]:
    result = []
    result.append(f"Imię: {name}")
    result.append(f"Rasa: {race.capitalize()}")
    result.append(f"Płeć: {'Kobieta' if gender.lower() == 'f' else 'Mężczyzna'}")
    return result


def format_professions(current: str, previous: str) -> list[str]:
    result = []
    result.append(f"Obecna profesja: {current}")
    result.append(f"Poprzednia profesja: {previous}")
    return result


def format_appearance(appearance: dict) -> list[str]:
    result = []
    result.append(f"Wiek: {appearance['age']}")
    result.append(f"Kolor oczu: {appearance['eyes']}")
    result.append(f"Kolor włosów: {appearance['hair']}")
    result.append(f"Wzrost: {appearance['height']} cm")
    result.append(f"Waga: {appearance['weight']} kg")
    result.append(f"Znaki szczególne: {appearance['marks']}")
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


async def character_randomizer(race: str, gender: str):
    race_data = data_manager.get_race_data(race)
    name_data = data_manager.get_names(race, gender)
    stats_lines, rolled_stats = format_stats(race_data["stats"])
    substats_lines = format_substats(race_data["substats"], rolled_stats)

    appearance = {
        "age": random.choice(data_manager.get_looks(race, "age")),
        "eyes": random.choice(data_manager.get_looks(race, "eyes")),
        "hair": random.choice(data_manager.get_looks(race, "hair")),
        "marks": random.sample(data_manager.get_looks(race, "marks"), 3),
        "weight": random.choice(data_manager.get_looks(race, "weight")),
        "height": random.choice(data_manager.get_looks(race, "height", gender))
    }

    result = []
    result.extend(format_identity(random.choice(name_data), race, gender))
    result.extend(format_professions("Brak", "Brak"))
    result.extend(format_appearance(appearance))
    result.extend(stats_lines)
    result.extend(substats_lines)

    return "\n".join(result)
