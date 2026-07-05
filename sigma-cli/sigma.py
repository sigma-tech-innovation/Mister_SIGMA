#!/usr/bin/env python3
import json
import platform
import sys
from pathlib import Path

SIGMA_VERSION = "0.3.0"
REGISTRY = Path("sigma-core/registry/registry.json")

def load_registry():
    if not REGISTRY.exists():
        print("Registry not found.")
        sys.exit(1)
    return json.loads(REGISTRY.read_text(encoding="utf-8"))

def cmd_version():
    print(f"Sigma CLI v{SIGMA_VERSION}")

def cmd_doctor():
    print("Σ Sigma Doctor")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print(f"Workspace: {Path.cwd()}")
    print("Status: OK")

def registry_list():
    data = load_registry()
    print(f"Σ Sigma Registry v{data['version']}")
    for obj in data["objects"]:
        print(f"- {obj['id']} | {obj['name']} | {obj['type']} | {obj['status']}")

def registry_show(object_id):
    data = load_registry()
    for obj in data["objects"]:
        if obj["id"] == object_id:
            print(f"ID     : {obj['id']}")
            print(f"Name   : {obj['name']}")
            print(f"Type   : {obj['type']}")
            print(f"Status : {obj['status']}")
            return
    print(f"Object not found: {object_id}")

def cmd_registry(args):
    if not args or args[0] == "list":
        registry_list()
    elif args[0] == "show":
        if len(args) < 2:
            print("Usage: sigma registry show <ID>")
            return
        registry_show(args[1])
    else:
        print("Usage: sigma registry [list|show <ID>]")

def cmd_help():
    print("""
Σ Sigma CLI

Commands:
  version
  doctor
  registry list
  registry show <ID>
  help
""")

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    args = sys.argv[2:]

    if cmd == "version":
        cmd_version()
    elif cmd == "doctor":
        cmd_doctor()
    elif cmd == "registry":
        cmd_registry(args)
    elif cmd == "help":
        cmd_help()
    else:
        print(f"Unknown command: {cmd}")
        cmd_help()

if __name__ == "__main__":
    main()
