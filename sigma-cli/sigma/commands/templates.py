from pathlib import Path

def run(args):
    root = Path.cwd() / "sigma-templates"

    print("===================================")
    print("       Σ SIGMA TEMPLATES")
    print("===================================")

    for p in sorted(root.iterdir()):
        if p.is_file():
            print("-", p.name)
