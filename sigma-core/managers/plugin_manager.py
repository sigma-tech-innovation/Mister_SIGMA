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

    def list(self):
        for plugin in self.db():
            print(
                f'{plugin["id"]} | {plugin["name"]} | {plugin["version"]} | {plugin["status"]}'
            )

    def next_id(self):
        db = self.db()

        if not db:
            return "PLG-0001"

        last = max(
            int(x["id"].split("-")[1])
            for x in db
        )

        return f"PLG-{last+1:04d}"
