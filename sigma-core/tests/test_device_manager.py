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


device_module = load(
    "device_manager",
    "sigma-core/managers/device_manager.py",
)


class DeviceManagerContractTests(
    unittest.TestCase
):

    def setUp(self):
        self.engine = SimpleNamespace(
            now=lambda: "2026-07-15T00:00:00+00:00"
        )
        self.manager = (
            device_module.DeviceManager(
                self.engine
            )
        )

    def test_manager_exists(self):
        self.assertIs(
            self.manager.engine,
            self.engine,
        )

    def test_device_states(self):
        self.assertEqual(
            self.manager.STATES,
            {
                "registered",
                "trusted",
                "disabled",
                "revoked",
            },
        )

    def test_device_types(self):
        expected = {
            "phone",
            "tablet",
            "computer",
            "server",
            "vps",
            "raspberry_pi",
            "iot",
            "gateway",
            "radio",
            "virtual",
            "unknown",
        }

        self.assertEqual(
            self.manager.TYPES,
            expected,
        )

    def test_normalize_state(self):
        self.assertEqual(
            self.manager.normalize_state(
                " TRUSTED "
            ),
            "trusted",
        )

        self.assertEqual(
            self.manager.normalize_state(
                device_module
                .DeviceState.REVOKED
            ),
            "revoked",
        )

    def test_normalize_type(self):
        self.assertEqual(
            self.manager.normalize_type(
                " RASPBERRY_PI "
            ),
            "raspberry_pi",
        )

        self.assertEqual(
            self.manager.normalize_type(
                device_module.DeviceType.VPS
            ),
            "vps",
        )

    def test_state_exists(self):
        self.assertTrue(
            self.manager.state_exists(
                "registered"
            )
        )

        self.assertFalse(
            self.manager.state_exists(
                "missing"
            )
        )

    def test_type_exists(self):
        self.assertTrue(
            self.manager.type_exists(
                "phone"
            )
        )

        self.assertTrue(
            self.manager.type_exists(
                "raspberry_pi"
            )
        )

        self.assertFalse(
            self.manager.type_exists(
                "spaceship"
            )
        )

    def test_error_contract(self):
        error = (
            device_module
            .DeviceNotFoundError(
                "Device not found",
                details={
                    "device_id": "DEVICE-1",
                },
            )
        )

        self.assertEqual(
            error.as_dict(),
            {
                "code": (
                    "SIGMA_DEVICE_NOT_FOUND"
                ),
                "message": (
                    "Device not found"
                ),
                "retryable": False,
                "details": {
                    "device_id": "DEVICE-1",
                },
            },
        )

    def test_event_contract(self):
        event = (
            device_module.DeviceRegistered(
                device_id="DEVICE-1",
                user_id="USER-1",
                organization_id="ORG-1",
                occurred_at=(
                    "2026-07-15T00:00:00"
                ),
                details={
                    "platform": "android",
                },
            )
        )

        self.assertEqual(
            event.as_dict(),
            {
                "device_id": "DEVICE-1",
                "user_id": "USER-1",
                "organization_id": "ORG-1",
                "occurred_at": (
                    "2026-07-15T00:00:00"
                ),
                "details": {
                    "platform": "android",
                },
                "event_type": (
                    "device.registered"
                ),
            },
        )

    def test_events_are_immutable(self):
        event = device_module.DeviceRevoked(
            device_id="DEVICE-1",
            user_id="USER-1",
            organization_id="ORG-1",
            occurred_at="2026",
            details={},
        )

        with self.assertRaises(
            AttributeError
        ):
            event.device_id = "DEVICE-2"

    def test_validate(self):
        result = self.manager.validate()

        self.assertTrue(result["valid"])
        self.assertIn(
            "trusted",
            result["states"],
        )
        self.assertIn(
            "raspberry_pi",
            result["types"],
        )
        self.assertIn(
            "device.registered",
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

        self.assertFalse(policy.trusted)
        self.assertTrue(
            policy.allow_remote_access
        )
        self.assertTrue(
            policy.validate()["valid"]
        )

    def test_new_device(self):
        device = self.manager.new_device(
            device_id="DEVICE-1",
            organization_id="ORG-1",
            workspace_id="WS-1",
            user_id="USER-1",
            device_type="phone",
            platform="android",
            hostname="pixel",
            metadata={
                "manufacturer": "Google",
            },
        )

        self.assertEqual(
            device.id,
            "DEVICE-1",
        )
        self.assertEqual(
            device.device_type,
            "phone",
        )
        self.assertEqual(
            device.platform,
            "android",
        )
        self.assertEqual(
            device.state,
            "registered",
        )
        self.assertEqual(
            device.version,
            1,
        )

    def test_device_as_dict(self):
        device = self.manager.new_device(
            device_id="DEVICE-1",
            organization_id="ORG-1",
            workspace_id="WS-1",
            user_id="USER-1",
            device_type="computer",
        )

        self.assertEqual(
            device.as_dict()["id"],
            "DEVICE-1",
        )


    def create_repository_device(
        self,
        device_id="DEVICE-1",
        user_id="USER-1",
        organization_id="ORG-1",
        workspace_id="WS-1",
        device_type="phone",
    ):
        device = self.manager.new_device(
            device_id=device_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            user_id=user_id,
            device_type=device_type,
        )

        return self.manager.create_device(
            device
        )

    def test_repository_initially_empty(self):
        self.assertEqual(
            self.manager.count(),
            0,
        )
        self.assertEqual(
            self.manager.list(),
            [],
        )

    def test_repository_create_and_get(self):
        device = (
            self.create_repository_device()
        )

        self.assertEqual(
            self.manager.count(),
            1,
        )
        self.assertIs(
            self.manager.get("DEVICE-1"),
            device,
        )
        self.assertTrue(
            self.manager.exists("DEVICE-1")
        )

    def test_repository_rejects_duplicate(self):
        self.create_repository_device()

        duplicate = (
            self.create_repository_device()
        )

        self.assertIsNone(duplicate)
        self.assertEqual(
            self.manager.count(),
            1,
        )

    def test_repository_delete(self):
        self.create_repository_device()

        deleted = self.manager.delete(
            "DEVICE-1"
        )

        self.assertEqual(
            deleted.id,
            "DEVICE-1",
        )
        self.assertFalse(
            self.manager.exists("DEVICE-1")
        )

    def test_find_by_user(self):
        self.create_repository_device(
            device_id="DEVICE-1",
            user_id="USER-1",
        )
        self.create_repository_device(
            device_id="DEVICE-2",
            user_id="USER-2",
        )

        result = self.manager.find(
            user_id="USER-1"
        )

        self.assertEqual(
            [d.id for d in result],
            ["DEVICE-1"],
        )

    def test_find_by_state_and_type(self):
        self.create_repository_device(
            device_id="DEVICE-1",
            device_type="phone",
        )
        self.create_repository_device(
            device_id="DEVICE-2",
            device_type="computer",
        )

        result = self.manager.find(
            state="REGISTERED",
            device_type=" PHONE ",
        )

        self.assertEqual(
            len(result),
            1,
        )
        self.assertEqual(
            result[0].id,
            "DEVICE-1",
        )


if __name__ == "__main__":
    unittest.main()
