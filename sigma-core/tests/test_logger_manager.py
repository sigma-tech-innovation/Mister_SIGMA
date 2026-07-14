import importlib.util
import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


logger = load(
    "logger",
    "sigma-core/managers/logger_manager.py"
)


class LoggerManagerTests(unittest.TestCase):

    def setUp(self):
        self.engine = SimpleNamespace()
        self.m = logger.LoggerManager(self.engine)

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)

    def test_info(self):
        output = io.StringIO()

        with redirect_stdout(output):
            self.m.info("system ready")

        self.assertEqual(
            output.getvalue().strip(),
            "[INFO] system ready"
        )

    def test_warning(self):
        output = io.StringIO()

        with redirect_stdout(output):
            self.m.warning("low memory")

        self.assertEqual(
            output.getvalue().strip(),
            "[WARNING] low memory"
        )

    def test_error(self):
        output = io.StringIO()

        with redirect_stdout(output):
            self.m.error("operation failed")

        self.assertEqual(
            output.getvalue().strip(),
            "[ERROR] operation failed"
        )


if __name__ == "__main__":
    unittest.main()
