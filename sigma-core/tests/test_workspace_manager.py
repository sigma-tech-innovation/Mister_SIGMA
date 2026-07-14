import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


workspace = load(
    "workspace",
    "sigma-core/managers/workspace_manager.py"
)


class WorkspaceManagerTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.engine = SimpleNamespace(
            root=Path(self.temp_dir.name)
        )
        self.m = workspace.WorkspaceManager(self.engine)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)

    def test_root_path_exists(self):
        self.assertEqual(self.m.root(), self.engine.root)
        self.assertEqual(
            self.m.path("data", "file.txt"),
            self.engine.root / "data" / "file.txt"
        )
        self.assertFalse(self.m.exists("missing.txt"))

    def test_list_and_count(self):
        self.m.create("alpha.txt", content="A")
        self.m.create("beta.txt", content="B")

        entries = self.m.list()

        self.assertEqual(
            [entry.name for entry in entries],
            ["alpha.txt", "beta.txt"]
        )
        self.assertEqual(self.m.count(), 2)

    def test_create_update_delete_file(self):
        created = self.m.create(
            "data",
            "test.txt",
            content="version-1"
        )

        self.assertIsNotNone(created)
        self.assertTrue(self.m.exists("data", "test.txt"))
        self.assertIsNone(
            self.m.create(
                "data",
                "test.txt",
                content="duplicate"
            )
        )

        updated = self.m.update(
            "data",
            "test.txt",
            content="version-2"
        )

        self.assertIsNotNone(updated)
        self.assertEqual(
            updated.read_text(encoding="utf-8"),
            "version-2"
        )

        self.assertTrue(
            self.m.delete("data", "test.txt")
        )
        self.assertFalse(
            self.m.delete("data", "test.txt")
        )

    def test_create_delete_directory(self):
        created = self.m.create(
            "workspace",
            "nested",
            directory=True
        )

        self.assertIsNotNone(created)
        self.assertTrue(created.is_dir())
        self.assertIsNone(
            self.m.update(
                "workspace",
                "nested",
                content="invalid"
            )
        )

        self.assertTrue(
            self.m.delete("workspace")
        )
        self.assertFalse(
            self.m.exists("workspace")
        )


if __name__ == "__main__":
    unittest.main()
