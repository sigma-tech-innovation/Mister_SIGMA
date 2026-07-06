from pathlib import Path
from datetime import datetime
import json

ROOT = Path.cwd()

class SigmaEngine:
    def __init__(self):
        self.root = ROOT
        self.db = self.root / "sigma-db"
        self.projects = self.root / "sigma-projects"

    def load_json(self, path):
        p = Path(path)
        if not p.exists() or p.read_text().strip() == "":
            return []
        return json.loads(p.read_text(encoding="utf-8"))

    def save_json(self, path, data):
        Path(path).write_text(json.dumps(data, indent=4), encoding="utf-8")

    def next_id(self, prefix, items):
        return f"{prefix}-{len(items)+1:04d}"

    def now(self):
        return datetime.now().isoformat()

engine = SigmaEngine()
