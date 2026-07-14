import unittest
import importlib.util

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

registry=load("registry","sigma-core/managers/registry_manager.py")
engine=load("engine","sigma-core/engine.py")

class RegistryManagerTests(unittest.TestCase):

    def setUp(self):
        self.m = registry.RegistryManager(engine.engine)

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)

    def test_list(self):
        self.assertIsInstance(self.m.list(), list)

    def test_count(self):
        self.assertGreaterEqual(self.m.count(), 0)

    def test_next_id(self):
        self.assertIsInstance(self.m.next_id(), str)

    def test_exists(self):
        entries = self.m.list()
        if entries:
            self.assertTrue(self.m.exists(entries[0]["id"]))

    def test_create_update_delete(self):
        created = self.m.create({
            "name": "pytest-registry",
            "version": "1.0.0",
            "status": "active"
        })

        registry_id = created["id"]

        try:
            self.assertTrue(self.m.exists(registry_id))

            updated = self.m.update(
                registry_id,
                version="2.0.0"
            )

            self.assertIsNotNone(updated)
            self.assertEqual(updated["version"], "2.0.0")

            self.assertTrue(self.m.delete(registry_id))
            self.assertFalse(self.m.exists(registry_id))

        finally:
            if self.m.exists(registry_id):
                self.m.delete(registry_id)

if __name__=="__main__":
    unittest.main()
