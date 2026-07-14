import uuid


class ConfigManager:
    """
    Gestionnaire de la configuration globale partagée.

    Ce fichier ne doit contenir aucune identité propre à une machine,
    un nœud ou une installation locale.
    """

    LOCAL_ONLY_KEYS = {
        "installation_id",
        "machine_id",
        "node_id",
        "hostname",
        "device_type",
        "profile",
        "local_profile",
        "environment",
        "local_environment",
        "last_sync",
        "workspace_path",
    }

    def __init__(self, engine):
        self.engine = engine
        self.path = engine.root / "sigma-config.json"

    def exists(self):
        return self.path.exists()

    def load(self):
        if not self.exists():
            return {}

        data = self.engine.load_json(self.path)

        if isinstance(data, dict):
            return data

        return {}

    def validate(self):
        data = self.load()

        forbidden = sorted(
            key
            for key in self.LOCAL_ONLY_KEYS
            if key in data
        )

        required = (
            "project",
            "organization_id",
            "user_id",
            "workspace_id",
        )

        missing = [
            key
            for key in required
            if not data.get(key)
        ]

        return {
            "valid": not forbidden and not missing,
            "forbidden": forbidden,
            "missing": missing,
            "configuration": data,
        }

    def save(self, data):
        if not isinstance(data, dict):
            raise TypeError(
                "Global configuration must be a dictionary"
            )

        forbidden = sorted(
            key
            for key in self.LOCAL_ONLY_KEYS
            if key in data
        )

        if forbidden:
            raise ValueError(
                "Local-only keys are forbidden in global configuration: "
                + ", ".join(forbidden)
            )

        self.engine.save_json(self.path, data)
        return data

    def get(self, key, default=None):
        return self.load().get(key, default)

    def set(self, key, value):
        if key in self.LOCAL_ONLY_KEYS:
            raise ValueError(
                f"Local-only key is forbidden: {key}"
            )

        config = self.load()
        config[key] = value
        self.save(config)
        return value

    def list(self):
        return self.load()

    def count(self):
        return len(self.load())

    def create(self, key, value):
        config = self.load()

        if key in config:
            return None

        return self.set(key, value)

    def update(self, key, value):
        config = self.load()

        if key not in config:
            return None

        return self.set(key, value)

    def delete(self, key):
        config = self.load()

        if key not in config:
            return False

        del config[key]
        self.save(config)
        return True

    def ensure_identity(self):
        """
        Compatibilité transitoire.

        Seul user_id appartient à la configuration globale.
        Les identités machine, node et installation sont gérées
        exclusivement par LocalConfigManager.
        """
        config = self.load()

        if not config.get("user_id"):
            config["user_id"] = str(uuid.uuid4())
            self.save(config)

        return config
