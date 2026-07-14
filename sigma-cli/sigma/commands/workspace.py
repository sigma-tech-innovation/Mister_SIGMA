from pathlib import Path
from sigma.workspace import create_workspace, show_workspace

def run(args):
    root = Path.cwd() / ".sigma-workspace"

    if not args or args[0] == "show":
        show_workspace(root)
    elif args[0] == "init":
        create_workspace(root)
        show_workspace(root)
    else:
        print("Usage: workspace [init|show]")
