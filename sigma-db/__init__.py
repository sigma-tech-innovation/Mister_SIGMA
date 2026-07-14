import json
from pathlib import Path

DB_ROOT = Path(__file__).parent

def db_path(name):
    return DB_ROOT / f"{name}.json"

def load(name):
    p = db_path(name)
    if not p.exists():
        return []
    txt = p.read_text(encoding="utf-8").strip()
    return json.loads(txt) if txt else []

def save(name, data):
    db_path(name).write_text(
        json.dumps(data, indent=4),
        encoding="utf-8"
    )
