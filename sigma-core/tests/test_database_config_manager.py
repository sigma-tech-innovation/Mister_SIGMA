import importlib.util
import unittest
from types import SimpleNamespace


def load(name, path):
    spec = importlib.util.spec_from_file_location(
        name,
        path,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


database_config_module = load(
    "database_config_manager",
    "sigma-core/managers/database_config_manager.py",
)


class FakeConfig:

    def __init__(self, data=None):
        self.data = dict(data or {})

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        return value


class DatabaseConfigManagerTests(unittest.TestCase):

    def create_manager(self, data=None):
        engine = SimpleNamespace(
            config=FakeConfig(data),
        )

        return (
            database_config_module
            .DatabaseConfigManager(engine)
        )

    def test_default_backend(self):
        manager = self.create_manager()

        self.assertEqual(
            manager.backend(),
            "json",
        )
        self.assertEqual(
            manager.url(),
            "",
        )

    def test_sqlite_configuration(self):
        manager = self.create_manager({
            "database_backend": "sqlite",
        })

        result = manager.validate()

        self.assertTrue(result["valid"])
        self.assertEqual(
            result["backend"],
            "sqlite",
        )

    def test_postgresql_configuration(self):
        manager = self.create_manager({
            "database_backend": "postgresql",
            "database_url": (
                "postgresql://localhost/sigma"
            ),
        })

        result = manager.validate()

        self.assertTrue(result["valid"])
        self.assertEqual(
            result["url"],
            "postgresql://localhost/sigma",
        )

    def test_postgresql_requires_url(self):
        manager = self.create_manager({
            "database_backend": "postgresql",
        })

        result = manager.validate()

        self.assertFalse(result["valid"])
        self.assertIn(
            "PostgreSQL database URL is missing",
            result["errors"],
        )

    def test_unknown_backend(self):
        manager = self.create_manager({
            "database_backend": "unknown",
        })

        result = manager.validate()

        self.assertFalse(result["valid"])
        self.assertIn(
            "Unsupported database backend: unknown",
            result["errors"],
        )


    def test_configure_sqlite(self):
        manager = self.create_manager()

        result = manager.configure(
            backend="sqlite"
        )

        self.assertTrue(result["valid"])
        self.assertEqual(
            manager.backend(),
            "sqlite"
        )

    def test_configure_postgresql(self):
        manager = self.create_manager()

        result = manager.configure(
            backend="postgresql",
            url="postgresql://localhost/sigma",
        )

        self.assertTrue(result["valid"])
        self.assertEqual(
            manager.backend(),
            "postgresql"
        )
        self.assertEqual(
            manager.url(),
            "postgresql://localhost/sigma"
        )

    def test_configure_rejects_invalid_backend(self):
        manager = self.create_manager()

        with self.assertRaisesRegex(
            ValueError,
            "Unsupported database backend"
        ):
            manager.configure(
                backend="invalid"
            )

        self.assertEqual(
            manager.backend(),
            "json"
        )

    def test_configure_rejects_postgresql_without_url(self):
        manager = self.create_manager()

        with self.assertRaisesRegex(
            ValueError,
            "database URL is missing"
        ):
            manager.set_backend(
                "postgresql"
            )

        self.assertEqual(
            manager.backend(),
            "json"
        )


if __name__ == "__main__":
    unittest.main()
