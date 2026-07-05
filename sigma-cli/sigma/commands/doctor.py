import platform
from pathlib import Path

def run():
    print("Σ Sigma Doctor")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print(f"Workspace: {Path.cwd()}")
    print("Status: OK")
