import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


def load(name, path):
    spec = importlib.util.spec_from_file_location(
        name,
        path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


user_module = load(
    "user_manager",
    "sigma-core/managers/user_manager.py"
)


class FakeDatabase:

    def __init__(self, root):
        self.root = root

    def path(self, name):
        return self.root / f"{name}.json"

    def load(self, name):
        path = self.path(name)

        if not path.exists():
            return []

        return json.loads(
            path.read_text(encoding="utf-8")
        )

    def save(self, name, data):
        self.path(name).write_text(
            json.dumps(data, indent=4),
            encoding="utf-8"
        )


class UserManagerTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()

        self.engine = SimpleNamespace(
            database=FakeDatabase(
                Path(self.temp.name)
            )
        )

        self.manager = (
            user_module.UserManager(self.engine)
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_manager_exists(self):
        self.assertIsNotNone(self.manager)

    def test_empty_database(self):
        self.assertEqual(
            self.manager.count(),
            0
        )
        self.assertEqual(
            self.manager.list(),
            []
        )


    def test_validate_record(self):
        result = self.manager.validate_record(
            {
                "id":"USER-1",
                "organization_id":"ORG-1",
                "email":"user@test.com",
                "username":"user",
                "display_name":"User",
                "status":"active",
            }
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])


    def test_create_user(self):
        self.engine.context = SimpleNamespace(
            organization_id=lambda: "ORG-1"
        )
        self.engine.now = lambda: "2026"
        self.engine.event = SimpleNamespace(
            emit=lambda *args: None
        )

        user = self.manager.create({
            "email":"user@test.com",
            "username":"user",
            "display_name":"User"
        })

        self.assertEqual(
            self.manager.count(),
            1
        )

        self.assertEqual(
            user["status"],
            "active"
        )


if __name__ == "__main__":
    unittest.main()
