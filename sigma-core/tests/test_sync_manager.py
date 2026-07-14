import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


def load(name, path):
    spec = importlib.util.spec_from_file_location(
        name,
        path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sync_module = load(
    "sync_manager",
    "sigma-core/managers/sync_manager.py"
)


class DictionaryConfig:

    def __init__(self, data):
        self.data = dict(data)

    def load(self):
        return dict(self.data)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        return value


class FakeContext:

    REQUIRED_FIELDS = (
        "organization_id",
        "user_id",
        "workspace_id",
        "installation_id",
        "machine_id",
        "node_id",
    )

    def __init__(self, global_config, local_config):
        self.global_config = global_config
        self.local_config = local_config

    def identity(self):
        global_data = self.global_config.load()
        local_data = self.local_config.load()

        return {
            "organization_id": global_data.get(
                "organization_id"
            ),
            "user_id": global_data.get("user_id"),
            "workspace_id": global_data.get(
                "workspace_id"
            ),
            "installation_id": local_data.get(
                "installation_id"
            ),
            "machine_id": local_data.get(
                "machine_id"
            ),
            "node_id": local_data.get("node_id"),
        }


class FakeEvent:

    def __init__(self):
        self.emitted = []

    def emit(self, name, *args):
        self.emitted.append((name, args))


class SyncManagerTests(unittest.TestCase):

    def setUp(self):
        self.global_config = DictionaryConfig({
            "organization_id": "sigma-tech-innovation",
            "user_id": "USER-0001",
            "workspace_id": "default",
            "sync_enabled": True,
            "registry_url": "https://example.invalid/repository",
            "api_endpoint": "",
        })

        self.local_config = DictionaryConfig({
            "installation_id": "INSTALLATION-0001",
            "machine_id": "MACHINE-0001",
            "node_id": "NODE-0001",
            "last_sync": "",
        })

        self.event = FakeEvent()

        self.context = FakeContext(
            self.global_config,
            self.local_config
        )

        self.engine = SimpleNamespace(
            root=Path("/tmp/sigma"),
            config=self.global_config,
            local_config=self.local_config,
            context=self.context,
            event=self.event,
        )

        self.m = sync_module.SyncManager(
            self.engine
        )

    def git_result(
        self,
        stdout="",
        returncode=0,
        stderr=""
    ):
        return SimpleNamespace(
            stdout=stdout,
            stderr=stderr,
            returncode=returncode,
        )

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)

    def test_configuration(self):
        data = self.m.configuration()

        self.assertTrue(data["enabled"])
        self.assertEqual(
            data["registry_url"],
            "https://example.invalid/repository"
        )

    def test_identity(self):
        data = self.m.identity()

        self.assertEqual(
            data["organization_id"],
            "sigma-tech-innovation"
        )
        self.assertEqual(
            data["installation_id"],
            "INSTALLATION-0001"
        )

    @patch.object(sync_module.subprocess, "run")
    def test_git_clean(self, run_mock):
        run_mock.side_effect = [
            self.git_result("develop\n"),
            self.git_result(""),
            self.git_result(
                "https://example.invalid/repository\n"
            ),
        ]

        data = self.m.git()

        self.assertTrue(data["available"])
        self.assertTrue(data["clean"])
        self.assertEqual(data["branch"], "develop")

    @patch.object(sync_module.subprocess, "run")
    def test_validate_ready(self, run_mock):
        run_mock.side_effect = [
            self.git_result("develop\n"),
            self.git_result(""),
            self.git_result(
                "https://example.invalid/repository\n"
            ),
        ]

        result = self.m.validate()

        self.assertTrue(result["ready"])
        self.assertEqual(result["errors"], [])

    @patch.object(sync_module.subprocess, "run")
    def test_validate_dirty_repository(self, run_mock):
        run_mock.side_effect = [
            self.git_result("develop\n"),
            self.git_result(" M file.py\n"),
            self.git_result(
                "https://example.invalid/repository\n"
            ),
        ]

        result = self.m.validate()

        self.assertFalse(result["ready"])
        self.assertIn(
            "Git working tree is not clean",
            result["errors"]
        )

    @patch.object(sync_module.subprocess, "run")
    def test_validate_missing_identity(self, run_mock):
        self.local_config.data.pop("node_id")

        run_mock.side_effect = [
            self.git_result("develop\n"),
            self.git_result(""),
            self.git_result(
                "https://example.invalid/repository\n"
            ),
        ]

        result = self.m.validate()

        self.assertFalse(result["ready"])
        self.assertIn(
            "node_id",
            result["missing"]
        )

    @patch.object(sync_module.subprocess, "run")
    def test_plan(self, run_mock):
        run_mock.side_effect = [
            self.git_result("develop\n"),
            self.git_result(""),
            self.git_result(
                "https://example.invalid/repository\n"
            ),
        ]

        plan = self.m.plan()

        self.assertTrue(plan["ready"])
        self.assertIn(
            "detect-conflicts",
            plan["steps"]
        )
        self.assertIn(
            "synchronize-shared-data",
            plan["steps"]
        )

    def test_mark_synced(self):
        value = self.m.mark_synced(
            "2026-07-14T22:40:00+00:00"
        )

        self.assertEqual(
            value,
            "2026-07-14T22:40:00+00:00"
        )
        self.assertEqual(
            self.local_config.get("last_sync"),
            value
        )
        self.assertEqual(
            self.event.emitted,
            [
                (
                    "sync.completed",
                    (value,)
                )
            ]
        )


if __name__ == "__main__":
    unittest.main()
