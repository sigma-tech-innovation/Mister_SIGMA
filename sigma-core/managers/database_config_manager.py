class DatabaseConfigManager:
    """
    Configuration centralisée de la persistance Sigma.
    """

    SUPPORTED_BACKENDS = {
        "json",
        "sqlite",
        "postgresql",
    }

    DEFAULT_BACKEND = "json"

    def __init__(self, engine):
        self.engine = engine

    def backend(self):
        value = self.engine.config.get(
            "database_backend",
            self.DEFAULT_BACKEND,
        )

        return str(
            value or self.DEFAULT_BACKEND
        ).strip().lower()

    def url(self):
        value = self.engine.config.get(
            "database_url",
            "",
        )

        return str(value or "").strip()

    def validate(self):
        backend = self.backend()
        url = self.url()
        errors = []

        if backend not in self.SUPPORTED_BACKENDS:
            errors.append(
                f"Unsupported database backend: {backend}"
            )

        if backend == "postgresql" and not url:
            errors.append(
                "PostgreSQL database URL is missing"
            )

        return {
            "valid": not errors,
            "backend": backend,
            "url": url,
            "supported_backends": sorted(
                self.SUPPORTED_BACKENDS
            ),
            "errors": errors,
        }

    def configure(
        self,
        backend=None,
        url=None,
    ):
        current_backend = self.backend()
        current_url = self.url()

        selected_backend = (
            str(backend).strip().lower()
            if backend is not None
            else current_backend
        )

        selected_url = (
            str(url or "").strip()
            if url is not None
            else current_url
        )

        errors = []

        if (
            selected_backend
            not in self.SUPPORTED_BACKENDS
        ):
            errors.append(
                "Unsupported database backend: "
                + selected_backend
            )

        if (
            selected_backend == "postgresql"
            and not selected_url
        ):
            errors.append(
                "PostgreSQL database URL is missing"
            )

        if errors:
            raise ValueError(
                "; ".join(errors)
            )

        self.engine.config.set(
            "database_backend",
            selected_backend,
        )

        self.engine.config.set(
            "database_url",
            selected_url,
        )

        return self.validate()

    def set_backend(self, backend):
        return self.configure(
            backend=backend
        )

    def set_url(self, url):
        return self.configure(
            url=url
        )

    def snapshot(self):
        return self.validate()
