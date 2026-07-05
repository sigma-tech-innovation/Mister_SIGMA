#!/usr/bin/env python3
import sys
import platform
from pathlib import Path

SIGMA_VERSION = "0.1.0"

def cmd_version():
    print(f"Sigma CLI v{SIGMA_VERSION}")

def cmd_doctor():
    print("Σ Sigma Doctor")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print(f"Workspace: {Path.cwd()}")
    print("Status: OK")

def cmd_help():
    print("""
Σ Sigma CLI

Commands:
  version   Show Sigma CLI version
  doctor    Check Sigma environment
  help      Show help
""")

def main():
    if len(sys.argv) < 2:
        cmd_help()
        return

    cmd = sys.argv[1]

    if cmd == "version":
        cmd_version()
    elif cmd == "doctor":
        cmd_doctor()
    elif cmd == "help":
        cmd_help()
    else:
        print(f"Unknown command: {cmd}")
        cmd_help()

if __name__ == "__main__":
    main()
