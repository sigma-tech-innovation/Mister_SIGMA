import importlib.util
import tempfile
import unittest
from pathlib import Path


def load(name, path):
    spec = importlib.util.spec_from_file_location(
        name,
        path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


config_module = load(
    "config_manager",
    "sigma-core/managers/config_manager.py"
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


class ConfigManagerTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.engine = FakeEngine(self.root)
        self.m = config_module.ConfigManager(
            self.engine
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def valid_config(self):
        return {
            "project": "Mister_SIGMA",
            "organization_id": "sigma-tech-innovation",
            "user_id": "USER-0001",
            "workspace_id": "default",
            "sync_enabled": True,
        }

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)

    def test_save_and_load(self):
        data = self.valid_config()

        self.assertEqual(
            self.m.save(data),
            data
        )
        self.assertEqual(
            self.m.load(),
            data
        )

    def test_get_set_list_count(self):
        self.m.save(self.valid_config())
        self.m.set("api_endpoint", "")

        self.assertEqual(
            self.m.get("api_endpoint"),
            ""
        )
        self.assertIsInstance(
            self.m.list(),
            dict
        )
        self.assertEqual(
            self.m.count(),
            6
        )

    def test_create_update_delete(self):
        self.m.save(self.valid_config())

        self.assertEqual(
            self.m.create("team", "Sigma"),
            "Sigma"
        )
        self.assertIsNone(
            self.m.create("team", "Duplicate")
        )
        self.assertEqual(
            self.m.update("team", "Core"),
            "Core"
        )
        self.assertIsNone(
            self.m.update("missing", "value")
        )
        self.assertTrue(
            self.m.delete("team")
        )
        self.assertFalse(
            self.m.delete("team")
        )

    def test_rejects_local_keys_on_save(self):
        data = self.valid_config()
        data["machine_id"] = "MACHINE-0001"

        with self.assertRaises(ValueError):
            self.m.save(data)

    def test_rejects_local_keys_on_set(self):
        self.m.save(self.valid_config())

        with self.assertRaises(ValueError):
            self.m.set(
                "node_id",
                "NODE-0001"
            )

    def test_validate_success(self):
        self.m.save(self.valid_config())

        result = self.m.validate()

        self.assertTrue(result["valid"])
        self.assertEqual(
            result["forbidden"],
            []
        )
        self.assertEqual(
            result["missing"],
            []
        )

    def test_validate_detects_legacy_file(self):
        self.engine.save_json(
            self.m.path,
            {
                **self.valid_config(),
                "hostname": "Legacy-Host",
            }
        )

        result = self.m.validate()

        self.assertFalse(result["valid"])
        self.assertIn(
            "hostname",
            result["forbidden"]
        )

    def test_ensure_identity_only_creates_user(self):
        self.m.save({
            "project": "Mister_SIGMA",
            "organization_id": "sigma-tech-innovation",
            "workspace_id": "default",
        })

        data = self.m.ensure_identity()

        self.assertIn("user_id", data)
        self.assertNotIn("machine_id", data)
        self.assertNotIn("node_id", data)
        self.assertNotIn("installation_id", data)

    def test_existing_user_identity_is_preserved(self):
        self.m.save(self.valid_config())

        first = self.m.ensure_identity()
        second = self.m.ensure_identity()

        self.assertEqual(
            first["user_id"],
            "USER-0001"
        )
        self.assertEqual(
            second["user_id"],
            "USER-0001"
        )


if __name__ == "__main__":
    unittest.main()
