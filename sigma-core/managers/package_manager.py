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

    def get(self, package_id):
        for package in self.database.load("packages"):
            if package.get("id") == package_id:
                return package
        return None

    def exists(self, package_id):
        return self.get(package_id) is not None

    def count(self):
        return len(self.database.load("packages"))
