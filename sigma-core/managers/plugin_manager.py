import json
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "base_manager",
    Path.cwd() / "sigma-core/managers/base_manager.py"
)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

class PluginManager(base.BaseManager):

    def export(self, filename):
        data = self.database.load("plugins")
        Path(filename).write_text(
            json.dumps(data, indent=2),
            encoding="utf-8"
        )
