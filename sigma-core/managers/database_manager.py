import importlib.util
from pathlib import Path


ROOT = Path.cwd()


def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(
        name,
        ROOT / relative_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base_backend = load_module(
    "database_base_backend",
    "sigma-core/managers/database_backends/base_backend.py"
)

json_backend = load_module(
    "database_json_backend",
    "sigma-core/managers/database_backends/json_backend.py"
)

sqlite_backend = load_module(
    "database_sqlite_backend",
    "sigma-core/managers/database_backends/sqlite_backend.py"
)

postgres_backend = load_module(
    "database_postgres_backend",
    "sigma-core/managers/database_backends/postgres_backend.py"
)

DatabaseBackend = base_backend.DatabaseBackend
JsonBackend = json_backend.JsonBackend
SQLiteBackend = sqlite_backend.SQLiteBackend
PostgreSQLBackend = postgres_backend.PostgreSQLBackend


class DatabaseManager:

    BACKENDS = {
        "json": JsonBackend,
        "postgresql": PostgreSQLBackend,
        "sqlite": SQLiteBackend,
    }

    def __init__(self, engine):
        self.engine = engine
        self.root = self.resolve_root(engine)
        self.backend_key = self.configured_backend()
        self.backend = self.create_backend(
            self.backend_key
        )

    def resolve_root(self, engine):
        if hasattr(engine, "workspace"):
            return engine.workspace.path(
                ".sigma-workspace",
                "database"
            )

        if hasattr(engine, "root"):
            return (
                Path(engine.root)
                / ".sigma-workspace"
                / "database"
            )

        if hasattr(engine, "db"):
            return Path(engine.db)

        raise RuntimeError(
            "Unable to locate database root"
        )

    def configured_backend(self):
        manager = getattr(
            self.engine,
            "database_config",
            None
        )

        if manager is not None:
            return manager.backend()

        config = getattr(
            self.engine,
            "config",
            None
        )

        if config is None:
            return "json"

        getter = getattr(config, "get", None)

        if getter is None:
            return "json"

        name = getter(
            "database_backend",
            "json"
        )

        return str(name or "json").strip().lower()

    def database_url(self):
        manager = getattr(
            self.engine,
            "database_config",
            None
        )

        if manager is not None:
            return manager.url() or None

        config = getattr(
            self.engine,
            "config",
            None
        )

        if config is None:
            return None

        getter = getattr(config, "get", None)

        if getter is None:
            return None

        return getter(
            "database_url",
            None
        )

    def create_backend(self, name):
        backend_class = self.BACKENDS.get(name)

        if backend_class is None:
            raise ValueError(
                f"Unknown database backend: {name}"
            )

        if name == "postgresql":
            return backend_class(
                root=self.root,
                database_url=self.database_url(),
            )

        return backend_class(self.root)

    def available_backends(self):
        return sorted(self.BACKENDS)

    def set_backend(self, name):
        self.backend = self.create_backend(name)
        self.backend_key = name
        return self.backend

    def migrate(
        self,
        target_backend,
        names=None
    ):
        source_backend = self.backend
        source_key = self.backend_key

        selected_names = (
            list(names)
            if names is not None
            else source_backend.list()
        )

        target = self.create_backend(
            target_backend
        )

        migrated = []

        for name in selected_names:
            target.save(
                name,
                source_backend.load(name)
            )
            migrated.append(name)

        return {
            "source_backend": source_key,
            "target_backend": target_backend,
            "databases": sorted(migrated),
            "count": len(migrated),
        }

    def switch_backend(
        self,
        name,
        migrate=False
    ):
        migration = None

        if migrate:
            migration = self.migrate(name)

        self.set_backend(name)

        return {
            "backend": self.backend_key,
            "migration": migration,
        }

    def backend_name(self):
        return type(self.backend).__name__

    def load(self, name):
        return self.backend.load(name)

    def save(self, name, data):
        return self.backend.save(name, data)

    def exists(self, name):
        return self.backend.exists(name)

    def delete(self, name):
        return self.backend.delete(name)

    def list(self):
        return self.backend.list()

    def validate(self):
        errors = []
        ready = True

        if self.backend_key not in self.BACKENDS:
            errors.append(
                "Unknown active backend"
            )
            ready = False

        if self.backend_key == "postgresql":
            if not self.backend.database_url:
                errors.append(
                    "PostgreSQL database URL is missing"
                )
                ready = False

            if not self.backend.driver_available():
                errors.append(
                    "PostgreSQL driver is unavailable"
                )
                ready = False

        return {
            "valid": not errors,
            "ready": ready,
            "backend": self.backend_name(),
            "backend_key": self.backend_key,
            "available_backends": (
                self.available_backends()
            ),
            "errors": errors,
        }

    def snapshot(self):
        return {
            "root": str(self.root),
            "backend": self.backend_name(),
            "backend_key": self.backend_key,
            "available_backends": (
                self.available_backends()
            ),
            "databases": self.list(),
            "validation": self.validate(),
        }
