import importlib.util
import unittest


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


package = load(
    "package",
    "sigma-core/managers/package_manager.py"
)
engine = load(
    "engine",
    "sigma-core/engine.py"
)


class PackageManagerTests(unittest.TestCase):

    def setUp(self):
        self.m = package.PackageManager(engine.engine)

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)

    def test_create_update_delete(self):
        created = self.m.create({
            "name": "pytest-package",
            "version": "1.0.0",
            "status": "active"
        })

        package_id = created["id"]

        try:
            self.assertTrue(self.m.exists(package_id))

            updated = self.m.update(
                package_id,
                version="2.0.0"
            )

            self.assertIsNotNone(updated)
            self.assertEqual(updated["version"], "2.0.0")

            self.assertTrue(self.m.delete(package_id))
            self.assertFalse(self.m.exists(package_id))

        finally:
            if self.m.exists(package_id):
                self.m.delete(package_id)


if __name__ == "__main__":
    unittest.main()
