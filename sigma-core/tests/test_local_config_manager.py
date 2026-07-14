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


local_config = load(
    "local_config",
    "sigma-core/managers/local_config_manager.py"
)


class FakeEngine:

    def __init__(self, root):
        self.root = root

    def load_json(self, path):
        import json

        content = Path(path).read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            return {}

        return json.loads(content)

    def save_json(self, path, data):
        import json

        Path(path).write_text(
            json.dumps(data, indent=4),
            encoding="utf-8"
        )


class LocalConfigManagerTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.engine = FakeEngine(self.root)
        self.m = local_config.LocalConfigManager(
            self.engine
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)

    def test_default_path(self):
        self.assertEqual(
            self.m.path,
            self.root
            / ".sigma-workspace"
            / "configs"
            / "local.json"
        )

    def test_missing_configuration(self):
        self.assertFalse(self.m.exists())
        self.assertEqual(self.m.load(), {})
        self.assertEqual(self.m.count(), 0)

    def test_save_creates_parent_directories(self):
        self.m.save({"profile": "test"})

        self.assertTrue(self.m.exists())
        self.assertEqual(
            self.m.get("profile"),
            "test"
        )

    def test_save_rejects_non_dictionary(self):
        with self.assertRaises(TypeError):
            self.m.save([])

    def test_create_update_delete(self):
        self.assertEqual(
            self.m.create("profile", "default"),
            "default"
        )

        self.assertIsNone(
            self.m.create("profile", "duplicate")
        )

        self.assertEqual(
            self.m.update("profile", "admin"),
            "admin"
        )

        self.assertEqual(
            self.m.get("profile"),
            "admin"
        )

        self.assertIsNone(
            self.m.update("missing", "value")
        )

        self.assertTrue(
            self.m.delete("profile")
        )

        self.assertFalse(
            self.m.delete("profile")
        )

    def test_set_and_list(self):
        result = self.m.set(
            "local_environment",
            "test"
        )

        self.assertEqual(result, "test")
        self.assertEqual(
            self.m.list(),
            {"local_environment": "test"}
        )

    def test_ensure_identity(self):
        data = self.m.ensure_identity()

        self.assertIn("installation_id", data)
        self.assertIn("machine_id", data)
        self.assertIn("node_id", data)
        self.assertIn("hostname", data)
        self.assertIn("workspace_path", data)
        self.assertNotIn("user_id", data)

    def test_identity_is_persistent(self):
        first = self.m.ensure_identity()
        second = self.m.ensure_identity()

        self.assertEqual(
            first["installation_id"],
            second["installation_id"]
        )
        self.assertEqual(
            first["machine_id"],
            second["machine_id"]
        )
        self.assertEqual(
            first["node_id"],
            second["node_id"]
        )

    def test_existing_values_are_preserved(self):
        self.m.save({
            "machine_id": "machine-existing",
            "node_id": "node-existing",
            "installation_id": "installation-existing",
            "local_profile": "administrator",
        })

        data = self.m.ensure_identity()

        self.assertEqual(
            data["machine_id"],
            "machine-existing"
        )
        self.assertEqual(
            data["node_id"],
            "node-existing"
        )
        self.assertEqual(
            data["installation_id"],
            "installation-existing"
        )
        self.assertEqual(
            data["local_profile"],
            "administrator"
        )

    def test_identity_accessors(self):
        data = self.m.ensure_identity()

        self.assertEqual(
            self.m.installation_id(),
            data["installation_id"]
        )
        self.assertEqual(
            self.m.machine_id(),
            data["machine_id"]
        )
        self.assertEqual(
            self.m.node_id(),
            data["node_id"]
        )


if __name__ == "__main__":
    unittest.main()
