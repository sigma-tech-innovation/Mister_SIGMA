from pathlib import Path

def run(args):
    root = Path.cwd() / "sigma-db"

    print("===================================")
    print("        Σ SIGMA DATABASE")
    print("===================================")

    for p in sorted(root.glob("*.json")):
        print("-", p.name)
