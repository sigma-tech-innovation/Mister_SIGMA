import importlib.util
import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch


def load(name, path):
    spec = importlib.util.spec_from_file_location(
        name,
        path,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


command = load(
    "database_command",
    "sigma-cli/sigma/commands/database.py",
)


class FakeDatabaseConfig:

    def __init__(self):
        self.data = {
            "backend": "json",
            "url": "",
            "valid": True,
            "errors": [],
        }

    def backend(self):
        return self.data["backend"]

    def snapshot(self):
        return dict(self.data)

    def configure(
        self,
        backend=None,
        url=None,
    ):
        if backend is not None:
            self.data["backend"] = backend

        if url is not None:
            self.data["url"] = url

        return dict(self.data)


class FakeDatabase:

    def __init__(self):
        self.backend_key = "json"

    def snapshot(self):
        return {
            "backend_key": self.backend_key,
            "databases": ["users"],
        }

    def available_backends(self):
        return [
            "json",
            "postgresql",
            "sqlite",
        ]

    def migrate(self, target, names=None):
        return {
            "source_backend": "json",
            "target_backend": target,
            "databases": names or ["users"],
            "count": len(names or ["users"]),
        }

    def list(self):
        return ["users"]


class DatabaseCommandTests(unittest.TestCase):

    def setUp(self):
        self.engine = SimpleNamespace(
            database_config=FakeDatabaseConfig(),
            database=FakeDatabase(),
        )

        self.patch = patch.object(
            command.engine_module,
            "engine",
            self.engine,
        )
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def test_status_default(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run([])

        self.assertEqual(
            result["runtime"]["backend_key"],
            "json",
        )
        self.assertIn(
            "SIGMA DATABASE",
            output.getvalue(),
        )

    def test_backend_status(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run(["backend"])

        self.assertEqual(
            result["configured"],
            "json",
        )
        self.assertIn(
            "sqlite",
            result["available"],
        )

    def test_backend_configure(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run([
                "backend",
                "sqlite",
            ])

        self.assertEqual(
            result["backend"],
            "sqlite",
        )
        self.assertIn(
            "Restart Sigma",
            output.getvalue(),
        )

    def test_migrate(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run([
                "migrate",
                "sqlite",
                "users",
            ])

        self.assertEqual(
            result["target_backend"],
            "sqlite",
        )
        self.assertEqual(
            result["databases"],
            ["users"],
        )

    def test_list(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run(["list"])

        self.assertEqual(
            result,
            ["users"],
        )
        self.assertIn(
            "- users",
            output.getvalue(),
        )

    def test_unknown_command(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run(["unknown"])

        self.assertIsNone(result)
        self.assertIn(
            "Usage: database",
            output.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
