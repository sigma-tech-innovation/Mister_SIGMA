import importlib.util
import unittest
from types import SimpleNamespace


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


task = load(
    "task",
    "sigma-core/managers/task_manager.py"
)


class TaskManagerTests(unittest.TestCase):

    def setUp(self):
        self.engine = SimpleNamespace()
        self.m = task.TaskManager(self.engine)

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)

    def test_add_and_get(self):
        self.m.add("backup", {"status": "pending"})

        self.assertEqual(
            self.m.get("backup"),
            {"status": "pending"}
        )

    def test_get_missing(self):
        self.assertIsNone(
            self.m.get("missing")
        )

    def test_list(self):
        self.m.add("sync", 1)
        self.m.add("backup", 2)

        self.assertEqual(
            self.m.list(),
            ["backup", "sync"]
        )

    def test_add_replaces_existing_task(self):
        self.m.add("deploy", "queued")
        self.m.add("deploy", "running")

        self.assertEqual(
            self.m.get("deploy"),
            "running"
        )
        self.assertEqual(
            self.m.list(),
            ["deploy"]
        )


if __name__ == "__main__":
    unittest.main()
