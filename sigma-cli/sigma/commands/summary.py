import subprocess
from pathlib import Path

ROOT = Path.cwd()

def run(args):

    print("========== SIGMA SUMMARY ==========")
    print("Root:", ROOT)
    print()

    print("Branch:")
    subprocess.run(["git", "branch", "--show-current"])

    print()
    print("Last commits:")
    subprocess.run(["git", "log", "--oneline", "-5"])

    print()
    print("Status:")
    subprocess.run(["git", "status", "--short"])
