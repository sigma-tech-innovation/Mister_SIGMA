from pathlib import Path
from datetime import datetime

LOG_DIR = Path.cwd() / ".sigma-workspace" / "logs"
LOG_FILE = LOG_DIR / "sigma.log"

def log(message):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {message}\n")
