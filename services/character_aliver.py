import random
import json
import os

file_path = os.path.join("data", "rasy.json")


async def character_randomizer(message):
    with open(file_path, "r", encoding="utf-8") as f:
        load = json.load(f)

    data = load[message]
    result = []
    for stat, value in data["stats"].items():
        roll = random.randint(2, 20)  # 2k10
        total = value + roll
        print(f"{stat} {total}")
        result.append(f"{stat} {total}")

    return "\n".join(result)
