import platform
import socket
import uuid
from pathlib import Path


class LocalConfigManager:
    """
    Gestionnaire de la configuration locale d'une installation Sigma.

    Le fichier local est stocké dans :
    .sigma-workspace/configs/local.json

    Cette configuration est propre à une machine et ne doit pas être
    versionnée par Git.
    """

    IDENTITY_KEYS = (
        "installation_id",
        "machine_id",
        "node_id",
    )

    def __init__(self, engine):
        self.engine = engine
        self.path = (
            engine.root
            / ".sigma-workspace"
            / "configs"
            / "local.json"
        )

    def exists(self):
        return self.path.exists()

    def load(self):
        if not self.exists():
            return {}

        data = self.engine.load_json(self.path)

        if isinstance(data, dict):
            return data

        return {}

    def save(self, data):
        if not isinstance(data, dict):
            raise TypeError(
                "Local configuration must be a dictionary"
            )

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True
        )
        self.engine.save_json(self.path, data)
        return data

    def get(self, key, default=None):
        return self.load().get(key, default)

    def set(self, key, value):
        data = self.load()
        data[key] = value
        self.save(data)
        return value

    def list(self):
        return self.load()

    def count(self):
        return len(self.load())

    def create(self, key, value):
        data = self.load()

        if key in data:
            return None

        data[key] = value
        self.save(data)
        return value

    def update(self, key, value):
        data = self.load()

        if key not in data:
            return None

        data[key] = value
        self.save(data)
        return value

    def delete(self, key):
        data = self.load()

        if key not in data:
            return False

        del data[key]
        self.save(data)
        return True

    def defaults(self):
        return {
            "hostname": socket.gethostname(),
            "device_type": platform.system().lower(),
            "operating_system": platform.system(),
            "operating_system_release": platform.release(),
            "machine_architecture": platform.machine(),
            "python_version": platform.python_version(),
            "workspace_path": str(self.engine.root),
            "local_profile": "default",
            "local_environment": "development",
            "last_sync": "",
        }

    def ensure_identity(self):
        data = self.load()
        changed = False

        for key in self.IDENTITY_KEYS:
            if not data.get(key):
                data[key] = str(uuid.uuid4())
                changed = True

        for key, value in self.defaults().items():
            if key not in data:
                data[key] = value
                changed = True

        if changed:
            self.save(data)

        return data

    def installation_id(self):
        return self.ensure_identity()["installation_id"]

    def machine_id(self):
        return self.ensure_identity()["machine_id"]

    def node_id(self):
        return self.ensure_identity()["node_id"]
