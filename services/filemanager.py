import json
import os


class FileManager:
    def __init__(self, filename):
        self.filename = f"data/{filename}.json"
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filename):
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump([], file, ensure_ascii=False, indent=4)

    def _load_data(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return [data]
                else:
                    return []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_data(self, data):
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def add(self, name, description):
        data = self._load_data()
        data.append({"name": name, "description": description})
        self._save_data(data)
        return f"Dodano: {name}"

    def remove(self, name):
        data = self._load_data()
        new_data = [item for item in data if item["name"] != name]

        if len(new_data) == len(data):
            return f"Błąd: {name} nie znaleziono."

        self._save_data(new_data)
        return f"Usunięto: {name}"

    def change(self, name, new_description):
        data = self._load_data()
        for item in data:
            if item["name"] == name:
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


async def handle_command(message, ctx, category):
    parts = message.split(maxsplit=2)

    if len(parts) < 2:
        return f"Użyj poprawnej składni: >{category} {{dodaj/usun/zmien/daj}} [parametry]"

    command = parts[1].lower()
    manager = FileManager(category)

    if command == "dodaj":
        if len(parts) < 3:
            return f"Użyj poprawnej składni: >{category} dodaj {{nazwa}} / {{opis}}"

        input_data = parts[2]
        if "/" not in input_data:
            return "Błąd: Użyj '/' do oddzielenia nazwy i opisu."

        name, description = input_data.split("/", 1)
        return manager.add(name.strip(), description.strip())

    elif command == "usun":
        if len(parts) < 3:
            return f"Użyj poprawnej składni: >{category} usun {{nazwa}}"

        return manager.remove(parts[2].strip())

    elif command == "zmien":
        if len(parts) < 3:
            return f"Użyj poprawnej składni: >{category} zmien {{nazwa}} / {{nowy opis}}"

        input_data = parts[2]
        if "/" not in input_data:
            return "Błąd: Użyj '/' do oddzielenia nazwy i nowego opisu."

        name, new_description = input_data.split("/", 1)
        return manager.change(name.strip(), new_description.strip())

    elif command == "daj":
        return manager.display()

    else:
        return "Nieznana akcja. Użyj: dodaj, usun, zmien, daj."
