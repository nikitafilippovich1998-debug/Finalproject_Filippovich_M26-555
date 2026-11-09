import json
import os

DATA_DIR = "data"

def _get_path(filename):
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, filename)

def load_json(filename, default):
    path = _get_path(filename)
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except json.JSONDecodeError: return default

def save_json(filename, data):
    path = _get_path(filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)