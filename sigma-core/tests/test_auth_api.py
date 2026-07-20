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


auth_api = load(
    "auth_api",
    "sigma-api/auth.py",
)


class FakeAuthenticationError(Exception):

    def __init__(
        self,
        code,
        message,
        *,
        retryable=False,
        details=None,
    ):
        super().__init__(message)
        self.contract = {
            "code": code,
            "message": message,
            "retryable": retryable,
            "details": dict(details or {}),
        }

    def as_dict(self):
        return dict(self.contract)


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
            "errors": [],
        }

    def password_policy(self):
        return {
            "algorithm": "pbkdf2_sha256",
            "iterations": 600000,
            "min_length": 12,
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

        return dict(self.list()[0])

    def list_audit(
        self,
        *,
        credential_id=None,
        user_id=None,
    ):
        return [
            {
                "id": "AUTHLOG-1",
                "credential_id": credential_id,
                "user_id": user_id,
                "outcome": "success",
            }
        ]

    def authenticate(
        self,
        credential_id,
        password,
        *,
        context=None,
    ):
        if credential_id == "LOCKED":
            raise FakeAuthenticationError(
                "SIGMA_AUTH_CREDENTIAL_LOCKED",
                "Credential is locked",
                retryable=True,
                details={
                    "credential_id": credential_id,
                },
            )

        if password != "Correct-Horse-123":
            raise FakeAuthenticationError(
                "SIGMA_AUTH_INVALID_CREDENTIAL",
                "Invalid credential",
            )

        return {
            "authenticated": True,
            "credential_id": credential_id,
            "user_id": "USER-1",
            "audit_id": "AUTHLOG-1",
        }

    def create(self, payload):
        if payload.get("id") == "DUPLICATE":
            return None

        if not payload.get("user_id"):
            raise ValueError(
                "Missing fields: user_id"
            )

        return {
            "id": payload.get(
                "id",
                "CRED-NEW",
            ),
            "user_id": payload["user_id"],
            "type": payload.get(
                "type",
                "password",
            ),
            "status": "active",
        }

    def revoke(self, credential_id):
        if credential_id != "CRED-1":
            return None

        return {
            "id": "CRED-1",
            "user_id": "USER-1",
            "type": "password",
            "status": "revoked",
        }


class AuthenticationApiTests(
    unittest.TestCase
):

    def setUp(self):
        self.authentication = (
            FakeAuthentication()
        )
        self.engine = SimpleNamespace(
            authentication=self.authentication,
        )

        self.patch = patch.object(
            auth_api.engine_module,
            "engine",
            self.engine,
        )
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def test_success_contract(self):
        result = auth_api.success(
            {
                "value": 1,
            },
            status=201,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["status"],
            201,
        )
        self.assertIsNone(
            result["error"]
        )

    def test_failure_contract(self):
        result = auth_api.failure(
            "ERROR",
            "Failed",
            status=400,
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["error"]["code"],
            "ERROR",
        )

    def test_status(self):
        result = auth_api.status()

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["data"][
                "organization_id"
            ],
            "ORG-1",
        )

    def test_validate(self):
        result = auth_api.validate()

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["status"],
            200,
        )

    def test_policy(self):
        result = auth_api.policy()

        self.assertEqual(
            result["data"]["algorithm"],
            "pbkdf2_sha256",
        )

    def test_list_credentials(self):
        result = (
            auth_api.list_credentials()
        )

        self.assertEqual(
            result["data"][0]["id"],
            "CRED-1",
        )

    def test_get_credential(self):
        found = auth_api.get_credential(
            "CRED-1"
        )
        missing = auth_api.get_credential(
            "missing"
        )

        self.assertTrue(found["ok"])
        self.assertFalse(missing["ok"])
        self.assertEqual(
            missing["status"],
            404,
        )

    def test_list_audit(self):
        result = auth_api.list_audit(
            credential_id="CRED-1",
            user_id="USER-1",
        )

        self.assertEqual(
            result["data"][0][
                "credential_id"
            ],
            "CRED-1",
        )

    def test_authenticate_success(self):
        result = auth_api.authenticate(
            {
                "credential_id": "CRED-1",
                "password": (
                    "Correct-Horse-123"
                ),
            },
            context={
                "source": "unit-test",
            },
        )

        self.assertTrue(result["ok"])
        self.assertTrue(
            result["data"][
                "authenticated"
            ]
        )
        self.assertNotIn(
            "password",
            str(result).lower(),
        )

    def test_authenticate_invalid_password(self):
        result = auth_api.authenticate({
            "credential_id": "CRED-1",
            "password": "Wrong-Password",
        })

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["status"],
            401,
        )
        self.assertEqual(
            result["error"]["code"],
            "SIGMA_AUTH_INVALID_CREDENTIAL",
        )

    def test_authenticate_locked(self):
        result = auth_api.authenticate({
            "credential_id": "LOCKED",
            "password": (
                "Correct-Horse-123"
            ),
        })

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["status"],
            423,
        )
        self.assertTrue(
            result["error"]["retryable"]
        )

    def test_authenticate_invalid_payload(self):
        result = auth_api.authenticate(
            None
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["status"],
            400,
        )

    def test_create_credential(self):
        result = (
            auth_api.create_credential({
                "id": "CRED-2",
                "user_id": "USER-2",
                "type": "password",
            })
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["status"],
            201,
        )

    def test_create_rejects_secret_fields(self):
        result = (
            auth_api.create_credential({
                "user_id": "USER-2",
                "password": "must-not-pass",
            })
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["status"],
            400,
        )
        self.assertIn(
            "password",
            result["error"][
                "details"
            ]["fields"],
        )

    def test_create_conflict(self):
        result = (
            auth_api.create_credential({
                "id": "DUPLICATE",
                "user_id": "USER-2",
            })
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["status"],
            409,
        )

    def test_revoke(self):
        result = (
            auth_api.revoke_credential(
                "CRED-1"
            )
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["data"]["status"],
            "revoked",
        )

    def test_revoke_missing(self):
        result = (
            auth_api.revoke_credential(
                "missing"
            )
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["status"],
            404,
        )

    def test_sanitize_response(self):
        result = (
            auth_api.sanitize_response({
                "user_id": "USER-1",
                "password": "hidden",
                "nested": {
                    "access_token": "hidden",
                    "device": "android",
                },
            })
        )

        self.assertEqual(
            result["user_id"],
            "USER-1",
        )
        self.assertEqual(
            result["nested"]["device"],
            "android",
        )
        self.assertNotIn(
            "password",
            result,
        )
        self.assertNotIn(
            "access_token",
            result["nested"],
        )

    def test_api_creates_no_session_contract(self):
        with open(
            "sigma-api/auth.py",
            encoding="utf-8",
        ) as f:
            source = f.read()

        self.assertNotIn(
            "session_manager",
            source,
        )
        self.assertNotIn(
            "refresh_token",
            source,
        )
        self.assertNotIn(
            "jwt",
            source.lower(),
        )


if __name__ == "__main__":
    unittest.main()
