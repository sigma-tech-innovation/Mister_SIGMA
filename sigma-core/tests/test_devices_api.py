import importlib.util
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


devices_api = load(
    "devices_api",
    "sigma-api/devices.py",
)


class FakeDevice:

    def __init__(
        self,
        device_id,
        *,
        user_id="USER-1",
        organization_id="ORG-1",
        workspace_id="WS-1",
        device_type="phone",
        state="registered",
    ):
        self.id = device_id
        self.user_id = user_id
        self.organization_id = organization_id
        self.workspace_id = workspace_id
        self.device_type = device_type
        self.state = state

    def as_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "organization_id": self.organization_id,
            "workspace_id": self.workspace_id,
            "device_type": self.device_type,
            "state": self.state,
        }


class FakeDeviceManager:

    def __init__(self):
        self.devices = [
            FakeDevice("DEVICE-1"),
            FakeDevice(
                "DEVICE-2",
                user_id="USER-2",
                organization_id="ORG-2",
                workspace_id="WS-2",
                device_type="computer",
                state="trusted",
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
                "registered",
                "trusted",
                "disabled",
                "revoked",
            ],
            "types": [
                "phone",
                "computer",
            ],
            "errors": [],
        }

    def list(self):
        return list(self.devices)

    def get(self, device_id):
        for device in self.devices:
            if device.id == device_id:
                return device
        return None

    def find(
        self,
        *,
        user_id=None,
        organization_id=None,
        workspace_id=None,
        device_type=None,
        state=None,
    ):
        result = self.list()

        filters = {
            "user_id": user_id,
            "organization_id": organization_id,
            "workspace_id": workspace_id,
            "device_type": device_type,
            "state": state,
        }

        for field, expected in filters.items():
            if expected is None:
                continue

            result = [
                device
                for device in result
                if getattr(device, field) == expected
            ]

        return result


class DevicesApiTests(unittest.TestCase):

    def setUp(self):
        self.engine = SimpleNamespace(
            device=FakeDeviceManager(),
        )

        self.patch = patch.object(
            devices_api.engine_module,
            "engine",
            self.engine,
        )
        self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def test_status(self):
        result = devices_api.status()
        self.assertTrue(result["ok"])

    def test_validate(self):
        result = devices_api.validate()
        self.assertTrue(result["data"]["valid"])

    def test_list(self):
        result = devices_api.list_devices()
        self.assertEqual(len(result["data"]), 2)

    def test_find(self):
        result = devices_api.list_devices(
            user_id="USER-2",
        )

        self.assertEqual(
            result["data"][0]["id"],
            "DEVICE-2",
        )

    def test_get(self):
        result = devices_api.get_device(
            "DEVICE-1"
        )

        self.assertEqual(
            result["data"]["id"],
            "DEVICE-1",
        )

    def test_missing(self):
        result = devices_api.get_device(
            "UNKNOWN"
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["status"],
            404,
        )

    def test_requires_id(self):
        result = devices_api.get_device("")

        self.assertEqual(
            result["status"],
            400,
        )

    def test_dictionary_serialization(self):
        self.assertEqual(
            devices_api.serialize_device(
                {"id": "DEVICE"}
            ),
            {"id": "DEVICE"},
        )

    def test_invalid_serialization(self):
        with self.assertRaises(TypeError):
            devices_api.serialize_device(
                object()
            )

    def test_no_secret_names(self):
        names = {
            n.lower()
            for n in compile(
                Path("sigma-api/devices.py").read_text(encoding="utf-8"),
                "devices.py",
                "exec",
            ).co_names
        }

        self.assertNotIn(
            "private_key",
            names,
        )
        self.assertNotIn(
            "certificate",
            names,
        )
        self.assertNotIn(
            "device_secret",
            names,
        )


if __name__ == "__main__":
    unittest.main()
