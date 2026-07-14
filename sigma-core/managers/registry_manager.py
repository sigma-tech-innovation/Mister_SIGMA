import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "base_manager",
    Path.cwd() / "sigma-core/managers/base_manager.py"
)

base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

class RegistryManager(base.BaseManager):

    def list(self):
        registry = self.database.load("registry")

        for reg in registry:
            print(
                f'{reg["id"]} | {reg["name"]} | {reg["version"]}'
            )

        return registry

    def next_id(self):
        db = self.database.load("registry")

        if not db:
            return "REG-0001"

        last = max(
            int(x["id"].split("-")[1])
            for x in db
        )

        return f"REG-{last+1:04d}"

    def get(self, registry_id):
        for reg in self.database.load("registry"):
            if reg.get("id") == registry_id:
                return reg
        return None

    def exists(self, registry_id):
        return self.get(registry_id) is not None

    def count(self):
        return len(self.database.load("registry"))
