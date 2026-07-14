from pathlib import Path

WORKSPACE_DIRS = [
    "projects",
    "registry",
    "logs",
    "backups",
    "configs",
    "cache",
    "temp"
]

def create_workspace(root: Path):
    for directory in WORKSPACE_DIRS:
        (root / directory).mkdir(parents=True, exist_ok=True)

def show_workspace(root: Path):
    print("Σ Sigma Workspace")
    for directory in WORKSPACE_DIRS:
        path = root / directory
        status = "OK" if path.exists() else "MISSING"
        print(f"- {directory}: {status}")
