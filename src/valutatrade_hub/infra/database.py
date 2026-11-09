from valutatrade_hub.storage import load_json, save_json


class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, filename, default):
        return load_json(filename, default)

    def save(self, filename, data):
        save_json(filename, data)