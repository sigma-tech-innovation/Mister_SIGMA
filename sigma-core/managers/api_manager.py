import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "base_manager",
    Path.cwd() / "sigma-core/managers/base_manager.py"
)

base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

class ApiManager(base.BaseManager):

    def endpoints(self):
        api = self.root / "sigma-api"

        for p in sorted(api.glob("*.py")):
            if p.name != "__init__.py":
                print("-", p.stem)

    def exists(self):
        return (self.root / "sigma-api").exists()

    def info(self):
        print("API Root :", self.root / "sigma-api")
        print("Available :", self.exists())
