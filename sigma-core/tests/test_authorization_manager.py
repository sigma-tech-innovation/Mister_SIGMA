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


authorization_module = load(
    "authorization_manager",
    "sigma-core/managers/authorization_manager.py"
)


class FakeContext:

    def __init__(self, role="administrator"):
        self.data = {
            "organization_id": "sigma-tech-innovation",
            "user_id": "USER-0001",
            "workspace_id": "WORKSPACE-0001",
            "role": role,
        }

    def get(self, key, default=None):
        return self.data.get(key, default)

    def organization_id(self):
        return self.data["organization_id"]

    def user_id(self):
        return self.data["user_id"]

    def workspace_id(self):
        return self.data["workspace_id"]


class AuthorizationManagerTests(unittest.TestCase):

    def create_manager(self, role="administrator"):
        engine = SimpleNamespace(
            context=FakeContext(role)
        )

        return (
            authorization_module
            .AuthorizationManager(engine)
        )

    def test_manager_exists(self):
        manager = self.create_manager()

        self.assertIsNotNone(manager)

    def test_administrator_has_all_permissions(self):
        manager = self.create_manager(
            "administrator"
        )

        self.assertTrue(
            manager.has_permission(
                "project.delete"
            )
        )
        self.assertTrue(
            manager.has_permission(
                "unknown.future.permission"
            )
        )

    def test_viewer_is_read_only(self):
        manager = self.create_manager(
            "viewer"
        )

        self.assertTrue(
            manager.has_permission(
                "project.read"
            )
        )
        self.assertFalse(
            manager.has_permission(
                "project.update"
            )
        )
        self.assertFalse(
            manager.has_permission(
                "sync.execute"
            )
        )

    def test_operator_can_execute_sync(self):
        manager = self.create_manager(
            "operator"
        )

        self.assertTrue(
            manager.can(
                "execute",
                "sync"
            )
        )
        self.assertFalse(
            manager.can(
                "delete",
                "project"
            )
        )

    def test_developer_permissions(self):
        manager = self.create_manager(
            "developer"
        )

        self.assertTrue(
            manager.has_permission(
                "package.create"
            )
        )
        self.assertFalse(
            manager.has_permission(
                "project.delete"
            )
        )

    def test_require_success(self):
        manager = self.create_manager(
            "manager"
        )

        self.assertTrue(
            manager.require(
                "project.update"
            )
        )

    def test_require_failure(self):
        manager = self.create_manager(
            "viewer"
        )

        with self.assertRaises(
            PermissionError
        ):
            manager.require(
                "project.delete"
            )

    def test_unknown_role_is_invalid(self):
        manager = self.create_manager(
            "unknown-role"
        )

        result = manager.validate()

        self.assertFalse(result["valid"])
        self.assertEqual(
            result["permissions"],
            []
        )
        self.assertIn(
            "Unknown role",
            result["errors"][0]
        )

    def test_default_role(self):
        engine = SimpleNamespace(
            context=FakeContext(None)
        )

        manager = (
            authorization_module
            .AuthorizationManager(engine)
        )

        self.assertEqual(
            manager.role(),
            "viewer"
        )

    def test_snapshot(self):
        manager = self.create_manager(
            "administrator"
        )

        result = manager.snapshot()

        self.assertTrue(result["valid"])
        self.assertEqual(
            result["organization_id"],
            "sigma-tech-innovation"
        )
        self.assertEqual(
            result["user_id"],
            "USER-0001"
        )
        self.assertEqual(
            result["workspace_id"],
            "WORKSPACE-0001"
        )
        self.assertEqual(
            result["role"],
            "administrator"
        )


if __name__ == "__main__":
    unittest.main()
