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


identity_module = load(
    "identity_manager",
    "sigma-core/managers/identity_manager.py"
)


class FakeContext:

    def __init__(self):
        self.data = {
            "organization_id": "sigma-tech-innovation",
            "user_id": "USER-0001",
            "workspace_id": "WORKSPACE-0001",
            "installation_id": "INSTALLATION-0001",
            "machine_id": "MACHINE-0001",
            "node_id": "NODE-0001",
        }

    def identity(self):
        return dict(self.data)


class IdentityManagerTests(unittest.TestCase):

    def setUp(self):
        self.context = FakeContext()
        self.engine = SimpleNamespace(
            context=self.context
        )
        self.m = identity_module.IdentityManager(
            self.engine
        )

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)
        self.assertIs(self.m.engine, self.engine)

    def test_info_uses_context(self):
        self.assertEqual(
            self.m.info(),
            self.context.identity()
        )

    def test_validate_success(self):
        result = self.m.validate()

        self.assertTrue(result["valid"])
        self.assertEqual(result["missing"], [])

    def test_validate_missing_identity(self):
        self.context.data["node_id"] = None

        result = self.m.validate()

        self.assertFalse(result["valid"])
        self.assertIn(
            "node_id",
            result["missing"]
        )

    def test_global_identity_accessors(self):
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

    def test_local_identity_accessors(self):
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
