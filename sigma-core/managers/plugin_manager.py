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

    def import_file(self, filename):
        data = json.loads(Path(filename).read_text(encoding="utf-8"))
        self.database.save("plugins", data)
