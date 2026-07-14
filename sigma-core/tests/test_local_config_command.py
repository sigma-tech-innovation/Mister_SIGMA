import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


def load(name, path):
    spec = importlib.util.spec_from_file_location(
        name,
        path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


command = load(
    "local_config_command",
    "sigma-cli/sigma/commands/local_config.py"
)


class FakeLocalConfig:

    def __init__(self, path):
        self.path = path
        self.data = {}

    def exists(self):
        return bool(self.data)

    def load(self):
        return dict(self.data)


class FakeMigration:

    def __init__(self, local_config):
        self.local_config = local_config

    def migrate(self, dry_run=True):
        result = {
            "source_path": "/tmp/sigma-config.json",
            "source_exists": True,
            "target_path": str(
                self.local_config.path
            ),
            "target_exists": (
                self.local_config.exists()
            ),
            "migrated": {
                "machine_id": "machine-test"
            },
            "preserved": {},
            "forbidden_found": [],
            "result": {
                "machine_id": "machine-test",
                "installation_id": (
                    "installation-test"
                ),
            },
            "dry_run": dry_run,
            "written": not dry_run,
            "backup_path": (
                None
                if dry_run
                else "/tmp/backup.json"
            ),
        }

        if not dry_run:
            self.local_config.data = dict(
                result["result"]
            )

        return result


class FakeEngine:

    def __init__(self, root):
        self.local_config = FakeLocalConfig(
            root / "local.json"
        )
        self.local_config_migration = (
            FakeMigration(self.local_config)
        )


class LocalConfigCommandTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.engine = FakeEngine(self.root)

        self.engine_patch = patch.object(
            command.engine_module,
            "engine",
            self.engine
        )
        self.engine_patch.start()

    def tearDown(self):
        self.engine_patch.stop()
        self.temp_dir.cleanup()

    def test_preview_is_default(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run([])

        self.assertTrue(result["dry_run"])
        self.assertFalse(result["written"])
        self.assertIn(
            "LOCAL CONFIG PREVIEW",
            output.getvalue()
        )

    def test_preview_command(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run(["preview"])

        self.assertTrue(result["dry_run"])
        self.assertIn(
            "machine-test",
            output.getvalue()
        )

    def test_show_missing(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run(["show"])

        self.assertEqual(result, {})
        self.assertIn(
            "Configuration locale absente",
            output.getvalue()
        )

    def test_show_existing(self):
        self.engine.local_config.data = {
            "machine_id": "machine-existing"
        }

        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run(["show"])

        self.assertEqual(
            result["machine_id"],
            "machine-existing"
        )
        self.assertIn(
            "machine-existing",
            output.getvalue()
        )

    def test_apply(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run(["apply"])

        self.assertTrue(result["written"])
        self.assertEqual(
            result["backup_path"],
            "/tmp/backup.json"
        )
        self.assertTrue(
            self.engine.local_config.exists()
        )
        self.assertIn(
            "Migration      : OK",
            output.getvalue()
        )

    def test_unknown_command(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run(["unknown"])

        self.assertIsNone(result)
        self.assertIn(
            "Usage: local-config",
            output.getvalue()
        )


if __name__ == "__main__":
    unittest.main()
