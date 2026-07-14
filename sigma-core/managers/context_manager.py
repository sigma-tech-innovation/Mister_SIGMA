class ContextManager:
    """
    Contexte d'exécution unifié de Mister SIGMA.

    Il agrège les données globales partagées et les données propres
    à l'installation locale, sans modifier leurs sources de vérité.
    """

    GLOBAL_FIELDS = (
        "project",
        "organization_id",
        "user_id",
        "workspace_id",
        "owner",
        "role",
        "team",
    )

    LOCAL_FIELDS = (
        "installation_id",
        "machine_id",
        "node_id",
        "hostname",
        "device_type",
        "local_profile",
        "local_environment",
        "last_sync",
    )

    REQUIRED_FIELDS = (
        "organization_id",
        "user_id",
        "workspace_id",
        "installation_id",
        "machine_id",
        "node_id",
    )

    def __init__(self, engine):
        self.engine = engine

    def global_context(self):
        config = self.engine.config.load()

        return {
            key: config.get(key)
            for key in self.GLOBAL_FIELDS
        }

    def local_context(self):
        config = self.engine.local_config.load()

        return {
            key: config.get(key)
            for key in self.LOCAL_FIELDS
        }

    def current(self):
        return {
            **self.global_context(),
            **self.local_context(),
        }

    def get(self, key, default=None):
        return self.current().get(key, default)

    def identity(self):
        context = self.current()

        return {
            key: context.get(key)
            for key in self.REQUIRED_FIELDS
        }

    def missing(self):
        identity = self.identity()

        return [
            key
            for key in self.REQUIRED_FIELDS
            if not identity.get(key)
        ]

    def valid(self):
        return not self.missing()

    def validate(self):
        missing = self.missing()

        return {
            "valid": not missing,
            "missing": missing,
            "context": self.current(),
        }

    def organization_id(self):
        return self.get("organization_id")

    def user_id(self):
        return self.get("user_id")

    def workspace_id(self):
        return self.get("workspace_id")

    def installation_id(self):
        return self.get("installation_id")

    def machine_id(self):
        return self.get("machine_id")

    def node_id(self):
        return self.get("node_id")
