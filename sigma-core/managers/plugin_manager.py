import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "base_manager",
    Path.cwd() / "sigma-core/managers/base_manager.py"
)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

class PluginManager(base.BaseManager):

    def validate(self, name):
        plugins = self.database.load("plugins")
        return any(
            p.get("name") == name and
            p.get("status") in ("enabled", "disabled")
            for p in plugins
        )
