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


provider_manager_module = load(
    "data_provider_manager",
    "sigma-core/managers/data_provider_manager.py",
)


class FakeProvider:

    provider_key = "fake"

    def configuration(self):
        return {
            "enabled": True,
        }

    def validate(self):
        return {
            "valid": True,
            "errors": [],
        }

    def snapshot(self):
        return {
            "provider": self.provider_key,
            "configuration": self.configuration(),
            "validation": self.validate(),
        }


class DataProviderManagerTests(unittest.TestCase):

    def setUp(self):
        self.engine = SimpleNamespace()
        self.manager = (
            provider_manager_module
            .DataProviderManager(self.engine)
        )

    def test_empty_registry(self):
        self.assertEqual(
            self.manager.list(),
            [],
        )
        self.assertEqual(
            self.manager.count(),
            0,
        )

    def test_register_and_get(self):
        provider = FakeProvider()

        result = self.manager.register(
            "fake",
            provider,
        )

        self.assertIs(result, provider)
        self.assertIs(
            self.manager.get("fake"),
            provider,
        )
        self.assertTrue(
            self.manager.exists("fake")
        )

    def test_duplicate_registration(self):
        provider = FakeProvider()

        self.manager.register(
            "fake",
            provider,
        )

        self.assertIsNone(
            self.manager.register(
                "fake",
                provider,
            )
        )

    def test_unregister(self):
        self.manager.register(
            "fake",
            FakeProvider(),
        )

        self.assertTrue(
            self.manager.unregister("fake")
        )
        self.assertFalse(
            self.manager.unregister("fake")
        )

    def test_validate(self):
        self.manager.register(
            "fake",
            FakeProvider(),
        )

        result = self.manager.validate()

        self.assertTrue(result["valid"])
        self.assertEqual(
            result["count"],
            1,
        )

    def test_snapshot(self):
        self.manager.register(
            "fake",
            FakeProvider(),
        )

        result = self.manager.snapshot()

        self.assertIn(
            "fake",
            result["providers"],
        )
        self.assertTrue(
            result["validation"]["valid"]
        )


if __name__ == "__main__":
    unittest.main()
