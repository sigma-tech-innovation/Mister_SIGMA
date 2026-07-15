import importlib.util
import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace


def load(name, path):
    spec = importlib.util.spec_from_file_location(
        name,
        path,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


device_cli = load(
    "device_cli",
    "sigma-cli/sigma/commands/device.py",
)


class FakeDevice:

    def __init__(self, device_id):
        self.id = device_id

    def as_dict(self):
        return {
            "id": self.id,
        }


class FakeManager:

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
            "errors": [],
        }

    def list(self):
        return [
            FakeDevice("DEVICE-1"),
            FakeDevice("DEVICE-2"),
        ]


class DeviceCommandTests(
    unittest.TestCase
):

    def setUp(self):
        self.engine = SimpleNamespace(
            device=FakeManager(),
        )

    def capture(self, func):
        stream = io.StringIO()

        with redirect_stdout(stream):
            func(self.engine)

        return json.loads(
            stream.getvalue()
        )

    def test_status(self):
        data = self.capture(
            device_cli.status
        )

        self.assertTrue(
            data["validation"]["valid"]
        )

    def test_validate(self):
        data = self.capture(
            device_cli.validate
        )

        self.assertTrue(
            data["valid"]
        )

    def test_list(self):
        data = self.capture(
            device_cli.list_devices
        )

        self.assertEqual(
            len(data),
            2,
        )


if __name__ == "__main__":
    unittest.main()
