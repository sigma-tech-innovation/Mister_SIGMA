from pathlib import Path

ROOT = Path.cwd()

def run(args):

    cmd_dir = ROOT / "sigma-cli/sigma/commands"

    print("========== SIGMA CLI HELP ==========")
    print()

    for p in sorted(cmd_dir.glob("*.py")):
        if p.name == "__init__.py":
            continue

        print(f"sigma {p.stem}")
