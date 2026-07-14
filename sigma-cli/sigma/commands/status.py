from sigma.config import get_config
from sigma.node import get_node
from sigma.workspace import WORKSPACE_DIRS
from pathlib import Path

def run(args):

    cfg = get_config()
    node = get_node()

    print("===================================")
    print("        Σ SIGMA STATUS")
    print("===================================")

    print(f"Version    : {cfg['version']}")
    print(f"Hostname   : {node['hostname']}")
    print(f"OS         : {node['system']} {node['release']}")
    print(f"Workspace  : {cfg['root']}")
    print()

    print("Workspace status:")

    root = Path(cfg["root"]) / ".sigma-workspace"

    for d in WORKSPACE_DIRS:
        state = "OK" if (root / d).exists() else "MISSING"
        print(f"  {d:<12} {state}")

    print()

    print("Registry:")
    print(f"  {cfg['registry']}")
