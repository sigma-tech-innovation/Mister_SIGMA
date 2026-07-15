import importlib.util
import unittest
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


authentication_module = load(
    "authentication_manager",
    "sigma-core/managers/authentication_manager.py",
)


class AuthenticationManagerTests(unittest.TestCase):

    def setUp(self):
        self.engine = SimpleNamespace(
            now=lambda: "2026-07-15T01:00:00+00:00",
            context=SimpleNamespace(
                organization_id=lambda: "ORG-1",
                user_id=lambda: "USER-CURRENT",
            ),
        )

        self.manager = (
            authentication_module
            .AuthenticationManager(self.engine)
        )

    @patch.object(
        authentication_module.uuid,
        "uuid4",
        return_value="fixed-id",
    )
    def test_new_record(self, uuid_mock):
        record = self.manager.new_record(
            user_id="USER-1",
        )

        self.assertEqual(
            record["id"],
            "CRED-fixed-id",
        )
        self.assertEqual(
            record["organization_id"],
            "ORG-1",
        )
        self.assertEqual(
            record["user_id"],
            "USER-1",
        )
        self.assertEqual(
            record["type"],
            "password",
        )
        self.assertEqual(
            record["status"],
            "active",
        )
        self.assertEqual(
            record["version"],
            1,
        )
        uuid_mock.assert_called_once_with()

    def test_validate_record(self):
        record = self.manager.new_record(
            user_id="USER-1",
        )

        result = self.manager.validate_record(
            record
        )

        self.assertTrue(result["valid"])
        self.assertEqual(
            result["errors"],
            [],
        )

    def test_invalid_type(self):
        record = self.manager.new_record(
            user_id="USER-1",
        )
        record["type"] = "unknown"

        result = self.manager.validate_record(
            record
        )

        self.assertFalse(result["valid"])
        self.assertIn(
            "Invalid credential type",
            result["errors"],
        )

    def test_invalid_status(self):
        record = self.manager.new_record(
            user_id="USER-1",
        )
        record["status"] = "unknown"

        result = self.manager.validate_record(
            record
        )

        self.assertFalse(result["valid"])
        self.assertIn(
            "Invalid credential status",
            result["errors"],
        )

    def test_secret_fields_rejected(self):
        record = self.manager.new_record(
            user_id="USER-1",
        )
        record["password_hash"] = "secret"

        result = self.manager.validate_record(
            record
        )

        self.assertFalse(result["valid"])
        self.assertIn(
            "Secret fields are not allowed",
            result["errors"][0],
        )

    def test_public_record_redacts_unknown_fields(self):
        record = self.manager.new_record(
            user_id="USER-1",
        )
        record["internal_value"] = "private"

        public = self.manager.public_record(
            record
        )

        self.assertNotIn(
            "internal_value",
            public,
        )
        self.assertNotIn(
            "password_hash",
            public,
        )
        self.assertEqual(
            public["user_id"],
            "USER-1",
        )

    def test_can_authenticate(self):
        record = self.manager.new_record(
            user_id="USER-1",
        )

        self.assertTrue(
            self.manager.can_authenticate(
                record
            )
        )

        record["status"] = "locked"

        self.assertFalse(
            self.manager.can_authenticate(
                record
            )
        )

    def test_error_contract(self):
        error = (
            authentication_module
            .InvalidCredentialError(
                "Invalid credential",
                details={
                    "user_id": "USER-1",
                },
            )
        )

        self.assertEqual(
            error.as_dict(),
            {
                "code": (
                    "SIGMA_AUTH_INVALID_CREDENTIAL"
                ),
                "message": "Invalid credential",
                "retryable": False,
                "details": {
                    "user_id": "USER-1",
                },
            },
        )

    def test_validate_manager(self):
        result = self.manager.validate()

        self.assertTrue(result["valid"])
        self.assertIn(
            "password",
            result["credential_types"],
        )
        self.assertIn(
            "locked",
            result["statuses"],
        )

    def test_snapshot_contains_no_secret(self):
        snapshot = self.manager.snapshot()

        self.assertEqual(
            snapshot["organization_id"],
            "ORG-1",
        )
        self.assertEqual(
            snapshot["user_id"],
            "USER-CURRENT",
        )
        self.assertNotIn(
            "secret",
            str(snapshot).lower(),
        )


if __name__ == "__main__":
    unittest.main()
