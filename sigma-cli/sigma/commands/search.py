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

    if len(args) == 0:
        print("Usage : sigma search <text>")
        return

    keyword = args[0].lower()

    e = engine_module.engine

    print("=== PROJECTS ===")

    for p in e.database.load("projects"):
        txt = str(p).lower()
        if keyword in txt:
            print("-", p)

    print()

    print("=== PACKAGES ===")

    for p in e.database.load("packages"):
        txt = str(p).lower()
        if keyword in txt:
            print("-", p)

    print()

    print("=== NODES ===")

    for p in e.database.load("nodes"):
        txt = str(p).lower()
        if keyword in txt:
            print("-", p)
