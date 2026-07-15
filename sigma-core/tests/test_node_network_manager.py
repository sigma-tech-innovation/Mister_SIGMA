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
            SimpleNamespace(
                now=lambda: "2026-07-15T00:00:00+00:00"
            )
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


    def test_default_policy(self):
        policy = self.manager.default_policy()

        self.assertTrue(policy.allow_cluster_join)
        self.assertTrue(policy.allow_remote_management)
        self.assertTrue(policy.validate()["valid"])

    def test_new_node(self):
        node = self.manager.new_node(
            node_id="NODE-1",
            role="core",
            hostname="alpha",
            address="10.0.0.1",
        )

        self.assertEqual(node.id, "NODE-1")
        self.assertEqual(node.role, "core")
        self.assertEqual(node.state, "online")
        self.assertEqual(node.version, 1)

    def test_node_as_dict(self):
        node = self.manager.new_node(
            node_id="NODE-2",
            role="edge",
        )

        self.assertEqual(
            node.as_dict()["id"],
            "NODE-2",
        )


if __name__ == "__main__":
    unittest.main()
