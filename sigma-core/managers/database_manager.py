import json
from pathlib import Path

class DatabaseManager:

    def __init__(self, engine):
        self.engine = engine

    def path(self, name):
        return self.engine.db / f"{name}.json"

    def load(self, name):
        p = self.path(name)

        if not p.exists():
            return []

        txt = p.read_text(encoding="utf-8").strip()

        if txt == "":
            return []

        return json.loads(txt)

    def save(self, name, data):
        self.path(name).write_text(
            json.dumps(data, indent=4),
            encoding="utf-8"
        )

    def list(self):
        return sorted(
            p.stem
            for p in self.engine.db.glob("*.json")
        )
