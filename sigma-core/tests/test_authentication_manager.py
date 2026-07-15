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

        self.assertEqual(
            set(snapshot),
            {
                "organization_id",
                "user_id",
                "validation",
            },
        )

        self.assertNotIn(
            "secret_records",
            snapshot,
        )
        self.assertNotIn(
            "credentials",
            snapshot,
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


    def test_password_policy(self):
        policy = self.manager.password_policy()

        self.assertEqual(
            policy["algorithm"],
            "pbkdf2_sha256",
        )
        self.assertEqual(
            policy["iterations"],
            600000,
        )
        self.assertEqual(
            policy["salt_bytes"],
            16,
        )

    def test_password_validation(self):
        self.assertFalse(
            self.manager.validate_password(
                "short"
            )["valid"]
        )

        self.assertTrue(
            self.manager.validate_password(
                "Correct-Horse-123"
            )["valid"]
        )

    def test_password_hash_is_salted(self):
        first = self.manager.hash_password(
            "Correct-Horse-123",
            iterations=1000,
        )
        second = self.manager.hash_password(
            "Correct-Horse-123",
            iterations=1000,
        )

        self.assertNotEqual(
            first["salt"],
            second["salt"],
        )
        self.assertNotEqual(
            first["hash"],
            second["hash"],
        )
        self.assertNotIn(
            "Correct-Horse-123",
            str(first),
        )

    def test_password_hash_deterministic_with_fixed_salt(self):
        first = self.manager.hash_password(
            "Correct-Horse-123",
            salt=b"0123456789abcdef",
            iterations=1000,
        )
        second = self.manager.hash_password(
            "Correct-Horse-123",
            salt=b"0123456789abcdef",
            iterations=1000,
        )

        self.assertEqual(first, second)

    def test_verify_password_hash(self):
        secret = self.manager.hash_password(
            "Correct-Horse-123",
            salt=b"0123456789abcdef",
            iterations=1000,
        )

        self.assertTrue(
            self.manager.verify_password_hash(
                "Correct-Horse-123",
                secret,
            )
        )
        self.assertFalse(
            self.manager.verify_password_hash(
                "Wrong-Password-123",
                secret,
            )
        )

    def test_secret_repository_is_separate(self):
        self.manager.save_secret(
            "CRED-1",
            {
                "algorithm": "pbkdf2_sha256",
                "digest": "sha256",
                "iterations": 1000,
                "salt": "salt",
                "hash": "hash",
            },
        )

        self.assertEqual(
            self.manager.records(),
            [],
        )
        self.assertEqual(
            self.manager.get_secret(
                "CRED-1"
            )["credential_id"],
            "CRED-1",
        )

    def test_set_and_verify_password(self):
        self.manager.create({
            "id": "CRED-1",
            "user_id": "USER-1",
            "type": "password",
        })

        original_iterations = (
            self.manager.PASSWORD_ITERATIONS
        )
        self.manager.PASSWORD_ITERATIONS = 1000

        try:
            result = self.manager.set_password(
                "CRED-1",
                "Correct-Horse-123",
            )

            self.assertTrue(
                result["metadata"][
                    "password_configured"
                ]
            )
            self.assertTrue(
                self.manager.verify_password(
                    "CRED-1",
                    "Correct-Horse-123",
                )
            )
            self.assertFalse(
                self.manager.verify_password(
                    "CRED-1",
                    "Wrong-Password-123",
                )
            )

        finally:
            self.manager.PASSWORD_ITERATIONS = (
                original_iterations
            )

    def test_failed_attempts_lock_credential(self):
        self.manager.create({
            "id": "CRED-1",
            "user_id": "USER-1",
            "type": "password",
        })

        original_iterations = (
            self.manager.PASSWORD_ITERATIONS
        )
        self.manager.PASSWORD_ITERATIONS = 1000

        try:
            self.manager.set_password(
                "CRED-1",
                "Correct-Horse-123",
            )

            for _ in range(
                self.manager.MAX_FAILED_ATTEMPTS
            ):
                self.assertFalse(
                    self.manager.verify_password(
                        "CRED-1",
                        "Wrong-Password-123",
                    )
                )

            credential = self.manager.get(
                "CRED-1"
            )

            self.assertEqual(
                credential["status"],
                "locked",
            )
            self.assertEqual(
                credential["failed_attempts"],
                self.manager.MAX_FAILED_ATTEMPTS,
            )

        finally:
            self.manager.PASSWORD_ITERATIONS = (
                original_iterations
            )

    def test_change_password(self):
        self.manager.create({
            "id": "CRED-1",
            "user_id": "USER-1",
            "type": "password",
        })

        original_iterations = (
            self.manager.PASSWORD_ITERATIONS
        )
        self.manager.PASSWORD_ITERATIONS = 1000

        try:
            self.manager.set_password(
                "CRED-1",
                "Old-Password-123",
            )

            self.manager.change_password(
                "CRED-1",
                "Old-Password-123",
                "New-Password-456",
            )

            self.assertFalse(
                self.manager.verify_password(
                    "CRED-1",
                    "Old-Password-123",
                )
            )
            self.assertTrue(
                self.manager.verify_password(
                    "CRED-1",
                    "New-Password-456",
                )
            )

        finally:
            self.manager.PASSWORD_ITERATIONS = (
                original_iterations
            )

    def test_change_password_rejects_wrong_current(self):
        self.manager.create({
            "id": "CRED-1",
            "user_id": "USER-1",
            "type": "password",
        })

        original_iterations = (
            self.manager.PASSWORD_ITERATIONS
        )
        self.manager.PASSWORD_ITERATIONS = 1000

        try:
            self.manager.set_password(
                "CRED-1",
                "Old-Password-123",
            )

            with self.assertRaises(
                authentication_module
                .InvalidCredentialError
            ):
                self.manager.change_password(
                    "CRED-1",
                    "Wrong-Password-123",
                    "New-Password-456",
                )

        finally:
            self.manager.PASSWORD_ITERATIONS = (
                original_iterations
            )

    def test_revoke_deletes_secret(self):
        self.manager.create({
            "id": "CRED-1",
            "user_id": "USER-1",
            "type": "password",
        })

        original_iterations = (
            self.manager.PASSWORD_ITERATIONS
        )
        self.manager.PASSWORD_ITERATIONS = 1000

        try:
            self.manager.set_password(
                "CRED-1",
                "Correct-Horse-123",
            )

            self.assertIsNotNone(
                self.manager.get_secret(
                    "CRED-1"
                )
            )

            self.manager.revoke(
                "CRED-1"
            )

            self.assertIsNone(
                self.manager.get_secret(
                    "CRED-1"
                )
            )

        finally:
            self.manager.PASSWORD_ITERATIONS = (
                original_iterations
            )

    def test_events_never_include_password_material(self):
        self.manager.create({
            "id": "CRED-1",
            "user_id": "USER-1",
            "type": "password",
        })

        original_iterations = (
            self.manager.PASSWORD_ITERATIONS
        )
        self.manager.PASSWORD_ITERATIONS = 1000

        try:
            self.manager.set_password(
                "CRED-1",
                "Correct-Horse-123",
            )

            serialized = str(
                self.event.events
            )

            self.assertNotIn(
                "Correct-Horse-123",
                serialized,
            )
            self.assertNotIn(
                "password_hash",
                serialized,
            )
            self.assertNotIn(
                '"hash"',
                serialized,
            )

        finally:
            self.manager.PASSWORD_ITERATIONS = (
                original_iterations
            )


    def configure_fast_password(self):
        self.original_iterations = (
            self.manager.PASSWORD_ITERATIONS
        )
        self.manager.PASSWORD_ITERATIONS = 1000

        self.addCleanup(
            setattr,
            self.manager,
            "PASSWORD_ITERATIONS",
            self.original_iterations,
        )

    def create_password_credential(self):
        self.configure_fast_password()

        self.manager.create({
            "id": "CRED-1",
            "user_id": "USER-1",
            "type": "password",
        })

        self.manager.set_password(
            "CRED-1",
            "Correct-Horse-123",
        )

    def test_authenticate_success(self):
        self.create_password_credential()

        result = self.manager.authenticate(
            "CRED-1",
            "Correct-Horse-123",
            context={
                "source": "unit-test",
            },
        )

        self.assertTrue(
            result["authenticated"]
        )
        self.assertEqual(
            result["user_id"],
            "USER-1",
        )
        self.assertEqual(
            result["credential_id"],
            "CRED-1",
        )
        self.assertTrue(
            result["audit_id"].startswith(
                "AUTHLOG-"
            )
        )

    def test_authenticate_invalid_password(self):
        self.create_password_credential()

        with self.assertRaises(
            authentication_module
            .InvalidCredentialError
        ):
            self.manager.authenticate(
                "CRED-1",
                "Wrong-Password-123",
            )

        audit = self.manager.list_audit()

        self.assertEqual(
            audit[-1]["outcome"],
            "failure",
        )
        self.assertEqual(
            audit[-1]["details"]["reason"],
            "invalid_credential",
        )

    def test_authenticate_unknown_credential(self):
        with self.assertRaises(
            authentication_module
            .InvalidCredentialError
        ):
            self.manager.authenticate(
                "CRED-MISSING",
                "Unknown-Password-123",
            )

        audit = self.manager.list_audit()

        self.assertEqual(
            audit[-1]["credential_id"],
            None,
        )
        self.assertEqual(
            audit[-1]["user_id"],
            None,
        )

    def test_authenticate_disabled_credential(self):
        self.create_password_credential()

        self.manager.update(
            "CRED-1",
            status="disabled",
        )

        with self.assertRaises(
            authentication_module
            .CredentialDisabledError
        ):
            self.manager.authenticate(
                "CRED-1",
                "Correct-Horse-123",
            )

        self.assertEqual(
            self.manager.list_audit()[-1][
                "details"
            ]["reason"],
            "credential_disabled",
        )

    def test_authenticate_locked_credential(self):
        self.create_password_credential()

        self.manager.update(
            "CRED-1",
            status="locked",
        )

        with self.assertRaises(
            authentication_module
            .CredentialLockedError
        ):
            self.manager.authenticate(
                "CRED-1",
                "Correct-Horse-123",
            )

        self.assertEqual(
            self.manager.list_audit()[-1][
                "details"
            ]["reason"],
            "credential_locked",
        )

    def test_repeated_failures_raise_locked_error(self):
        self.create_password_credential()

        for _ in range(
            self.manager.MAX_FAILED_ATTEMPTS - 1
        ):
            with self.assertRaises(
                authentication_module
                .InvalidCredentialError
            ):
                self.manager.authenticate(
                    "CRED-1",
                    "Wrong-Password-123",
                )

        with self.assertRaises(
            authentication_module
            .CredentialLockedError
        ):
            self.manager.authenticate(
                "CRED-1",
                "Wrong-Password-123",
            )

        self.assertEqual(
            self.manager.get(
                "CRED-1"
            )["status"],
            "locked",
        )

    def test_audit_filters(self):
        self.create_password_credential()

        self.manager.authenticate(
            "CRED-1",
            "Correct-Horse-123",
        )

        by_credential = (
            self.manager.list_audit(
                credential_id="CRED-1"
            )
        )
        by_user = self.manager.list_audit(
            user_id="USER-1"
        )

        self.assertEqual(
            len(by_credential),
            1,
        )
        self.assertEqual(
            len(by_user),
            1,
        )

    def test_audit_sanitizes_sensitive_context(self):
        self.create_password_credential()

        self.manager.authenticate(
            "CRED-1",
            "Correct-Horse-123",
            context={
                "ip": "127.0.0.1",
                "password": "must-disappear",
                "nested": {
                    "access_token": (
                        "must-disappear"
                    ),
                    "device": "android",
                },
            },
        )

        audit = self.manager.list_audit()[-1]
        serialized = str(audit)

        self.assertIn(
            "127.0.0.1",
            serialized,
        )
        self.assertIn(
            "android",
            serialized,
        )
        self.assertNotIn(
            "must-disappear",
            serialized,
        )
        self.assertNotIn(
            "password",
            audit["details"]["context"],
        )
        self.assertNotIn(
            "access_token",
            audit["details"][
                "context"
            ]["nested"],
        )

    def test_authentication_events_are_public(self):
        self.create_password_credential()

        self.manager.authenticate(
            "CRED-1",
            "Correct-Horse-123",
        )

        event_name, payload = (
            self.event.events[-1]
        )

        self.assertEqual(
            event_name,
            "authentication.succeeded",
        )
        self.assertEqual(
            payload["outcome"],
            "success",
        )

        serialized = str(payload).lower()

        self.assertNotIn(
            "correct-horse",
            serialized,
        )
        self.assertNotIn(
            "password",
            serialized,
        )
        self.assertNotIn(
            "hash",
            serialized,
        )
        self.assertNotIn(
            "salt",
            serialized,
        )

    def test_authenticate_creates_no_session(self):
        self.create_password_credential()

        result = self.manager.authenticate(
            "CRED-1",
            "Correct-Horse-123",
        )

        self.assertNotIn(
            "session_id",
            result,
        )
        self.assertNotIn(
            "token",
            result,
        )
        self.assertNotIn(
            "refresh_token",
            result,
        )

    def test_validate_reports_audit_database(self):
        result = self.manager.validate()

        self.assertEqual(
            result["audit_database"],
            "authentication_audit",
        )
        self.assertEqual(
            result["audit_count"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
