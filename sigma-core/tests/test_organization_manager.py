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


organization_module = load(
    "organization_manager",
    "sigma-core/managers/organization_manager.py"
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


class FakeContext:

    def user_id(self):
        return "USER-0001"

    def organization_id(self):
        return "ORG-CURRENT"


class FakeEvent:

    def __init__(self):
        self.events = []

    def emit(self, name, value):
        self.events.append(
            (name, value)
        )


class OrganizationManagerTests(
    unittest.TestCase
):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)

        self.event = FakeEvent()

        self.engine = SimpleNamespace(
            database=FakeDatabase(root),
            context=FakeContext(),
            event=self.event,
            now=lambda: "2026-07-14T23:45:00",
        )

        self.manager = (
            organization_module
            .OrganizationManager(self.engine)
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_organization(self, **fields):
        data = {
            "name": "Sigma Tech Innovation",
            **fields,
        }

        return self.manager.create(data)

    def test_manager_exists(self):
        self.assertIsNotNone(self.manager)

    def test_empty_database(self):
        self.assertEqual(
            self.manager.list(),
            []
        )
        self.assertEqual(
            self.manager.count(),
            0
        )

    def test_create(self):
        organization = (
            self.create_organization()
        )

        self.assertEqual(
            organization["name"],
            "Sigma Tech Innovation"
        )
        self.assertEqual(
            organization["slug"],
            "sigma-tech-innovation"
        )
        self.assertEqual(
            organization["owner_user_id"],
            "USER-0001"
        )
        self.assertEqual(
            organization["status"],
            "active"
        )
        self.assertEqual(
            self.manager.count(),
            1
        )

    def test_create_emits_event(self):
        organization = (
            self.create_organization()
        )

        self.assertEqual(
            self.event.events,
            [
                (
                    "organization.created",
                    organization
                )
            ]
        )

    def test_duplicate_slug_is_rejected(self):
        self.create_organization()

        duplicate = self.create_organization(
            name="Another Sigma",
            slug="Sigma Tech Innovation",
        )

        self.assertIsNone(duplicate)
        self.assertEqual(
            self.manager.count(),
            1
        )

    def test_get_and_exists(self):
        organization = (
            self.create_organization()
        )

        self.assertEqual(
            self.manager.get(
                organization["id"]
            ),
            organization
        )
        self.assertTrue(
            self.manager.exists(
                organization["id"]
            )
        )
        self.assertFalse(
            self.manager.exists(
                "ORG-MISSING"
            )
        )

    def test_get_by_slug(self):
        organization = (
            self.create_organization()
        )

        self.assertEqual(
            self.manager.get_by_slug(
                "Sigma Tech Innovation"
            ),
            organization
        )

    def test_update(self):
        organization = (
            self.create_organization()
        )

        updated = self.manager.update(
            organization["id"],
            name="Sigma Innovation Group",
            description="Updated",
        )

        self.assertEqual(
            updated["name"],
            "Sigma Innovation Group"
        )
        self.assertEqual(
            updated["description"],
            "Updated"
        )

    def test_suspend_and_archive(self):
        organization = (
            self.create_organization()
        )

        suspended = self.manager.set_status(
            organization["id"],
            "suspended"
        )

        self.assertEqual(
            suspended["status"],
            "suspended"
        )

        archived = self.manager.delete(
            organization["id"]
        )

        self.assertEqual(
            archived["status"],
            "archived"
        )

    def test_invalid_status(self):
        organization = (
            self.create_organization()
        )

        with self.assertRaises(
            ValueError
        ):
            self.manager.set_status(
                organization["id"],
                "invalid"
            )

    def test_validate(self):
        self.create_organization()

        result = self.manager.validate()

        self.assertTrue(result["valid"])
        self.assertEqual(
            result["count"],
            1
        )
        self.assertEqual(
            result["errors"],
            []
        )

    def test_current_missing(self):
        self.assertIsNone(
            self.manager.current()
        )

    def test_snapshot(self):
        self.create_organization()

        snapshot = self.manager.snapshot()

        self.assertEqual(
            snapshot[
                "current_organization_id"
            ],
            "ORG-CURRENT"
        )
        self.assertTrue(
            snapshot["validation"]["valid"]
        )


if __name__ == "__main__":
    unittest.main()
