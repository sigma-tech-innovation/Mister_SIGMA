import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

def run(args):

    src = ROOT / "sigma-db"

    dst = ROOT / "backups"

    dst.mkdir(exist_ok=True)

    name = "sigma-db-" + datetime.now().strftime("%Y%m%d-%H%M%S")

    target = dst / name

    shutil.copytree(src, target)

    print("Backup created:")
    print(target)
