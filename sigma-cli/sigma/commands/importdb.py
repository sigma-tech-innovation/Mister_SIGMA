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

    file = ROOT / "sigma_export.json"

    if not file.exists():
        print("sigma_export.json not found.")
        return

    data = json.loads(file.read_text())

    e = engine_module.engine

    for db, values in data.items():
        e.database.save(db, values)

    print("Import completed.")
