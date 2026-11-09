class SettingsLoader:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._settings = {
                "data_dir": "data",
                "rates_ttl_seconds": 300,
                "log_format": "text",
                "log_level": "INFO"
            }
        return cls._instance

    def get(self, key: str, default=None):
        return self._settings.get(key, default)