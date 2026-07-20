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
    "authentication_command",
    "sigma-cli/sigma/commands/authentication.py",
)


class FakeAuthentication:

    def snapshot(self):
        return {
            "organization_id": "ORG-1",
            "user_id": "USER-1",
            "validation": self.validate(),
        }

    def validate(self):
        return {
            "valid": True,
            "count": 1,
            "audit_count": 1,
            "errors": [],
        }

    def list(self):
        return [
            {
                "id": "CRED-1",
                "user_id": "USER-1",
                "type": "password",
                "status": "active",
            }
        ]

    def get(self, credential_id):
        if credential_id != "CRED-1":
            return None

        return self.list()[0]

    def list_audit(
        self,
        *,
        credential_id=None,
        user_id=None,
    ):
        records = [
            {
                "id": "AUTHLOG-1",
                "credential_id": "CRED-1",
                "user_id": "USER-1",
                "outcome": "success",
            }
        ]

        if credential_id == "missing":
            return []

        if user_id == "missing":
            return []

        return records

    def password_policy(self):
        return {
            "algorithm": "pbkdf2_sha256",
            "iterations": 600000,
            "min_length": 12,
        }


class AuthenticationCommandTests(
    unittest.TestCase
):

    def setUp(self):
        self.engine = SimpleNamespace(
            authentication=FakeAuthentication(),
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
            result["organization_id"],
            "ORG-1",
        )
        self.assertIn(
            "SIGMA AUTHENTICATION",
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
            result = command.run(["list"])

        self.assertEqual(
            result[0]["id"],
            "CRED-1",
        )

    def test_show_found(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run([
                "show",
                "CRED-1",
            ])

        self.assertTrue(result["found"])
        self.assertEqual(
            result["credential"]["id"],
            "CRED-1",
        )

    def test_show_missing(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run([
                "show",
                "missing",
            ])

        self.assertFalse(result["found"])

    def test_audit(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run([
                "audit",
                "--credential",
                "CRED-1",
            ])

        self.assertEqual(
            result[0]["outcome"],
            "success",
        )

    def test_policy(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run([
                "policy"
            ])

        self.assertEqual(
            result["algorithm"],
            "pbkdf2_sha256",
        )

    def test_unknown_command(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = command.run([
                "unknown"
            ])

        self.assertIsNone(result)
        self.assertIn(
            "Usage: authentication",
            output.getvalue(),
        )

    def test_cli_contract_has_no_password_argument(self):
        with open(
            "sigma-cli/sigma/commands/"
            "authentication.py",
            encoding="utf-8",
        ) as f:
            source = f.read()

        self.assertNotIn(
            'args[1]',
            source.split(
                "def authenticate",
            )[-1]
            if "def authenticate" in source
            else "",
        )

        self.assertNotIn(
            "getpass",
            source,
        )


if __name__ == "__main__":
    unittest.main()
