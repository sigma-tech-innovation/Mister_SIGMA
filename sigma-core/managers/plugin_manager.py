import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "base_manager",
    Path.cwd() / "sigma-core/managers/base_manager.py"
)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

class PluginManager(base.BaseManager):

    def db(self):
        return self.database.load("plugins")

    def save(self, data):
        self.database.save("plugins", data)

    def rename(self, old_name, new_name):
        db = self.db()
        for p in db:
            if p["name"] == old_name:
                p["name"] = new_name
        self.save(db)
