import importlib.util
import json
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

    out = {}

    for db in [
        "projects",
        "nodes",
        "packages",
        "registry",
        "templates",
        "releases"
    ]:
        out[db] = e.database.load(db)

    target = ROOT / "sigma_export.json"

    target.write_text(
        json.dumps(out, indent=4),
        encoding="utf-8"
    )

    print("Export created:")
    print(target)
