from pathlib import Path

ROOT = Path.cwd()

def walk(path, level=0):
    for p in sorted(path.iterdir()):
        print("  " * level + "- " + p.name)
        if p.is_dir():
            walk(p, level + 1)

def run(args):

    print("===================================")
    print("          Σ SIGMA TREE")
    print("===================================")

    walk(ROOT)
