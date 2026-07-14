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
        print("Usage : sigma show <database>")
        return

    e = engine_module.engine

    db = args[0]

    try:
        data = e.database.load(db)

        print(f"=== {db.upper()} ===")

        for item in data:
            print(item)

    except Exception:
        print("Unknown database :", db)
