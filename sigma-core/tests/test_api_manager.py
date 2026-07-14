import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


api = load(
    "api",
    "sigma-core/managers/api_manager.py"
)


class ApiManagerTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.api_dir = self.root / "sigma-api"
        self.api_dir.mkdir()

        (self.api_dir / "__init__.py").write_text(
            "",
            encoding="utf-8"
        )
        (self.api_dir / "nodes.py").write_text(
            "",
            encoding="utf-8"
        )
        (self.api_dir / "registry.py").write_text(
            "",
            encoding="utf-8"
        )

        self.engine = SimpleNamespace(root=self.root)
        self.m = api.ApiManager(self.engine)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)

    def test_exists(self):
        self.assertTrue(self.m.exists())

    def test_endpoints(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = self.m.endpoints()

        self.assertIsNone(result)
        self.assertEqual(
            output.getvalue().strip().splitlines(),
            ["- nodes", "- registry"]
        )

    def test_info(self):
        output = io.StringIO()

        with redirect_stdout(output):
            result = self.m.info()

        self.assertIsNone(result)
        self.assertIn(
            f"API Root : {self.api_dir}",
            output.getvalue()
        )
        self.assertIn(
            "Available : True",
            output.getvalue()
        )

    def test_missing_api_directory(self):
        for path in self.api_dir.iterdir():
            path.unlink()
        self.api_dir.rmdir()

        self.assertFalse(self.m.exists())

        output = io.StringIO()

        with redirect_stdout(output):
            self.m.endpoints()

        self.assertEqual(output.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
