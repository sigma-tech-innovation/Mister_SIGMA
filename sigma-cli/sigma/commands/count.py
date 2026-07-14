import importlib.util
from pathlib import Path

ROOT = Path.cwd()

spec = importlib.util.spec_from_file_location(
    "engine",
    ROOT / "sigma-core/engine.py"
)

engine_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine_module)

def run(args):

    e = engine_module.engine

    names = [
        "projects",
        "nodes",
        "packages",
        "registry",
        "templates",
        "releases"
    ]

    print("========== COUNTS ==========")

    for name in names:
        print(f"{name:12}", len(e.database.load(name)))
