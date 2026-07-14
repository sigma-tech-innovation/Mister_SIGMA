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


if __name__ == "__main__":
    unittest.main()
