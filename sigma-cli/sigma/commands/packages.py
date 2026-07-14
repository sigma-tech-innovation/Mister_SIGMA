from pathlib import Path

def run(args):
    root = Path.cwd() / "sigma-cli" / "sigma" / "packages"

    print("===================================")
    print("        Σ SIGMA PACKAGES")
    print("===================================")

    for p in sorted(root.glob("*.py")):
        if p.name != "__init__.py":
            print("-", p.stem)
