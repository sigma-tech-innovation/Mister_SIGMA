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

    ok = True

    for db in [
        "projects",
        "nodes",
        "packages",
        "registry",
        "templates",
        "releases"
    ]:
        try:
            data = e.database.load(db)
            print(f"[OK] {db}: {len(data)}")
        except Exception as ex:
            ok = False
            print(f"[ERROR] {db}: {ex}")

    if ok:
        print("\nSIGMA verification passed.")
    else:
        print("\nSIGMA verification failed.")
