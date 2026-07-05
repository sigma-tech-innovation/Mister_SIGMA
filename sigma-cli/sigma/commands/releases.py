from pathlib import Path

def run(args):
    root = Path.cwd() / "releases"

    print("===================================")
    print("        Σ SIGMA RELEASES")
    print("===================================")

    for p in sorted(root.iterdir()):
        if p.is_file():
            print("-", p.name)
