from services.data_manager import load_json


def load_personalities():
    return load_json("personalities.json")
