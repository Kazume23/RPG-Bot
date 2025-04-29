# personalities.py
import json
import os


def load_personalities():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'personalities.json'))
    print(path)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
