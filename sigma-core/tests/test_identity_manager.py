import importlib.util
import unittest
from types import SimpleNamespace


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


identity = load(
    "identity",
    "sigma-core/managers/identity_manager.py"
)


class FakeConfig:

    def ensure_identity(self):
        return {
            "machine_id": "machine-test",
            "user_id": "user-test",
            "node_id": "node-test"
        }


class IdentityManagerTests(unittest.TestCase):

    def setUp(self):
        self.engine = SimpleNamespace(
            config=FakeConfig()
        )
        self.m = identity.IdentityManager(self.engine)

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)

    def test_info(self):
        result = self.m.info()

        self.assertEqual(
            result,
            {
                "machine_id": "machine-test",
                "user_id": "user-test",
                "node_id": "node-test"
            }
        )

    def test_machine_id(self):
        self.assertEqual(
            self.m.machine_id(),
            "machine-test"
        )

    def test_user_id(self):
        self.assertEqual(
            self.m.user_id(),
            "user-test"
        )

    def test_node_id(self):
        self.assertEqual(
            self.m.node_id(),
            "node-test"
        )


if __name__ == "__main__":
    unittest.main()
