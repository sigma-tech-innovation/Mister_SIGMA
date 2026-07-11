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

    def save(self,data):
        self.database.save("plugins",data)

    def enable(self,name):
        db=self.db()
        for p in db:
            if p["name"]==name:
                p["status"]="enabled"
        self.save(db)
