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

    print("===================================")
    print("          Σ SIGMA INFO")
    print("===================================")

    print("Root       :", e.root)
    print("Database   :", e.db)
    print("Projects   :", e.projects_dir)
    print("Time       :", e.now())
    print("API        :", e.api.exists())
