import unittest
import importlib.util

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

node = load("node", "sigma-core/managers/node_manager.py")
engine = load("engine", "sigma-core/engine.py")


class NodeManagerTests(unittest.TestCase):

    def setUp(self):
        self.m = node.NodeManager(engine.engine)

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)

    def test_list(self):
        self.assertIsInstance(self.m.list(), list)

    def test_count(self):
        self.assertGreaterEqual(self.m.count(), 0)

    def test_next_id(self):
        self.assertIsInstance(self.m.next_id(), str)

    def test_exists(self):
        nodes = self.m.list()
        if nodes:
            self.assertTrue(self.m.exists(nodes[0]["id"]))

    def test_create_update_delete(self):
        new = self.m.create({"name":"pytest-node","status":"active"})
        self.assertTrue(self.m.exists(new["id"]))

        updated = self.m.update(new["id"], status="offline")
        self.assertEqual(updated["status"], "offline")

        self.assertTrue(self.m.delete(new["id"]))
        self.assertFalse(self.m.exists(new["id"]))

if __name__ == "__main__":
    unittest.main()
