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

    def create(self,pid,name,version,status="enabled"):
        db=self.db()
        db.append({
            "id":pid,
            "name":name,
            "version":version,
            "status":status
        })
        self.save(db)
