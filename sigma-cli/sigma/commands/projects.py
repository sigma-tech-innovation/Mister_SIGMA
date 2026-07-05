from pathlib import Path

def run(args):
    root = Path.cwd() / "sigma-projects"

    print("===================================")
    print("        Σ SIGMA PROJECTS")
    print("===================================")

    if not root.exists():
        print("No project directory.")
        return

    for p in sorted(root.iterdir()):
        if p.is_dir():
            print("-", p.name)
