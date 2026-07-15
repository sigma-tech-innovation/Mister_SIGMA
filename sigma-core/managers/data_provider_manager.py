class DataProviderManager:
    """
    Registre central des connecteurs externes Sigma.

    DatabaseManager reste responsable du stockage interne.
    DataProviderManager gère les interfaces externes.
    """

    def __init__(self, engine):
        self.engine = engine
        self.providers = {}

    def register(self, name, provider):
        key = str(name).strip().lower()

        if not key:
            raise ValueError(
                "Provider name is required"
            )

        if key in self.providers:
            return None

        self.providers[key] = provider
        return provider

    def unregister(self, name):
        key = str(name).strip().lower()

        if key not in self.providers:
            return False

        del self.providers[key]
        return True

    def get(self, name):
        key = str(name).strip().lower()
        return self.providers.get(key)

    def exists(self, name):
        return self.get(name) is not None

    def list(self):
        return sorted(self.providers)

    def count(self):
        return len(self.providers)

    def validate(self):
        results = {}
        errors = []

        for name in self.list():
            result = self.providers[name].validate()
            results[name] = result

            if not result.get("valid"):
                errors.append(
                    f"Provider invalid: {name}"
                )

        return {
            "valid": not errors,
            "count": self.count(),
            "providers": results,
            "errors": errors,
        }

    def snapshot(self):
        return {
            "providers": {
                name: self.providers[name].snapshot()
                for name in self.list()
            },
            "validation": self.validate(),
        }
