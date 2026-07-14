import unittest
import importlib.util

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

release=load("release","sigma-core/managers/release_manager.py")
engine=load("engine","sigma-core/engine.py")

class ReleaseManagerTests(unittest.TestCase):

    def setUp(self):
        self.m = release.ReleaseManager(engine.engine)

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
            "version": "pytest-release-1.0.0",
            "status": "draft"
        })

        release_id = created["id"]

        try:
            self.assertTrue(self.m.exists(release_id))

            updated = self.m.update(
                release_id,
                status="published"
            )

            self.assertIsNotNone(updated)
            self.assertEqual(updated["status"], "published")

            self.assertTrue(self.m.delete(release_id))
            self.assertFalse(self.m.exists(release_id))

        finally:
            if self.m.exists(release_id):
                self.m.delete(release_id)

if __name__=="__main__":
    unittest.main()
