from pathlib import Path


class ConfigManager:

    def __init__(self, engine):
        self.engine = engine
        self.path = engine.root / "sigma-config.json"

    def exists(self):
        return self.path.exists()

    def load(self):
        if not self.exists():
            return {}
        return self.engine.load_json(self.path)

    def save(self, data):
        self.engine.save_json(self.path, data)

    def get(self, key, default=None):
        return self.load().get(key, default)

    def set(self, key, value):
        cfg = self.load()
        cfg[key] = value
        self.save(cfg)
