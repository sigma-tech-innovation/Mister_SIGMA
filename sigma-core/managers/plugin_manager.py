import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location(
    "base_manager",
    Path.cwd()/"sigma-core/managers/base_manager.py"
)
base=importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

class PluginManager(base.BaseManager):

    def db(self):
        return self.database.load("plugins")

    def get(self,name):
        for p in self.db():
            if p["name"]==name:
                return p
        return None
