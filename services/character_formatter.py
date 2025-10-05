import random


def format_identity(name: str = None, race: str = None, gender: str = None, char_class: str = None) -> list[str]:
    result = []
    if name: result.append(f"Imię: {name}")
    if race: result.append(f"Rasa: {race.capitalize()}")
    if gender: result.append(f"Płeć: {'Kobieta' if gender.lower() == 'f' else 'Mężczyzna'}")
    if char_class: result.append(f"Obecna profesja: {char_class.capitalize()}")
    return result


def format_appearance(appearance: dict) -> list[str]:
    return [
        f"Wiek: {appearance['age']}",
        f"Kolor oczu: {appearance['eyes']}",
        f"Kolor włosów: {appearance['hair']}",
        f"Wzrost: {appearance['height']} cm",
        f"Waga: {appearance['weight']} kg",
        f"Znaki szczególne: {', '.join(appearance['marks'])}"
    ]


def format_stats(stats: dict) -> tuple[list[str], dict]:
    result, rolled = [], {}
    for stat, base in stats.items():
        if isinstance(base, list):
            base_value = random.choice(base)
        else:
            base_value = base
        roll = random.randint(2, 20)
        total = base_value + roll
        rolled[stat] = total
        result.append(f"{stat}: {total}")
    return result, rolled


def format_substats(substats: dict, rolled_stats: dict) -> list[str]:
    result = []
    for key, value in substats.items():
        if value == "S":
            total = rolled_stats["K"] // 10
        elif value == "Wt":
            total = rolled_stats["ODP"] // 10
        elif isinstance(value, list):
            total = random.choice(value)
        else:
            total = value
        result.append(f"{key}: {total}")
    return result


def format_skills(skills: list[str]) -> list[str]:
    result = ["Umiejętności:"]
    for skill in skills:
        result.append(f"- {skill}")
    return result


def format_abilities(abilities: list[str]) -> list[str]:
    result = ["Zdolności:"]
    for ability in abilities:
        result.append(f"- {ability}")
    return result


def format_equipment(equipment: list[str]) -> list[str]:
    result = ["Ekwipunek:"]
    for item in equipment:
        result.append(f"- {item}")
    return result
