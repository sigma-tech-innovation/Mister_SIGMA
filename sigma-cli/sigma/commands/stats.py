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
    print("         Σ SIGMA STATS")
    print("===================================")

    print("Databases :", len(e.database.list()))
    print("Projects  :", len(e.database.load("projects")))
    print("Nodes     :", len(e.database.load("nodes")))
    print("Packages  :", len(e.database.load("packages")))
    print("Registry  :", len(e.database.load("registry")))
    print("Templates :", len(e.database.load("templates")))
    print("Releases  :", len(e.database.load("releases")))

    print()

    print("Project folders :", len([
        p for p in e.projects_dir.iterdir()
        if p.is_dir()
    ]))
