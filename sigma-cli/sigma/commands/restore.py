import shutil
from pathlib import Path

ROOT = Path.cwd()

def run(args):

    backups = sorted((ROOT / "backups").glob("sigma-db-*"))

    if not backups:
        print("No backup found.")
        return

    latest = backups[-1]

    dst = ROOT / "sigma-db"

    if dst.exists():
        shutil.rmtree(dst)

    shutil.copytree(latest, dst)

    print("Database restored from:")
    print(latest)
