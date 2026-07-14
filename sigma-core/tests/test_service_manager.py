import importlib.util
import unittest
from types import SimpleNamespace


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


service = load(
    "service",
    "sigma-core/managers/service_manager.py"
)


class ServiceManagerTests(unittest.TestCase):

    def setUp(self):
        self.engine = SimpleNamespace()
        self.m = service.ServiceManager(self.engine)

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)

    def test_register_and_get(self):
        item = object()

        self.m.register("database", item)

        self.assertIs(
            self.m.get("database"),
            item
        )

    def test_get_missing(self):
        self.assertIsNone(
            self.m.get("missing")
        )

    def test_list(self):
        self.m.register("workspace", object())
        self.m.register("config", object())

        self.assertEqual(
            self.m.list(),
            ["config", "workspace"]
        )

    def test_register_replaces_existing_service(self):
        first = object()
        second = object()

        self.m.register("logger", first)
        self.m.register("logger", second)

        self.assertIs(
            self.m.get("logger"),
            second
        )
        self.assertEqual(
            self.m.list(),
            ["logger"]
        )


if __name__ == "__main__":
    unittest.main()
