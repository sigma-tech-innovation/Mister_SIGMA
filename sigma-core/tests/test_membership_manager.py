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


membership_module = load(
    "membership_manager",
    "sigma-core/managers/membership_manager.py"
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




class FakeAuthorization:

    def role_exists(self, role):
        return role in {
            "administrator",
            "manager",
            "developer",
            "operator",
            "viewer",
        }


class MembershipManagerTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()

        self.engine = SimpleNamespace(
            database=FakeDatabase(
                Path(self.temp.name)
            ),
            authorization=FakeAuthorization(),
            context=SimpleNamespace(
                organization_id=lambda:"ORG-1",
                workspace_id=lambda:"WS-1"
            ),
            now=lambda:"2026",
            event=SimpleNamespace(
                emit=lambda *args: None
            )
        )

        self.manager = membership_module.MembershipManager(
            self.engine
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
        result = self.manager.validate_record({
            "id":"MEM-1",
            "organization_id":"ORG-1",
            "workspace_id":"WS-1",
            "user_id":"USER-1",
            "role":"administrator",
            "status":"active",
        })

        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])


    def test_create(self):
        membership = self.manager.create({
            "user_id":"USER-1",
            "role":"administrator",
        })

        self.assertEqual(
            self.manager.count(),
            1
        )

        self.assertEqual(
            membership["status"],
            "active"
        )


if __name__ == "__main__":
    unittest.main()
