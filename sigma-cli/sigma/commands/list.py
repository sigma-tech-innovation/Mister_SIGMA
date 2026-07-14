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

    print("=== PROJECTS ===")
    e.projects.list()

    print()
    print("=== NODES ===")
    e.nodes.list()

    print()
    print("=== PACKAGES ===")
    e.packages.list()

    print()
    print("=== REGISTRY ===")
    e.registry.list()

    print()
    print("=== TEMPLATES ===")
    e.templates.list()

    print()
    print("=== RELEASES ===")
    e.releases.list()
