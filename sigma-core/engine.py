from pathlib import Path
from datetime import datetime
import json
import importlib.util

ROOT = Path.cwd()

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

DatabaseModule = load_module(
    "database_manager",
    ROOT / "sigma-core/managers/database_manager.py"
)

ProjectModule = load_module(
    "project_manager",
    ROOT / "sigma-core/managers/project_manager.py"
)

class SigmaEngine:

    def __init__(self):

        self.root = ROOT
        self.db = self.root / "sigma-db"
        self.projects_dir = self.root / "sigma-projects"

        self.database = DatabaseModule.DatabaseManager(self)
        self.projects = ProjectModule.ProjectManager(self)

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

    def now(self):
        return datetime.now().isoformat()

engine = SigmaEngine()
