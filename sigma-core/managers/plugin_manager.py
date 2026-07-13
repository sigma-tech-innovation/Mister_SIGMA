import json
import shutil
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "base_manager",
    Path.cwd() / "sigma-core/managers/base_manager.py"
)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


class PluginManager(base.BaseManager):

    def list(self):
        return self.database.load("plugins")

    def get(self, name):
        for plugin in self.list():
            if plugin.get("name") == name:
                return plugin
        return None

    def exists(self, name):
        return self.get(name) is not None

    def validate(self, name):
        plugin = self.get(name)
        return (
            plugin is not None
            and plugin.get("status") in ("enabled", "disabled")
        )

    def install(self, plugin):
        if self.exists(plugin["name"]):
            return False

        plugins = self.list()
        plugins.append(plugin)
        self.database.save("plugins", plugins)
        return True

    def create(self, plugin):
        self.install(plugin)

    def delete(self, name):
        plugins = [
            p for p in self.list()
            if p.get("name") != name
        ]
        self.database.save("plugins", plugins)

    def enable(self, name):
        plugins = self.list()
        for p in plugins:
            if p.get("name") == name:
                p["status"] = "enabled"
        self.database.save("plugins", plugins)

    def disable(self, name):
        plugins = self.list()
        for p in plugins:
            if p.get("name") == name:
                p["status"] = "disabled"
        self.database.save("plugins", plugins)

    def export_file(self, filename):
        Path(filename).write_text(
            json.dumps(self.list(), indent=2),
            encoding="utf-8"
        )

    def import_file(self, filename):
        data = json.loads(
            Path(filename).read_text(encoding="utf-8")
        )
        self.database.save("plugins", data)

    def backup(self, filename):
        shutil.copy2("sigma-db/plugins.json", filename)

    def restore(self, filename):
        shutil.copy2(filename, "sigma-db/plugins.json")


    def count(self):
        return len(self.list())

    def search(self, keyword):
        keyword=keyword.lower()
        return [
            p for p in self.list()
            if keyword in p.get("name","").lower()
        ]

    def rename(self, old_name, new_name):
        plugins=self.list()
        for p in plugins:
            if p.get("name")==old_name:
                p["name"]=new_name
                self.database.save("plugins", plugins)
                return True
        return False

    def update(self, name, **fields):
        plugins=self.list()
        for p in plugins:
            if p.get("name")==name:
                p.update(fields)
                self.database.save("plugins", plugins)
                return True
        return False


    def names(self):
        return [p.get("name") for p in self.list()]

    def enabled(self):
        return [
            p for p in self.list()
            if p.get("status") == "enabled"
        ]

    def disabled(self):
        return [
            p for p in self.list()
            if p.get("status") == "disabled"
        ]


    def uninstall(self, name):
        return self.delete(name)


    def save(self):
        self.database.save("plugins", self.list())
        return True


    def load(self):
        return self.database.load("plugins")


    def unload(self, name):
        return self.disable(name)


    def status(self, name):
        plugin = self.get(name)
        if plugin is None:
            return None
        return plugin.get("status")


    def version(self, name):
        plugin = self.get(name)
        if plugin is None:
            return None
        return plugin.get("version")


    def plugin_id(self, name):
        plugin = self.get(name)
        if plugin is None:
            return None
        return plugin.get("id")
