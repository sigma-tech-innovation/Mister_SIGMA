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
        packages = self.database.load("packages")

        for pkg in packages:
            print(
                f'{pkg["id"]} | {pkg["name"]} | {pkg["version"]}'
            )

        return packages

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

    def create(self, package):
        db = self.database.load("packages")

        if "id" not in package:
            package["id"] = self.next_id()

        db.append(package)
        self.database.save("packages", db)
        return package

    def update(self, package_id, **fields):
        db = self.database.load("packages")

        for package in db:
            if package.get("id") == package_id:
                package.update(fields)
                self.database.save("packages", db)
                return package

        return None

    def delete(self, package_id):
        db = self.database.load("packages")
        new_db = [p for p in db if p.get("id") != package_id]

        if len(new_db) == len(db):
            return False

        self.database.save("packages", new_db)
        return True

    def count(self):
        return len(self.database.load("packages"))
