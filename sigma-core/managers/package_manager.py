import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "base_manager",
    Path.cwd() / "sigma-core/managers/base_manager.py"
)

base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

class PackageManager(base.BaseManager):

    def list(self):
        for pkg in self.database.load("packages"):
            print(
                f'{pkg["id"]} | {pkg["name"]} | {pkg["version"]}'
            )

    def next_id(self):
        db = self.database.load("packages")

        if not db:
            return "PKG-0001"

        last = max(
            int(x["id"].split("-")[1])
            for x in db
        )

        return f"PKG-{last+1:04d}"
