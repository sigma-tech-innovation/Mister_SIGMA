#!/usr/bin/env python3
import json
import platform
import sys
from pathlib import Path

SIGMA_VERSION = "0.2.0"
REGISTRY = Path("sigma-core/registry/registry.json")

def cmd_version():
    print(f"Sigma CLI v{SIGMA_VERSION}")

def cmd_doctor():
    print("Σ Sigma Doctor")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print(f"Workspace: {Path.cwd()}")
    print("Status: OK")

def cmd_registry():
    if not REGISTRY.exists():
        print("Registry not found.")
        return
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    print(f"Σ Sigma Registry v{data['version']}")
    for obj in data["objects"]:
        print(f"- {obj['id']} | {obj['name']} | {obj['type']} | {obj['status']}")

def cmd_help():
    print("""
Σ Sigma CLI

Commands:
  version
  doctor
  registry
  help
""")

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "version":
        cmd_version()
    elif cmd == "doctor":
        cmd_doctor()
    elif cmd == "registry":
        cmd_registry()
    elif cmd == "help":
        cmd_help()
    else:
        print(f"Unknown command: {cmd}")
        cmd_help()

if __name__ == "__main__":
    main()
