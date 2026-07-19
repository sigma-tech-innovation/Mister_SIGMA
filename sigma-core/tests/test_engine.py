import importlib.util
import unittest


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


engine_module = load(
    "engine",
    "sigma-core/engine.py",
)


class SigmaEngineTests(unittest.TestCase):

    def setUp(self):
        self.engine = engine_module.engine

    def test_engine_exists(self):
        self.assertIsNotNone(self.engine)

    def test_manager_registry_exists(self):
        self.assertIsInstance(self.engine.managers, dict)

    def test_node_manager_registered(self):
        self.assertIs(
            self.engine.manager("nodes"),
            self.engine.nodes,
        )

    def test_node_network_manager_registered(self):
        self.assertIs(
            self.engine.manager("node_network"),
            self.engine.node_network,
        )

    def test_unknown_manager_raises(self):
        with self.assertRaises(KeyError):
            self.engine.manager("__unknown__")


if __name__ == "__main__":
    unittest.main()
