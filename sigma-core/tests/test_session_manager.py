import importlib.util
import unittest
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
        self.engine = SimpleNamespace()
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


if __name__ == "__main__":
    unittest.main()
