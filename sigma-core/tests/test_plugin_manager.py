import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


plugin = load(
    "plugin",
    "sigma-core/managers/plugin_manager.py"
)
database = load(
    "database",
    "sigma-core/managers/database_manager.py"
)


class PluginManagerTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.db_dir = self.root / "sigma-db"
        self.db_dir.mkdir()

        self.engine = SimpleNamespace(db=self.db_dir)
        self.engine.database = database.DatabaseManager(self.engine)
        self.m = plugin.PluginManager(self.engine)

        self.engine.database.save("plugins", [
            {
                "id": "PLG-0001",
                "name": "alpha",
                "version": "1.0.0",
                "status": "enabled"
            },
            {
                "id": "PLG-0002",
                "name": "beta",
                "version": "2.0.0",
                "status": "disabled"
            }
        ])

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_manager_exists(self):
        self.assertIsNotNone(self.m)

    def test_list_get_exists_count(self):
        self.assertEqual(self.m.count(), 2)
        self.assertTrue(self.m.exists("alpha"))
        self.assertFalse(self.m.exists("missing"))
        self.assertEqual(
            self.m.get("alpha")["version"],
            "1.0.0"
        )

    def test_install_create_delete(self):
        item = {
            "id": "PLG-0003",
            "name": "gamma",
            "version": "1.0.0",
            "status": "enabled"
        }

        self.assertTrue(self.m.install(item))
        self.assertFalse(self.m.install(item))
        self.assertTrue(self.m.exists("gamma"))
        self.assertTrue(self.m.delete("gamma"))
        self.assertFalse(self.m.delete("gamma"))

    def test_enable_disable_and_status(self):
        self.assertTrue(self.m.disable("alpha"))
        self.assertEqual(
            self.m.status("alpha"),
            "disabled"
        )

        self.assertTrue(self.m.enable("alpha"))
        self.assertEqual(
            self.m.status("alpha"),
            "enabled"
        )

        self.assertFalse(self.m.enable("missing"))
        self.assertFalse(self.m.disable("missing"))

    def test_update_rename_search(self):
        self.assertTrue(
            self.m.update("alpha", version="1.1.0")
        )
        self.assertEqual(
            self.m.version("alpha"),
            "1.1.0"
        )

        self.assertTrue(
            self.m.rename("alpha", "alpha-renamed")
        )
        self.assertTrue(
            self.m.exists("alpha-renamed")
        )
        self.assertEqual(
            len(self.m.search("RENAMED")),
            1
        )

    def test_names_enabled_disabled(self):
        self.assertEqual(
            self.m.names(),
            ["alpha", "beta"]
        )
        self.assertEqual(
            [p["name"] for p in self.m.enabled()],
            ["alpha"]
        )
        self.assertEqual(
            [p["name"] for p in self.m.disabled()],
            ["beta"]
        )

    def test_validate_metadata_and_reload(self):
        self.assertTrue(self.m.validate("alpha"))
        self.assertFalse(self.m.validate("missing"))
        self.assertEqual(
            self.m.plugin_id("alpha"),
            "PLG-0001"
        )
        self.assertEqual(
            self.m.version("alpha"),
            "1.0.0"
        )
        self.assertTrue(self.m.reload("alpha"))
        self.assertFalse(self.m.reload("missing"))

    def test_enable_disable_all_and_by_id(self):
        enabled = self.m.enable_all()
        self.assertEqual(
            enabled,
            {"alpha": True, "beta": True}
        )

        disabled = self.m.disable_all()
        self.assertEqual(
            disabled,
            {"alpha": True, "beta": True}
        )

        self.assertTrue(
            self.m.enable_by_id("PLG-0001")
        )
        self.assertTrue(
            self.m.disable_by_id("PLG-0001")
        )
        self.assertFalse(
            self.m.enable_by_id("missing")
        )

    def test_export_import(self):
        export_path = self.root / "plugins-export.json"

        self.m.export_file(export_path)
        self.engine.database.save("plugins", [])

        self.m.import_file(export_path)

        self.assertEqual(self.m.count(), 2)

    def test_discover(self):
        plugins_dir = self.root / "sigma-plugins"
        valid = plugins_dir / "valid-plugin"
        invalid = plugins_dir / "invalid-plugin"

        valid.mkdir(parents=True)
        invalid.mkdir(parents=True)
        (valid / "__init__.py").write_text(
            "",
            encoding="utf-8"
        )

        previous = Path.cwd()

        try:
            os.chdir(self.root)
            self.assertEqual(
                self.m.discover(),
                ["valid-plugin"]
            )
        finally:
            os.chdir(previous)


if __name__ == "__main__":
    unittest.main()
