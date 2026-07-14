import importlib.util
import unittest
from types import SimpleNamespace


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = load(
    "base",
    "sigma-core/managers/base_manager.py"
)


class BaseManagerTests(unittest.TestCase):

    def setUp(self):
        self.dependencies = {
            "config": object(),
            "workspace": object(),
            "logger": object(),
            "service": object(),
            "event": object(),
            "task": object(),
            "plugin": object(),
            "registry": object(),
            "database": object(),
        }

        self.engine = SimpleNamespace(**self.dependencies)
        self.m = base.BaseManager(self.engine)

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)
        self.assertIs(self.m.engine, self.engine)

    def test_config(self):
        self.assertIs(
            self.m.config,
            self.dependencies["config"]
        )

    def test_workspace(self):
        self.assertIs(
            self.m.workspace,
            self.dependencies["workspace"]
        )

    def test_logger(self):
        self.assertIs(
            self.m.logger,
            self.dependencies["logger"]
        )

    def test_service(self):
        self.assertIs(
            self.m.service,
            self.dependencies["service"]
        )

    def test_event(self):
        self.assertIs(
            self.m.event,
            self.dependencies["event"]
        )

    def test_task(self):
        self.assertIs(
            self.m.task,
            self.dependencies["task"]
        )

    def test_plugin(self):
        self.assertIs(
            self.m.plugin,
            self.dependencies["plugin"]
        )

    def test_registry(self):
        self.assertIs(
            self.m.registry,
            self.dependencies["registry"]
        )

    def test_database(self):
        self.assertIs(
            self.m.database,
            self.dependencies["database"]
        )


if __name__ == "__main__":
    unittest.main()
