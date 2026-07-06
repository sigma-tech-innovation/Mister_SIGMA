from pathlib import Path

ROOT = Path.cwd()

def run(args):

    log = ROOT / ".git" / "logs" / "HEAD"

    if not log.exists():
        print("No git history.")
        return

    print("========== LAST 20 COMMITS ==========")

    lines = log.read_text(errors="ignore").splitlines()

    for line in lines[-20:]:
        print(line)
