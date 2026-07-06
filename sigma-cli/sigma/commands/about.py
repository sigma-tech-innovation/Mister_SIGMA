from pathlib import Path

ROOT = Path.cwd()

def run(args):

    version = (ROOT / "VERSION").read_text().strip()

    print("===================================")
    print("         Σ MISTER SIGMA")
    print("===================================")
    print("Version :", version)
    print("Author  : Ayoub El Belkasmi")
    print("Company : Sigma Tech Innovation")
    print("License : MIT")
    print("Repository : Mister_SIGMA")
