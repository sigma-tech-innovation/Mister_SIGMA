import importlib.util
import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
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
    "sync_command",
    "sigma-cli/sigma/commands/sync.py"
)


class FakeSync:

    def snapshot(self):
        return {
            "configuration": {
                "enabled": True
            },
            "identity": {
                "user_id": "USER-0001"
            },
            "git": {
                "branch": "develop"
            },
        }

    def validate(self):
        return {
            "ready": True,
            "missing": [],
            "errors": [],
            "snapshot": self.snapshot(),
        }

    def plan(self):
        return {
            "ready": True,
            "steps": [
                "validate-identity",
                "detect-conflicts",
                "synchronize-shared-data",
            ],
            "validation": self.validate(),
        }


class SyncCommandTests(unittest.TestCase):

    def setUp(self):
        self.engine = SimpleNamespace(
            sync=FakeSync()
        )

        self.patch = patch.object(
            command.engine_module,
            "engine",
            self.engine
        )
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def test_snapshot_is_default(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run([])

        self.assertEqual(
            result["git"]["branch"],
            "develop"
        )
        self.assertIn(
            "SYNC SNAPSHOT",
            output.getvalue()
        )

    def test_snapshot_command(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run(["snapshot"])

        self.assertTrue(
            result["configuration"]["enabled"]
        )

    def test_validate_command(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run(["validate"])

        self.assertTrue(result["ready"])
        self.assertIn(
            "Validation : OK",
            output.getvalue()
        )

    def test_plan_command(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run(["plan"])

        self.assertTrue(result["ready"])
        self.assertIn(
            "detect-conflicts",
            output.getvalue()
        )

    def test_unknown_command(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run(["unknown"])

        self.assertIsNone(result)
        self.assertIn(
            "Usage: sync",
            output.getvalue()
        )


if __name__ == "__main__":
    unittest.main()
