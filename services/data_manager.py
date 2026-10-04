import json
from pathlib import Path
from typing import Any, Dict, List, Union

from config.settings import settings

DATA_DIR = settings.content_data_dir
_cache: Dict[Path, Any] = {}


def load_json(filename: str, subdir: str = None, use_cache: bool = True) -> Union[Dict, List]:
    path = DATA_DIR / subdir / filename if subdir else DATA_DIR / filename

    if use_cache and path in _cache:
        return _cache[path]

    if not path.exists():
        raise FileNotFoundError(f"Plik JSON nie istnieje: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if use_cache:
        _cache[path] = data

    return data


def get_race_data(race: str) -> Dict[str, Any]:
    data = load_json("rasy.json", subdir="characters")
    race_lower = race.lower()
    normalized = {key.lower(): value for key, value in data.items()}
    if race_lower not in normalized:
        raise KeyError(f"Nie znaleziono rasy: {race}")
    return normalized[race_lower]


def get_names(race: str, gender: str) -> List[str]:
    data = load_json("names.json", subdir="characters")
    race_lower = race.lower()
    gender_lower = gender.lower()
    normalized_races = {key.lower(): value for key, value in data.items()}
    if race_lower not in normalized_races:
        raise KeyError(f"Nie znaleziono rasy w names.json: {race}")
    race_data = normalized_races[race_lower]
    normalized_gender = {key.lower(): value for key, value in race_data.items()}
    if gender_lower not in normalized_gender:
        raise KeyError(f"Nie znaleziono płci {gender} dla rasy {race}")
    return normalized_gender[gender_lower]


def get_class_data(class_name: str) -> Dict[str, Any]:
    data = load_json("class.json", subdir="characters")
    class_lower = class_name.lower()
    normalized = {key.lower(): value for key, value in data.items()}
    if class_lower not in normalized:
        raise KeyError(f"Nie znaleziono klasy: {class_name}")
    return normalized[class_lower]


def get_skills() -> Dict[str, Any]:
    return load_json("skills.json", subdir="content")


def get_abilities() -> Dict[str, Any]:
    return load_json("abilities.json", subdir="content")


def get_ochlapus_effects() -> List[str]:
    data = load_json("ochlapus.json", subdir="content")
    effects = data.get("ochlapus", {})
    return [f"**{name.strip()}**\n{description.strip()}" for name, description in effects.items()]


def clear_cache() -> None:
    _cache.clear()
