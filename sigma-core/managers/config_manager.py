import uuid
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


    def ensure_identity(self):
        cfg = self.load()

        changed = False

        for key in ("machine_id", "user_id", "node_id"):
            if key not in cfg:
                cfg[key] = str(uuid.uuid4())
                changed = True

        if changed:
            self.save(cfg)

        return cfg
