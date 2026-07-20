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


sessions_api = load(
    "sessions_api",
    "sigma-api/sessions.py",
)


class FakeSession:

    def __init__(
        self,
        session_id,
        *,
        user_id="USER-1",
        organization_id="ORG-1",
        workspace_id="WORKSPACE-1",
        credential_id="CRED-1",
        device_id="DEVICE-1",
        state="active",
    ):
        self.id = session_id
        self.user_id = user_id
        self.organization_id = organization_id
        self.workspace_id = workspace_id
        self.credential_id = credential_id
        self.device_id = device_id
        self.state = state

    def as_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "organization_id": (
                self.organization_id
            ),
            "workspace_id": (
                self.workspace_id
            ),
            "credential_id": (
                self.credential_id
            ),
            "device_id": self.device_id,
            "state": self.state,
        }


class FakeSessionManager:

    def __init__(self):
        self.sessions = [
            FakeSession("SESSION-1"),
            FakeSession(
                "SESSION-2",
                user_id="USER-2",
                organization_id="ORG-2",
                workspace_id="WORKSPACE-2",
                credential_id="CRED-2",
                device_id="DEVICE-2",
                state="revoked",
            ),
        ]

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
        return list(self.sessions)

    def get(self, session_id):
        for session in self.sessions:
            if session.id == session_id:
                return session

        return None

    def find(
        self,
        *,
        user_id=None,
        organization_id=None,
        workspace_id=None,
        credential_id=None,
        device_id=None,
        state=None,
    ):
        records = self.list()

        filters = {
            "user_id": user_id,
            "organization_id": organization_id,
            "workspace_id": workspace_id,
            "credential_id": credential_id,
            "device_id": device_id,
            "state": state,
        }

        for field, expected in filters.items():
            if expected is None:
                continue

            records = [
                session
                for session in records
                if getattr(
                    session,
                    field,
                ) == expected
            ]

        return records


class SessionsApiTests(unittest.TestCase):

    def setUp(self):
        self.manager = FakeSessionManager()
        self.engine = SimpleNamespace(
            session=self.manager,
        )

        self.patch = patch.object(
            sessions_api.engine_module,
            "engine",
            self.engine,
        )
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def test_success_contract(self):
        result = sessions_api.success(
            {"value": 1},
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
        result = sessions_api.failure(
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
        result = sessions_api.status()

        self.assertTrue(result["ok"])
        self.assertTrue(
            result["data"][
                "validation"
            ]["valid"]
        )

    def test_validate(self):
        result = sessions_api.validate()

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["status"],
            200,
        )

    def test_list_sessions(self):
        result = (
            sessions_api.list_sessions()
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            len(result["data"]),
            2,
        )

    def test_list_sessions_with_filter(self):
        result = sessions_api.list_sessions(
            user_id="USER-1",
            state="active",
        )

        self.assertEqual(
            len(result["data"]),
            1,
        )
        self.assertEqual(
            result["data"][0]["id"],
            "SESSION-1",
        )

    def test_get_session(self):
        result = sessions_api.get_session(
            "SESSION-1"
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["data"]["id"],
            "SESSION-1",
        )

    def test_get_session_missing(self):
        result = sessions_api.get_session(
            "missing"
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["status"],
            404,
        )
        self.assertEqual(
            result["error"]["code"],
            "SIGMA_SESSION_NOT_FOUND",
        )

    def test_get_session_requires_id(self):
        result = sessions_api.get_session(
            ""
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["status"],
            400,
        )

    def test_serialize_dictionary(self):
        result = (
            sessions_api.serialize_session({
                "id": "SESSION-1",
            })
        )

        self.assertEqual(
            result,
            {
                "id": "SESSION-1",
            },
        )

    def test_serialize_rejects_unknown_type(self):
        with self.assertRaises(
            TypeError
        ):
            sessions_api.serialize_session(
                object()
            )

    def test_contract_creates_no_token(self):
        with open(
            "sigma-api/sessions.py",
            encoding="utf-8",
        ) as f:
            module_source = f.read()

        compiled = compile(
            module_source,
            "sigma-api/sessions.py",
            "exec",
        )

        names = {
            str(name).lower()
            for name in compiled.co_names
        }

        self.assertNotIn(
            "refresh_token",
            names,
        )
        self.assertNotIn(
            "jwt",
            names,
        )
        self.assertNotIn(
            "session_secret",
            names,
        )


if __name__ == "__main__":
    unittest.main()
