import importlib.util
import tempfile
import unittest
from pathlib import Path


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


config = load(
    "config",
    "sigma-core/managers/config_manager.py"
)
engine = load(
    "engine",
    "sigma-core/engine.py"
)


class ConfigManagerTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.m = config.ConfigManager(engine.engine)
        self.m.path = Path(self.temp_dir.name) / "sigma-config.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)

    def test_file_exists(self):
        self.assertFalse(self.m.exists())
        self.m.save({})
        self.assertTrue(self.m.exists())

    def test_list_and_count(self):
        self.m.save({
            "project": "Mister_SIGMA",
            "environment": "test"
        })

        self.assertIsInstance(self.m.list(), dict)
        self.assertEqual(self.m.count(), 2)

    def test_get_and_set(self):
        self.m.set("environment", "development")

        self.assertEqual(
            self.m.get("environment"),
            "development"
        )

    def test_create_update_delete(self):
        self.assertEqual(
            self.m.create("pytest-key", "value-1"),
            "value-1"
        )

        self.assertIsNone(
            self.m.create("pytest-key", "duplicate")
        )

        self.assertEqual(
            self.m.update("pytest-key", "value-2"),
            "value-2"
        )

        self.assertEqual(
            self.m.get("pytest-key"),
            "value-2"
        )

        self.assertIsNone(
            self.m.update("missing-key", "value")
        )

        self.assertTrue(
            self.m.delete("pytest-key")
        )

        self.assertFalse(
            self.m.delete("pytest-key")
        )

    def test_ensure_identity(self):
        identity = self.m.ensure_identity()

        self.assertIn("machine_id", identity)
        self.assertIn("user_id", identity)
        self.assertIn("node_id", identity)


if __name__ == "__main__":
    unittest.main()
