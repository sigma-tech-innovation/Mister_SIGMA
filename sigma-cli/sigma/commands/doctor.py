import platform
import shutil
from pathlib import Path
from sigma.config import REGISTRY_PATH
from sigma.workspace import WORKSPACE_DIRS

def check(name, ok):
    status = "OK" if ok else "FAIL"
    print(f"{name:<20} {status}")

def run():
    root = Path.cwd()
    workspace = root / ".sigma-workspace"

    print("Σ Sigma Doctor")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print()

    check("Git", shutil.which("git") is not None)
    check("Python", True)
    check("Registry", REGISTRY_PATH.exists())

    for d in WORKSPACE_DIRS:
        check(f"Workspace/{d}", (workspace / d).exists())
