import importlib.util
from pathlib import Path

ROOT = Path.cwd()

spec = importlib.util.spec_from_file_location(
    "engine",
    ROOT / "sigma-core/engine.py"
)

engine_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine_module)

def check(path):
    return "OK" if path.exists() else "MISSING"

def run(args):

    e = engine_module.engine

    print("===================================")
    print("        Σ SIGMA HEALTH")
    print("===================================")

    print("sigma-core      :", check(ROOT / "sigma-core"))
    print("sigma-cli       :", check(ROOT / "sigma-cli"))
    print("sigma-db        :", check(ROOT / "sigma-db"))
    print("sigma-projects  :", check(ROOT / "sigma-projects"))
    print("sigma-api       :", check(ROOT / "sigma-api"))
    print("roadmap         :", check(ROOT / "roadmap"))
    print("releases        :", check(ROOT / "releases"))
