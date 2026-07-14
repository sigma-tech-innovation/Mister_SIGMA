import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


database = load(
    "database",
    "sigma-core/managers/database_manager.py"
)


class DatabaseManagerTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_dir = Path(self.temp_dir.name)
        self.engine = SimpleNamespace(db=self.db_dir)
        self.m = database.DatabaseManager(self.engine)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)

    def test_path(self):
        self.assertEqual(
            self.m.path("nodes"),
            self.db_dir / "nodes.json"
        )

    def test_load_missing_and_empty(self):
        self.assertEqual(
            self.m.load("missing"),
            []
        )

        self.m.path("empty").write_text(
            "",
            encoding="utf-8"
        )

        self.assertEqual(
            self.m.load("empty"),
            []
        )

    def test_save_and_load(self):
        data = [
            {
                "id": "TEST-0001",
                "name": "pytest"
            }
        ]

        self.m.save("items", data)

        self.assertEqual(
            self.m.load("items"),
            data
        )

    def test_list(self):
        self.m.save("zeta", [])
        self.m.save("alpha", [])

        self.assertEqual(
            self.m.list(),
            ["alpha", "zeta"]
        )


if __name__ == "__main__":
    unittest.main()
