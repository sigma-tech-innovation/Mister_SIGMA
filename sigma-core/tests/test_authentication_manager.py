import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
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


class FakeDatabase:

    def __init__(self, root):
        self.root = root

    def path(self, name):
        return self.root / f"{name}.json"

    def load(self, name):
        path = self.path(name)

        if not path.exists():
            return []

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    def save(self, name, data):
        path = self.path(name)
        path.write_text(
            json.dumps(
                data,
                indent=4,
            ),
            encoding="utf-8",
        )
        return data


class FakeEvent:

    def __init__(self):
        self.events = []

    def emit(self, name, payload):
        self.events.append(
            (name, payload)
        )


class AuthenticationManagerTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.event = FakeEvent()

        self.engine = SimpleNamespace(
            now=lambda: "2026-07-15T01:00:00+00:00",
            context=SimpleNamespace(
                organization_id=lambda: "ORG-1",
                user_id=lambda: "USER-CURRENT",
            ),
            database=FakeDatabase(
                Path(self.temp.name)
            ),
            event=self.event,
        )

        self.manager = (
            authentication_module
            .AuthenticationManager(self.engine)
        )

    def tearDown(self):
        self.temp.cleanup()

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


    def test_empty_repository(self):
        self.assertEqual(
            self.manager.records(),
            [],
        )
        self.assertEqual(
            self.manager.list(),
            [],
        )
        self.assertEqual(
            self.manager.count(),
            0,
        )

    def test_create_and_get_credential(self):
        credential = self.manager.create({
            "id": "CRED-1",
            "user_id": "USER-1",
            "type": "password",
        })

        self.assertEqual(
            credential["id"],
            "CRED-1",
        )
        self.assertEqual(
            self.manager.count(),
            1,
        )
        self.assertEqual(
            self.manager.get("CRED-1"),
            credential,
        )
        self.assertTrue(
            self.manager.exists("CRED-1")
        )

    def test_create_rejects_duplicate_id(self):
        data = {
            "id": "CRED-1",
            "user_id": "USER-1",
        }

        self.assertIsNotNone(
            self.manager.create(data)
        )
        self.assertIsNone(
            self.manager.create({
                "id": "CRED-1",
                "user_id": "USER-2",
            })
        )

    def test_create_rejects_duplicate_user_type(self):
        self.manager.create({
            "id": "CRED-1",
            "user_id": "USER-1",
            "type": "password",
        })

        duplicate = self.manager.create({
            "id": "CRED-2",
            "user_id": "USER-1",
            "type": "password",
        })

        self.assertIsNone(duplicate)

        external = self.manager.create({
            "id": "CRED-3",
            "user_id": "USER-1",
            "type": "external",
        })

        self.assertIsNotNone(external)

    def test_get_by_user_and_type(self):
        self.manager.create({
            "id": "CRED-1",
            "user_id": "USER-1",
            "type": "password",
        })
        self.manager.create({
            "id": "CRED-2",
            "user_id": "USER-1",
            "type": "external",
        })

        self.assertEqual(
            len(
                self.manager.get_by_user(
                    "USER-1"
                )
            ),
            2,
        )
        self.assertEqual(
            self.manager.get_by_user(
                "USER-1",
                credential_type="password",
            )[0]["id"],
            "CRED-1",
        )

    def test_update_increments_version(self):
        self.manager.create({
            "id": "CRED-1",
            "user_id": "USER-1",
        })

        updated = self.manager.update(
            "CRED-1",
            status="disabled",
            metadata={
                "reason": "manual",
            },
        )

        self.assertEqual(
            updated["version"],
            2,
        )
        self.assertEqual(
            updated["status"],
            "disabled",
        )
        self.assertEqual(
            updated["metadata"],
            {
                "reason": "manual",
            },
        )

    def test_update_rejects_secret_fields(self):
        self.manager.create({
            "id": "CRED-1",
            "user_id": "USER-1",
        })

        with self.assertRaisesRegex(
            ValueError,
            "Secret fields are not allowed",
        ):
            self.manager.update(
                "CRED-1",
                password_hash="secret",
            )

    def test_update_rejects_immutable_fields(self):
        self.manager.create({
            "id": "CRED-1",
            "user_id": "USER-1",
        })

        with self.assertRaisesRegex(
            ValueError,
            "Immutable fields",
        ):
            self.manager.update(
                "CRED-1",
                user_id="USER-2",
            )

    def test_revoke(self):
        self.manager.create({
            "id": "CRED-1",
            "user_id": "USER-1",
        })

        revoked = self.manager.revoke(
            "CRED-1"
        )

        self.assertEqual(
            revoked["status"],
            "revoked",
        )
        self.assertFalse(
            self.manager.can_authenticate(
                revoked
            )
        )

    def test_events_are_public(self):
        self.manager.create({
            "id": "CRED-1",
            "user_id": "USER-1",
        })

        name, payload = self.event.events[0]

        self.assertEqual(
            name,
            "authentication.credential_created",
        )
        self.assertNotIn(
            "password_hash",
            payload,
        )

    def test_validate_repository(self):
        self.manager.create({
            "id": "CRED-1",
            "user_id": "USER-1",
        })

        result = self.manager.validate()

        self.assertTrue(result["valid"])
        self.assertEqual(
            result["count"],
            1,
        )


if __name__ == "__main__":
    unittest.main()
