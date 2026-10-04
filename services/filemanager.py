import json
import os
from pathlib import Path
from typing import Optional

from config.settings import COMMAND_PREFIX, settings


class FileDataError(RuntimeError):
    pass


class FileManager:
    def __init__(self, filename, data_dir: Optional[Path] = None):
        base_dir = data_dir or settings.storage_dir
        self.filename = base_dir / f"{filename}.json"
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        if not self.filename.exists():
            with self.filename.open("w", encoding="utf-8") as file:
                json.dump([], file, ensure_ascii=False, indent=4)

    def _load_data(self):
        try:
            with self.filename.open("r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return [data]
                raise FileDataError(f"Plik {self.filename.name} ma nieobsługiwany format.")
        except json.JSONDecodeError as exc:
            raise FileDataError(
                f"Plik {self.filename.name} jest uszkodzony. Nie został nadpisany."
            ) from exc
        except FileNotFoundError as exc:
            raise FileDataError(f"Brakuje pliku {self.filename.name}.") from exc

    def _save_data(self, data):
        temp_path = self.filename.with_suffix(self.filename.suffix + ".tmp")
        try:
            with temp_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temp_path, self.filename)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def add(self, name, description):
        if not name or not description:
            return "Nazwa i opis nie mogą być puste."
        data = self._load_data()
        if any(item.get("name", "").casefold() == name.casefold() for item in data if isinstance(item, dict)):
            return f"Błąd: {name} już istnieje."
        data.append({"name": name, "description": description})
        self._save_data(data)
        return f"Dodano: {name}"

    def remove(self, name):
        data = self._load_data()
        new_data = [
            item for item in data
            if not isinstance(item, dict) or item.get("name", "").casefold() != name.casefold()
        ]

        if len(new_data) == len(data):
            return f"Błąd: {name} nie znaleziono."

        self._save_data(new_data)
        return f"Usunięto: {name}"

    def change(self, name, new_description):
        data = self._load_data()
        for item in data:
            if isinstance(item, dict) and item.get("name", "").casefold() == name.casefold():
                item["description"] = new_description
                self._save_data(data)
                return f"Zmieniono: {name}"

        return f"Błąd: {name} nie znaleziono."

    def display(self):
        data = self._load_data()
        filtered_data = [item for item in data if "name" in item and "description" in item]

        if not filtered_data:
            return "Brak zapisanych danych."

        return "\n".join([f"{i + 1}. {item['name']} - {item['description']}" for i, item in enumerate(filtered_data)])


async def handle_command(args: str, category: str):
    parts = args.split(maxsplit=1)

    if not parts:
        return f"Użyj poprawnej składni: `{COMMAND_PREFIX}{category} <dodaj/usun/zmien/daj> [parametry]`"

    command = parts[0].lower()
    manager = FileManager(category)

    try:
        if command == "dodaj":
            if len(parts) < 2:
                return f"Użyj poprawnej składni: `{COMMAND_PREFIX}{category} dodaj <nazwa> / <opis>`"

            input_data = parts[1]
            if "/" not in input_data:
                return "Błąd: użyj `/` do oddzielenia nazwy i opisu."

            name, description = input_data.split("/", 1)
            return manager.add(name.strip(), description.strip())

        if command == "usun":
            if len(parts) < 2:
                return f"Użyj poprawnej składni: `{COMMAND_PREFIX}{category} usun <nazwa>`"

            return manager.remove(parts[1].strip())

        if command == "zmien":
            if len(parts) < 2:
                return f"Użyj poprawnej składni: `{COMMAND_PREFIX}{category} zmien <nazwa> / <nowy opis>`"

            input_data = parts[1]
            if "/" not in input_data:
                return "Błąd: użyj `/` do oddzielenia nazwy i nowego opisu."

            name, new_description = input_data.split("/", 1)
            return manager.change(name.strip(), new_description.strip())

        if command == "daj":
            return manager.display()

        return "Nieznana akcja. Użyj: dodaj, usun, zmien, daj."
    except FileDataError as exc:
        return f"Błąd danych: {exc}"
