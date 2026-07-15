import importlib.util
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace


def load(name, path):
    spec = importlib.util.spec_from_file_location(
        name,
        path,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


session_module = load(
    "session_manager",
    "sigma-core/managers/session_manager.py",
)


class SessionManagerContractTests(
    unittest.TestCase
):

    def setUp(self):
        self.engine = SimpleNamespace(
            now=lambda: (
                "2026-07-15T00:00:00+00:00"
            ),
        )
        self.manager = (
            session_module.SessionManager(
                self.engine
            )
        )

    def test_manager_exists(self):
        self.assertIs(
            self.manager.engine,
            self.engine,
        )

    def test_session_states(self):
        self.assertEqual(
            self.manager.STATES,
            {
                "active",
                "disabled",
                "expired",
                "revoked",
            },
        )

    def test_normalize_state(self):
        self.assertEqual(
            self.manager.normalize_state(
                " ACTIVE "
            ),
            "active",
        )
        self.assertEqual(
            self.manager.normalize_state(
                session_module
                .SessionState.REVOKED
            ),
            "revoked",
        )

    def test_state_exists(self):
        self.assertTrue(
            self.manager.state_exists(
                "active"
            )
        )
        self.assertFalse(
            self.manager.state_exists(
                "unknown"
            )
        )

    def test_error_contract(self):
        error = (
            session_module
            .SessionNotFoundError(
                "Session not found",
                details={
                    "session_id": "SESSION-1",
                },
            )
        )

        self.assertEqual(
            error.as_dict(),
            {
                "code": (
                    "SIGMA_SESSION_NOT_FOUND"
                ),
                "message": (
                    "Session not found"
                ),
                "retryable": False,
                "details": {
                    "session_id": (
                        "SESSION-1"
                    ),
                },
            },
        )

    def test_event_contract(self):
        event = session_module.SessionCreated(
            session_id="SESSION-1",
            user_id="USER-1",
            organization_id="ORG-1",
            occurred_at="2026-07-15T00:00:00",
            details={
                "source": "unit-test",
            },
        )

        self.assertEqual(
            event.as_dict(),
            {
                "event_type": (
                    "session.created"
                ),
                "session_id": (
                    "SESSION-1"
                ),
                "user_id": "USER-1",
                "organization_id": "ORG-1",
                "occurred_at": (
                    "2026-07-15T00:00:00"
                ),
                "details": {
                    "source": "unit-test",
                },
            },
        )

    def test_events_are_immutable(self):
        event = session_module.SessionRevoked(
            session_id="SESSION-1",
            user_id="USER-1",
            organization_id="ORG-1",
            occurred_at="2026",
            details={},
        )

        with self.assertRaises(
            AttributeError
        ):
            event.session_id = "SESSION-2"

    def test_validate(self):
        result = self.manager.validate()

        self.assertTrue(result["valid"])
        self.assertIn(
            "active",
            result["states"],
        )
        self.assertIn(
            "session.created",
            result["event_types"],
        )

    def test_snapshot(self):
        snapshot = self.manager.snapshot()

        self.assertTrue(
            snapshot["validation"]["valid"]
        )
        self.assertEqual(
            set(snapshot),
            {
                "validation",
            },
        )


    def test_default_policy(self):
        policy = self.manager.default_policy()

        self.assertEqual(
            policy.absolute_ttl_seconds,
            86400,
        )
        self.assertEqual(
            policy.idle_ttl_seconds,
            3600,
        )
        self.assertTrue(policy.renewable)
        self.assertTrue(
            policy.validate()["valid"]
        )

    def test_invalid_policy(self):
        policy = session_module.SessionPolicy(
            absolute_ttl_seconds=60,
            idle_ttl_seconds=120,
        )

        result = policy.validate()

        self.assertFalse(result["valid"])
        self.assertIn(
            "Idle TTL cannot exceed absolute TTL",
            result["errors"],
        )

    def test_new_session(self):
        session = self.manager.new_session(
            session_id="SESSION-1",
            user_id="USER-1",
            credential_id="CRED-1",
            organization_id="ORG-1",
            workspace_id="WORKSPACE-1",
            device_id="DEVICE-1",
            metadata={
                "source": "unit-test",
            },
        )

        self.assertEqual(
            session.id,
            "SESSION-1",
        )
        self.assertEqual(
            session.state,
            "active",
        )
        self.assertEqual(
            session.device_id,
            "DEVICE-1",
        )
        self.assertEqual(
            session.version,
            1,
        )
        self.assertEqual(
            session.metadata,
            {
                "source": "unit-test",
            },
        )

    def test_session_expirations(self):
        policy = session_module.SessionPolicy(
            absolute_ttl_seconds=7200,
            idle_ttl_seconds=1800,
        )

        session = self.manager.new_session(
            session_id="SESSION-1",
            user_id="USER-1",
            credential_id="CRED-1",
            organization_id="ORG-1",
            workspace_id="WORKSPACE-1",
            policy=policy,
        )

        self.assertEqual(
            session.expires_at,
            "2026-07-15T02:00:00+00:00",
        )
        self.assertEqual(
            session.idle_expires_at,
            "2026-07-15T00:30:00+00:00",
        )

    def test_validate_session(self):
        session = self.manager.new_session(
            session_id="SESSION-1",
            user_id="USER-1",
            credential_id="CRED-1",
            organization_id="ORG-1",
            workspace_id="WORKSPACE-1",
        )

        result = self.manager.validate_session(
            session
        )

        self.assertTrue(result["valid"])
        self.assertEqual(
            result["errors"],
            [],
        )

    def test_validate_session_rejects_missing_id(self):
        session = session_module.Session(
            id="",
            organization_id="ORG-1",
            workspace_id="WORKSPACE-1",
            user_id="USER-1",
            credential_id="CRED-1",
            state="active",
            created_at=(
                "2026-07-15T00:00:00+00:00"
            ),
            updated_at=(
                "2026-07-15T00:00:00+00:00"
            ),
            expires_at=(
                "2026-07-16T00:00:00+00:00"
            ),
            idle_expires_at=(
                "2026-07-15T01:00:00+00:00"
            ),
            last_activity_at=(
                "2026-07-15T00:00:00+00:00"
            ),
        )

        result = self.manager.validate_session(
            session
        )

        self.assertFalse(result["valid"])
        self.assertIn(
            "Missing fields: id",
            result["errors"],
        )

    def test_is_expired_by_idle_timeout(self):
        session = self.manager.new_session(
            session_id="SESSION-1",
            user_id="USER-1",
            credential_id="CRED-1",
            organization_id="ORG-1",
            workspace_id="WORKSPACE-1",
        )

        self.assertFalse(
            self.manager.is_expired(
                session,
                at=datetime(
                    2026,
                    7,
                    15,
                    0,
                    30,
                    tzinfo=timezone.utc,
                ),
            )
        )

        self.assertTrue(
            self.manager.is_expired(
                session,
                at=datetime(
                    2026,
                    7,
                    15,
                    1,
                    0,
                    tzinfo=timezone.utc,
                ),
            )
        )

    def test_is_expired_by_absolute_timeout(self):
        policy = session_module.SessionPolicy(
            absolute_ttl_seconds=60,
            idle_ttl_seconds=60,
        )

        session = self.manager.new_session(
            session_id="SESSION-1",
            user_id="USER-1",
            credential_id="CRED-1",
            organization_id="ORG-1",
            workspace_id="WORKSPACE-1",
            policy=policy,
        )

        self.assertTrue(
            self.manager.is_expired(
                session,
                at=(
                    "2026-07-15T00:01:00+00:00"
                ),
            )
        )

    def test_session_as_dict(self):
        session = self.manager.new_session(
            session_id="SESSION-1",
            user_id="USER-1",
            credential_id="CRED-1",
            organization_id="ORG-1",
            workspace_id="WORKSPACE-1",
        )

        data = session.as_dict()

        self.assertEqual(
            data["id"],
            "SESSION-1",
        )
        self.assertEqual(
            data["state"],
            "active",
        )

    def test_validate_reports_default_policy(self):
        result = self.manager.validate()

        self.assertTrue(result["valid"])
        self.assertEqual(
            result["default_policy"][
                "absolute_ttl_seconds"
            ],
            86400,
        )


    def create_repository_session(
        self,
        session_id="SESSION-1",
        user_id="USER-1",
        organization_id="ORG-1",
        workspace_id="WORKSPACE-1",
        credential_id="CRED-1",
        device_id=None,
    ):
        session = self.manager.new_session(
            session_id=session_id,
            user_id=user_id,
            credential_id=credential_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            device_id=device_id,
        )

        return self.manager.create_session(
            session
        )

    def test_repository_initially_empty(self):
        self.assertEqual(
            self.manager.list(),
            [],
        )
        self.assertEqual(
            self.manager.count(),
            0,
        )

    def test_repository_create_and_get(self):
        session = (
            self.create_repository_session()
        )

        self.assertIsNotNone(session)
        self.assertEqual(
            self.manager.count(),
            1,
        )
        self.assertIs(
            self.manager.get("SESSION-1"),
            session,
        )
        self.assertTrue(
            self.manager.exists("SESSION-1")
        )

    def test_repository_rejects_duplicate(self):
        self.assertIsNotNone(
            self.create_repository_session()
        )

        duplicate = (
            self.create_repository_session()
        )

        self.assertIsNone(duplicate)
        self.assertEqual(
            self.manager.count(),
            1,
        )

    def test_repository_delete(self):
        self.create_repository_session()

        deleted = self.manager.delete(
            "SESSION-1"
        )

        self.assertEqual(
            deleted.id,
            "SESSION-1",
        )
        self.assertFalse(
            self.manager.exists("SESSION-1")
        )
        self.assertIsNone(
            self.manager.delete("SESSION-1")
        )

    def test_find_by_user(self):
        self.create_repository_session(
            session_id="SESSION-1",
            user_id="USER-1",
        )
        self.create_repository_session(
            session_id="SESSION-2",
            user_id="USER-2",
        )

        result = self.manager.find(
            user_id="USER-1"
        )

        self.assertEqual(
            [session.id for session in result],
            ["SESSION-1"],
        )

    def test_find_by_workspace_and_device(self):
        self.create_repository_session(
            session_id="SESSION-1",
            workspace_id="WORKSPACE-1",
            device_id="DEVICE-1",
        )
        self.create_repository_session(
            session_id="SESSION-2",
            workspace_id="WORKSPACE-2",
            device_id="DEVICE-2",
        )

        result = self.manager.find(
            workspace_id="WORKSPACE-1",
            device_id="DEVICE-1",
        )

        self.assertEqual(
            len(result),
            1,
        )
        self.assertEqual(
            result[0].id,
            "SESSION-1",
        )

    def test_find_by_organization_and_credential(self):
        self.create_repository_session(
            session_id="SESSION-1",
            organization_id="ORG-1",
            credential_id="CRED-1",
        )
        self.create_repository_session(
            session_id="SESSION-2",
            organization_id="ORG-2",
            credential_id="CRED-2",
        )

        result = self.manager.find(
            organization_id="ORG-1",
            credential_id="CRED-1",
        )

        self.assertEqual(
            [session.id for session in result],
            ["SESSION-1"],
        )

    def test_find_by_state_normalizes_value(self):
        self.create_repository_session()

        result = self.manager.find(
            state=" ACTIVE "
        )

        self.assertEqual(
            len(result),
            1,
        )
        self.assertEqual(
            result[0].state,
            "active",
        )

    def test_create_session_rejects_invalid_model(self):
        invalid = session_module.Session(
            id="",
            organization_id="ORG-1",
            workspace_id="WORKSPACE-1",
            user_id="USER-1",
            credential_id="CRED-1",
            state="active",
            created_at=(
                "2026-07-15T00:00:00+00:00"
            ),
            updated_at=(
                "2026-07-15T00:00:00+00:00"
            ),
            expires_at=(
                "2026-07-16T00:00:00+00:00"
            ),
            idle_expires_at=(
                "2026-07-15T01:00:00+00:00"
            ),
            last_activity_at=(
                "2026-07-15T00:00:00+00:00"
            ),
        )

        with self.assertRaises(
            session_module.InvalidSessionError
        ):
            self.manager.create_session(
                invalid
            )


if __name__ == "__main__":
    unittest.main()
