import shutil
from pathlib import Path

ROOT = Path.cwd()

def run(args):

    db = ROOT / "sigma-db"

    if db.exists():
        shutil.rmtree(db)

    db.mkdir()

    print("Database reset:")
    print(db)
