import importlib.util
import unittest
from types import SimpleNamespace


def load(name, path):
    spec = importlib.util.spec_from_file_location(
        name,
        path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


context_module = load(
    "context_manager",
    "sigma-core/managers/context_manager.py"
)


class DictionaryConfig:

    def __init__(self, data):
        self.data = dict(data)

    def load(self):
        return dict(self.data)


class ContextManagerTests(unittest.TestCase):

    def setUp(self):
        self.global_data = {
            "project": "Mister_SIGMA",
            "organization_id": "sigma-tech-innovation",
            "user_id": "USER-0001",
            "workspace_id": "WORKSPACE-0001",
            "owner": "Ayoub",
            "role": "administrator",
            "team": "Sigma",
            "machine_id": "legacy-machine",
        }

        self.local_data = {
            "installation_id": "INSTALLATION-0001",
            "machine_id": "MACHINE-0001",
            "node_id": "NODE-0001",
            "hostname": "Admin-Sigma-Phone",
            "device_type": "android",
            "local_profile": "default",
            "local_environment": "development",
            "last_sync": "",
            "user_id": "forbidden-local-user",
        }

        self.engine = SimpleNamespace(
            config=DictionaryConfig(
                self.global_data
            ),
            local_config=DictionaryConfig(
                self.local_data
            ),
        )

        self.m = context_module.ContextManager(
            self.engine
        )

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)

    def test_global_context(self):
        context = self.m.global_context()

        self.assertEqual(
            context["organization_id"],
            "sigma-tech-innovation"
        )
        self.assertEqual(
            context["user_id"],
            "USER-0001"
        )
        self.assertNotIn(
            "machine_id",
            context
        )

    def test_local_context(self):
        context = self.m.local_context()

        self.assertEqual(
            context["machine_id"],
            "MACHINE-0001"
        )
        self.assertEqual(
            context["installation_id"],
            "INSTALLATION-0001"
        )
        self.assertNotIn(
            "user_id",
            context
        )

    def test_current_context(self):
        context = self.m.current()

        self.assertEqual(
            context["user_id"],
            "USER-0001"
        )
        self.assertEqual(
            context["machine_id"],
            "MACHINE-0001"
        )

    def test_identity(self):
        identity = self.m.identity()

        self.assertEqual(
            set(identity),
            set(self.m.REQUIRED_FIELDS)
        )
        self.assertEqual(
            identity["node_id"],
            "NODE-0001"
        )

    def test_valid_context(self):
        self.assertTrue(self.m.valid())
        self.assertEqual(
            self.m.missing(),
            []
        )

        validation = self.m.validate()

        self.assertTrue(validation["valid"])
        self.assertEqual(
            validation["missing"],
            []
        )

    def test_missing_context(self):
        del self.local_data["node_id"]

        self.engine.local_config = DictionaryConfig(
            self.local_data
        )

        manager = context_module.ContextManager(
            self.engine
        )

        self.assertFalse(manager.valid())
        self.assertIn(
            "node_id",
            manager.missing()
        )

    def test_get(self):
        self.assertEqual(
            self.m.get("role"),
            "administrator"
        )
        self.assertEqual(
            self.m.get("unknown", "default"),
            "default"
        )

    def test_accessors(self):
        self.assertEqual(
            self.m.organization_id(),
            "sigma-tech-innovation"
        )
        self.assertEqual(
            self.m.user_id(),
            "USER-0001"
        )
        self.assertEqual(
            self.m.workspace_id(),
            "WORKSPACE-0001"
        )
        self.assertEqual(
            self.m.installation_id(),
            "INSTALLATION-0001"
        )
        self.assertEqual(
            self.m.machine_id(),
            "MACHINE-0001"
        )
        self.assertEqual(
            self.m.node_id(),
            "NODE-0001"
        )


if __name__ == "__main__":
    unittest.main()
