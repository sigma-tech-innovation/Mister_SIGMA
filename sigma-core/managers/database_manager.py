import json
from pathlib import Path


class DatabaseBackend:
    """
    Backend abstrait.
    """

    def load(self, name):
        raise NotImplementedError

    def save(self, name, data):
        raise NotImplementedError


class JsonBackend(DatabaseBackend):

    def __init__(self, root):
        self.root = Path(root)

    def path(self, name):
        return self.root / f"{name}.json"

    def load(self, name):
        path = self.path(name)

        if not path.exists():
            return []

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    def save(self, name, data):
        path = self.path(name)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            json.dumps(
                data,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


class DatabaseManager:

    def __init__(self, engine):
        self.engine = engine

        if hasattr(engine, "workspace"):
            root = engine.workspace.path(
                ".sigma-workspace",
                "database",
            )

        elif hasattr(engine, "root"):
            root = (
                Path(engine.root)
                / ".sigma-workspace"
                / "database"
            )

        elif hasattr(engine, "db"):
            root = Path(engine.db)

        else:
            raise RuntimeError(
                "Unable to locate database root"
            )

        self.backend = JsonBackend(root)

    def backend_name(self):
        return type(
            self.backend
        ).__name__

    def load(self, name):
        return self.backend.load(name)

    def save(self, name, data):
        self.backend.save(name, data)

    def validate(self):
        return {
            "valid": True,
            "backend": self.backend_name(),
        }

    def snapshot(self):
        return {
            "backend": self.backend_name(),
        }
