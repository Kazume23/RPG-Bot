from services import data_manager
from services.character_formatter import (
    format_stats, format_substats, format_skills,
    format_abilities, format_equipment
)


async def show_all_classes():
    data = data_manager.load_json("class.json", subdir="characters")
    return "Dostępne klasy: " + ", ".join(data.keys())


async def show_class_info(class_name: str):
    data = data_manager.get_class_data(class_name)
    result = [f"Obecna profesja: {class_name.capitalize()}", ""]

    stats_lines = []
    for stat, values in data["stats"].items():
        val = max(values) if isinstance(values, list) else values
        stats_lines.append(f"{stat}: {val}")
    result.extend(stats_lines)
    result.append("")

    substats_lines = []
    for sub, values in data["substats"].items():
        val = max(values) if isinstance(values, list) else values
        substats_lines.append(f"{sub}: {val}")
    result.extend(substats_lines)
    result.append("")

    result.extend(format_skills([s if isinstance(s, str) else "/".join(s) for s in data["skills"]]))
    result.append("")
    result.extend(format_abilities([a if isinstance(a, str) else "/".join(a) for a in data["abilities"]]))
    result.append("")
    result.extend(format_equipment(data["equipment"]))

    return "\n".join(result)
