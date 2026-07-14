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
            ["json", "sqlite"]
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


if __name__ == "__main__":
    unittest.main()
