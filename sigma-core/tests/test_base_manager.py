import importlib.util
import unittest
from pathlib import Path
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
            "root": Path("/tmp/sigma"),
            "db": Path("/tmp/sigma/sigma-db"),
            "projects_dir": Path("/tmp/sigma/sigma-projects"),
            "config": object(),
            "local_config": object(),
            "local_config_migration": object(),
            "identity": object(),
            "context": object(),
            "authorization": object(),
            "organization": object(),
            "workspace": object(),
            "logger": object(),
            "service": object(),
            "event": object(),
            "task": object(),
            "plugin": object(),
            "registry": object(),
            "database": object(),
            "projects": object(),
            "nodes": object(),
            "packages": object(),
            "templates": object(),
            "releases": object(),
            "api": object(),
            "sync": object(),
        }

        self.engine = SimpleNamespace(**self.dependencies)
        self.engine.managers = {
            "database": self.dependencies["database"],
            "identity": self.dependencies["identity"],
        }

        def manager(name):
            if name not in self.engine.managers:
                raise KeyError(name)
            return self.engine.managers[name]

        self.engine.manager = manager
        self.m = base.BaseManager(self.engine)

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)
        self.assertIs(self.m.engine, self.engine)

    def test_paths(self):
        self.assertIs(self.m.root, self.dependencies["root"])
        self.assertIs(self.m.db, self.dependencies["db"])
        self.assertIs(
            self.m.projects_dir,
            self.dependencies["projects_dir"]
        )

    def test_configuration_dependencies(self):
        self.assertIs(
            self.m.config,
            self.dependencies["config"]
        )
        self.assertIs(
            self.m.local_config,
            self.dependencies["local_config"]
        )
        self.assertIs(
            self.m.local_config_migration,
            self.dependencies["local_config_migration"]
        )
        self.assertIs(
            self.m.identity,
            self.dependencies["identity"]
        )
        self.assertIs(
            self.m.context,
            self.dependencies["context"]
        )
        self.assertIs(
            self.m.authorization,
            self.dependencies["authorization"]
        )
        self.assertIs(
            self.m.organization,
            self.dependencies["organization"]
        )

    def test_runtime_dependencies(self):
        for name in (
            "workspace",
            "logger",
            "service",
            "event",
            "task",
            "plugin",
        ):
            self.assertIs(
                getattr(self.m, name),
                self.dependencies[name]
            )

    def test_data_dependencies(self):
        for name in (
            "registry",
            "database",
            "projects",
            "nodes",
            "packages",
            "templates",
            "releases",
            "api",
            "sync",
        ):
            self.assertIs(
                getattr(self.m, name),
                self.dependencies[name]
            )

    def test_manager_lookup(self):
        self.assertIs(
            self.m.manager("database"),
            self.dependencies["database"]
        )
        self.assertIs(
            self.m.manager("identity"),
            self.dependencies["identity"]
        )

        with self.assertRaises(KeyError):
            self.m.manager("missing")


if __name__ == "__main__":
    unittest.main()
