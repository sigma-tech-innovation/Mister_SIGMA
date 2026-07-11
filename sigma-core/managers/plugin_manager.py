import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "base_manager",
    Path.cwd() / "sigma-core/managers/base_manager.py"
)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

class PluginManager(base.BaseManager):

    def discover(self):
        root = Path("sigma-plugins")

        if not root.exists():
            return []

        return sorted(
            p.name
            for p in root.iterdir()
            if p.is_dir() and (p / "__init__.py").exists()
        )
