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
    "session_command",
    "sigma-cli/sigma/commands/session.py",
)


class FakeSessionRecord:

    def __init__(self, session_id):
        self.id = session_id

    def as_dict(self):
        return {
            "id": self.id,
            "state": "active",
            "user_id": "USER-1",
        }


class FakeSessionManager:

    def snapshot(self):
        return {
            "validation": self.validate(),
        }

    def validate(self):
        return {
            "valid": True,
            "states": [
                "active",
                "disabled",
                "expired",
                "revoked",
            ],
            "errors": [],
        }

    def list(self):
        return [
            FakeSessionRecord(
                "SESSION-1"
            )
        ]

    def get(self, session_id):
        if session_id == "SESSION-1":
            return FakeSessionRecord(
                session_id
            )

        return None


class SessionCommandTests(
    unittest.TestCase
):

    def setUp(self):
        self.engine = SimpleNamespace(
            session=FakeSessionManager(),
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

        self.assertTrue(
            result["validation"]["valid"]
        )
        self.assertIn(
            "SIGMA SESSION",
            output.getvalue(),
        )

    def test_validate(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run([
                "validate"
            ])

        self.assertTrue(result["valid"])

    def test_list(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run([
                "list"
            ])

        self.assertEqual(
            result[0]["id"],
            "SESSION-1",
        )

    def test_show_found(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run([
                "show",
                "SESSION-1",
            ])

        self.assertTrue(result["found"])
        self.assertEqual(
            result["session"]["id"],
            "SESSION-1",
        )

    def test_show_missing(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run([
                "show",
                "missing",
            ])

        self.assertFalse(result["found"])

    def test_show_usage(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run([
                "show"
            ])

        self.assertIsNone(result)
        self.assertIn(
            "Usage: session show",
            output.getvalue(),
        )

    def test_unknown_command(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run([
                "unknown"
            ])

        self.assertIsNone(result)
        self.assertIn(
            "Usage: session",
            output.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
