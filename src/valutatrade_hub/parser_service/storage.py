import json
import os


def save_rates_atomic(filepath, data):
    """Безопасная запись: сначала во временный файл, потом переименование."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    temp_path = filepath + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    os.replace(temp_path, filepath)