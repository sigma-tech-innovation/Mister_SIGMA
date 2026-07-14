import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


def load(name, path):
    spec = importlib.util.spec_from_file_location(
        name,
        path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


database = load(
    "database_manager",
    "sigma-core/managers/database_manager.py"
)


class DatabaseManagerTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()

        self.engine = SimpleNamespace(
            root=Path(self.temp.name)
        )

        self.manager = (
            database.DatabaseManager(
                self.engine
            )
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_backend(self):
        self.assertEqual(
            self.manager.backend_name(),
            "JsonBackend"
        )

    def test_save_load(self):
        self.manager.save(
            "users",
            [{"id": 1}]
        )

        self.assertEqual(
            self.manager.load("users"),
            [{"id": 1}]
        )

    def test_validate(self):
        self.assertTrue(
            self.manager.validate()["valid"]
        )


    def test_available_backends(self):
        self.assertEqual(
            self.manager.available_backends(),
            ["json", "postgresql", "sqlite"]
        )

    def test_exists_delete_and_list(self):
        self.assertFalse(
            self.manager.exists("users")
        )

        self.manager.save(
            "users",
            [{"id": 1}]
        )

        self.assertTrue(
            self.manager.exists("users")
        )
        self.assertEqual(
            self.manager.list(),
            ["users"]
        )
        self.assertTrue(
            self.manager.delete("users")
        )
        self.assertFalse(
            self.manager.delete("users")
        )

    def test_set_backend(self):
        backend = self.manager.set_backend(
            "json"
        )

        self.assertEqual(
            type(backend).__name__,
            "JsonBackend"
        )

        with self.assertRaises(ValueError):
            self.manager.set_backend(
                "missing"
            )

    def test_snapshot(self):
        snapshot = self.manager.snapshot()

        self.assertEqual(
            snapshot["backend_key"],
            "json"
        )
        self.assertTrue(
            snapshot["validation"]["valid"]
        )


    def test_sqlite_backend(self):
        backend = self.manager.set_backend(
            "sqlite"
        )

        self.assertEqual(
            type(backend).__name__,
            "SQLiteBackend"
        )

        self.manager.save(
            "users",
            [{"id": "USER-1"}]
        )

        self.assertEqual(
            self.manager.load("users"),
            [{"id": "USER-1"}]
        )
        self.assertTrue(
            self.manager.exists("users")
        )
        self.assertEqual(
            self.manager.list(),
            ["users"]
        )

    def test_sqlite_delete(self):
        self.manager.set_backend("sqlite")
        self.manager.save("users", [])

        self.assertTrue(
            self.manager.delete("users")
        )
        self.assertFalse(
            self.manager.exists("users")
        )


    def test_migrate_json_to_sqlite(self):
        self.manager.save(
            "users",
            [{"id": "USER-1"}]
        )
        self.manager.save(
            "memberships",
            [{"id": "MEM-1"}]
        )

        result = self.manager.migrate(
            "sqlite"
        )

        self.assertEqual(
            result["source_backend"],
            "json"
        )
        self.assertEqual(
            result["target_backend"],
            "sqlite"
        )
        self.assertEqual(
            result["databases"],
            ["memberships", "users"]
        )

        self.manager.set_backend("sqlite")

        self.assertEqual(
            self.manager.load("users"),
            [{"id": "USER-1"}]
        )
        self.assertEqual(
            self.manager.load("memberships"),
            [{"id": "MEM-1"}]
        )

    def test_switch_backend_with_migration(self):
        self.manager.save(
            "users",
            [{"id": "USER-1"}]
        )

        result = self.manager.switch_backend(
            "sqlite",
            migrate=True
        )

        self.assertEqual(
            result["backend"],
            "sqlite"
        )
        self.assertEqual(
            result["migration"]["count"],
            1
        )
        self.assertEqual(
            self.manager.load("users"),
            [{"id": "USER-1"}]
        )

    def test_migrate_selected_databases(self):
        self.manager.save("users", [1])
        self.manager.save("projects", [2])

        result = self.manager.migrate(
            "sqlite",
            names=["users"]
        )

        self.assertEqual(
            result["databases"],
            ["users"]
        )

        self.manager.set_backend("sqlite")

        self.assertEqual(
            self.manager.load("users"),
            [1]
        )
        self.assertEqual(
            self.manager.load("projects"),
            []
        )


    def test_postgresql_backend_registration(self):
        backend = self.manager.set_backend(
            "postgresql"
        )

        self.assertEqual(
            type(backend).__name__,
            "PostgreSQLBackend"
        )
        self.assertIsNone(
            backend.database_url
        )
        self.assertFalse(
            backend.driver_available()
        )

    def test_postgresql_url_from_config(self):
        self.engine.config = SimpleNamespace(
            get=lambda key, default=None: (
                "postgresql://sigma/database"
                if key == "database_url"
                else default
            )
        )

        manager = database.DatabaseManager(
            self.engine
        )

        backend = manager.set_backend(
            "postgresql"
        )

        self.assertEqual(
            backend.database_url,
            "postgresql://sigma/database"
        )


    def test_backend_selected_from_config(self):
        self.engine.config = SimpleNamespace(
            get=lambda key, default=None: (
                "sqlite"
                if key == "database_backend"
                else default
            )
        )

        manager = database.DatabaseManager(
            self.engine
        )

        self.assertEqual(
            manager.backend_key,
            "sqlite"
        )
        self.assertEqual(
            manager.backend_name(),
            "SQLiteBackend"
        )

    def test_postgresql_validation_without_driver(self):
        backend = self.manager.set_backend(
            "postgresql"
        )

        result = self.manager.validate()

        self.assertFalse(result["valid"])
        self.assertFalse(result["ready"])
        self.assertIn(
            "PostgreSQL database URL is missing",
            result["errors"]
        )
        self.assertIn(
            "PostgreSQL driver is unavailable",
            result["errors"]
        )
        self.assertIs(
            backend,
            self.manager.backend
        )

    def test_json_validation_ready(self):
        result = self.manager.validate()

        self.assertTrue(result["valid"])
        self.assertTrue(result["ready"])
        self.assertEqual(
            result["errors"],
            []
        )


if __name__ == "__main__":
    unittest.main()
