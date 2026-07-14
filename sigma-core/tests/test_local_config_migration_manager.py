import importlib.util
import json
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


local_config_module = load(
    "local_config",
    "sigma-core/managers/local_config_manager.py"
)

migration_module = load(
    "local_config_migration",
    "sigma-core/managers/local_config_migration_manager.py"
)


class FakeEngine:

    def __init__(self, root):
        self.root = root
        self.local_config = (
            local_config_module.LocalConfigManager(self)
        )

    def load_json(self, path):
        content = Path(path).read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            return {}

        return json.loads(content)

    def save_json(self, path, data):
        Path(path).write_text(
            json.dumps(data, indent=4),
            encoding="utf-8"
        )


class LocalConfigMigrationManagerTests(
    unittest.TestCase
):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.engine = FakeEngine(self.root)

        self.source_path = (
            self.root / "sigma-config.json"
        )

        self.source_data = {
            "project": "Mister_SIGMA",
            "machine_id": "machine-source",
            "user_id": "user-global",
            "node_id": "node-source",
            "organization_id": "sigma-org",
            "workspace_id": "default",
            "device_type": "android",
            "environment": "development",
            "hostname": "Admin-Sigma-Phone",
            "owner": "Ayoub",
            "profile": "default",
            "role": "administrator",
            "team": "Sigma",
            "sync_enabled": True,
            "registry_url": "https://example.invalid",
            "api_endpoint": "",
            "last_sync": "",
        }

        self.source_path.write_text(
            json.dumps(
                self.source_data,
                indent=4
            ),
            encoding="utf-8"
        )

        self.m = (
            migration_module
            .LocalConfigMigrationManager(
                self.engine
            )
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)

    def test_load_source(self):
        self.assertEqual(
            self.m.load_source(),
            self.source_data
        )

    def test_preview_migrates_allowed_fields(self):
        plan = self.m.preview()
        result = plan["result"]

        self.assertEqual(
            result["machine_id"],
            "machine-source"
        )
        self.assertEqual(
            result["node_id"],
            "node-source"
        )
        self.assertEqual(
            result["hostname"],
            "Admin-Sigma-Phone"
        )
        self.assertEqual(
            result["local_profile"],
            "default"
        )
        self.assertEqual(
            result["local_environment"],
            "development"
        )
        self.assertIn(
            "installation_id",
            result
        )

    def test_preview_excludes_global_fields(self):
        result = self.m.preview()["result"]

        for key in (
            "user_id",
            "organization_id",
            "workspace_id",
            "owner",
            "role",
            "team",
            "registry_url",
            "api_endpoint",
            "sync_enabled",
            "project",
        ):
            self.assertNotIn(key, result)

    def test_preview_preserves_existing_values(self):
        self.engine.local_config.save({
            "machine_id": "machine-existing",
            "node_id": "node-existing",
            "installation_id": (
                "installation-existing"
            ),
            "hostname": "Existing-Host",
        })

        plan = self.m.preview()
        result = plan["result"]

        self.assertEqual(
            result["machine_id"],
            "machine-existing"
        )
        self.assertEqual(
            result["node_id"],
            "node-existing"
        )
        self.assertEqual(
            result["installation_id"],
            "installation-existing"
        )
        self.assertEqual(
            result["hostname"],
            "Existing-Host"
        )

    def test_dry_run_does_not_write(self):
        result = self.m.migrate(dry_run=True)

        self.assertTrue(result["dry_run"])
        self.assertFalse(result["written"])
        self.assertFalse(
            self.engine.local_config.exists()
        )

    def test_real_migration_writes_target(self):
        result = self.m.migrate(dry_run=False)

        self.assertFalse(result["dry_run"])
        self.assertTrue(result["written"])
        self.assertTrue(
            self.engine.local_config.exists()
        )

        local_data = (
            self.engine.local_config.load()
        )

        self.assertEqual(
            local_data["machine_id"],
            "machine-source"
        )
        self.assertEqual(
            local_data["node_id"],
            "node-source"
        )
        self.assertNotIn(
            "user_id",
            local_data
        )

    def test_real_migration_creates_backup(self):
        result = self.m.migrate(dry_run=False)

        backup_path = Path(
            result["backup_path"]
        )

        self.assertTrue(
            backup_path.exists()
        )

        backup_data = json.loads(
            backup_path.read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            backup_data,
            self.source_data
        )

    def test_source_is_not_modified(self):
        before = self.source_path.read_text(
            encoding="utf-8"
        )

        self.m.migrate(dry_run=False)

        after = self.source_path.read_text(
            encoding="utf-8"
        )

        self.assertEqual(before, after)

    def test_missing_source(self):
        self.source_path.unlink()

        result = self.m.migrate(
            dry_run=True
        )

        self.assertFalse(
            result["source_exists"]
        )
        self.assertIn(
            "installation_id",
            result["result"]
        )

    def test_forbidden_existing_target_is_rejected(
        self
    ):
        self.engine.local_config.save({
            "user_id": "forbidden-user"
        })

        with self.assertRaises(ValueError):
            self.m.migrate(dry_run=False)


if __name__ == "__main__":
    unittest.main()
