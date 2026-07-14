from pathlib import Path

ROOT = Path.cwd()

def run(args):

    cmd_dir = ROOT / "sigma-cli/sigma/commands"

    print("========== SIGMA COMMANDS ==========")

    for p in sorted(cmd_dir.glob("*.py")):
        if p.name != "__init__.py":
            print("-", p.stem)
