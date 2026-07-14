import json
from pathlib import Path


class JsonBackend:

    def __init__(self, root):
        self.root = Path(root)

    def path(self, name):
        return self.root / f"{name}.json"

    def load(self, name):
        path = self.path(name)

        if not path.exists():
            return []

        content = path.read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            return []

        return json.loads(content)

    def save(self, name, data):
        path = self.path(name)

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        path.write_text(
            json.dumps(
                data,
                indent=4,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

        return data

    def exists(self, name):
        return self.path(name).exists()

    def delete(self, name):
        path = self.path(name)

        if not path.exists():
            return False

        path.unlink()
        return True

    def list(self):
        if not self.root.exists():
            return []

        return sorted(
            path.stem
            for path in self.root.glob("*.json")
        )
