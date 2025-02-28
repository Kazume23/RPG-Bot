import json
import os


class FileManager:
    def __init__(self, filename):
        if not os.path.exists('data'):
            os.makedirs('data')

        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                content = file.read().strip()
                if content:
                    return json.loads(content)
                else:
                    return {}
        else:
            return {}

    def save_data(self):
        with open(self.filename, 'w') as file:
            json.dump(self.data, file, indent=4)

    def add(self, input_data):
        # Rozdzielanie nazwy i opisu na podstawie "/"
        if '/' not in input_data:
            return "Błąd: Użyj '/' do oddzielenia nazwy i opisu."

        name, description = input_data.split('/', 1)  # Rozdziel na dwie części
        name = name.strip()
        description = description.strip()

        if name in self.data:
            return f"Element {name} już istnieje!"

        self.data[name] = description
        self.save_data()
        return f"Element {name} został dodany z opisem: {description}"

    def remove(self, input_data):
        # Rozdzielanie na podstawie "/"
        if '/' not in input_data:
            return "Błąd: Użyj '/' do podania nazwy."

        name = input_data.split('/', 1)[0].strip()

        if name not in self.data:
            return f"Nie znaleziono elementu {name}."

        del self.data[name]
        self.save_data()
        return f"Element {name} został usunięty."

    def change(self, input_data):
        # Rozdzielanie na podstawie "/"
        if '/' not in input_data:
            return "Błąd: Użyj '/' do podania nazwy i nowego opisu."

        name, new_description = input_data.split('/', 1)
        name = name.strip()
        new_description = new_description.strip()

        if name not in self.data:
            return f"Nie znaleziono elementu {name}."

        self.data[name] = new_description
        self.save_data()
        return f"Opis elementu {name} został zmieniony na: {new_description}"

    def display(self):
        if not self.data:
            return "Brak danych."
        return "\n".join([f"{name}: {desc}" for name, desc in self.data.items()])
