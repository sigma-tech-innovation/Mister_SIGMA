from pathlib import Path

def run(args):
    root = Path.cwd() / "roadmap"

    print("===================================")
    print("         Σ SIGMA ROADMAP")
    print("===================================")

    for p in sorted(root.iterdir()):
        if p.is_file():
            print("-", p.name)
