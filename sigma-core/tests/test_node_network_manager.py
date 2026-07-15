import importlib.util
import unittest
from types import SimpleNamespace


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


node_module = load(
    "node_network_manager",
    "sigma-core/managers/node_network_manager.py",
)


class NodeContractsTests(unittest.TestCase):

    def setUp(self):
        self.manager = node_module.NodeNetworkManager(
            SimpleNamespace()
        )

    def test_validate(self):
        result = self.manager.validate()

        self.assertTrue(result["valid"])
        self.assertIn("online", result["states"])
        self.assertIn("core", result["roles"])

    def test_snapshot(self):
        self.assertTrue(
            self.manager.snapshot()["validation"]["valid"]
        )


if __name__ == "__main__":
    unittest.main()
