import importlib.util
import unittest


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


project = load(
    "project",
    "sigma-core/managers/project_manager.py"
)
engine = load(
    "engine",
    "sigma-core/engine.py"
)


class ProjectManagerTests(unittest.TestCase):

    def setUp(self):
        self.m = project.ProjectManager(engine.engine)

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)

    def test_create_update_delete(self):
        created = self.m.create({
            "name": "pytest-project",
            "type": "test",
            "status": "active"
        })

        project_id = created["id"]

        try:
            self.assertTrue(self.m.exists(project_id))

            updated = self.m.update(
                project_id,
                status="archived"
            )

            self.assertIsNotNone(updated)
            self.assertEqual(updated["status"], "archived")

            self.assertTrue(self.m.delete(project_id))
            self.assertFalse(self.m.exists(project_id))

        finally:
            if self.m.exists(project_id):
                self.m.delete(project_id)


if __name__ == "__main__":
    unittest.main()
