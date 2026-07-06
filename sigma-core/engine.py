from pathlib import Path
from datetime import datetime
import json
import importlib.util

ROOT = Path.cwd()

spec = importlib.util.spec_from_file_location(
    "database_manager",
    ROOT / "sigma-core" / "managers" / "database_manager.py"
)

db_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(db_module)

class SigmaEngine:

    def __init__(self):
        self.root = ROOT
        self.db = self.root / "sigma-db"
        self.projects = self.root / "sigma-projects"

        self.database = db_module.DatabaseManager(self)

    def load_json(self, path):
        p = Path(path)

        if not p.exists():
            return []

        txt = p.read_text(encoding="utf-8").strip()

        if txt == "":
            return []

        return json.loads(txt)

    def save_json(self, path, data):
        Path(path).write_text(
            json.dumps(data, indent=4),
            encoding="utf-8"
        )

    def next_id(self, prefix, items):
        return f"{prefix}-{len(items)+1:04d}"

    def now(self):
        return datetime.now().isoformat()

engine = SigmaEngine()
