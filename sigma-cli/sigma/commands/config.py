import json
from pathlib import Path

ROOT = Path.cwd()

def run(args):

    cfg = ROOT / ".sigma-workspace/configs/config.json"

    if not cfg.exists():
        cfg.parent.mkdir(parents=True, exist_ok=True)
        cfg.write_text(json.dumps({
            "workspace": str(ROOT),
            "version": "1.0.0"
        }, indent=4))

    print(cfg)
    print(cfg.read_text())
