import json
from pathlib import Path
import importlib.util

spec=importlib.util.spec_from_file_location(
    "base_manager",
    Path.cwd()/"sigma-core/managers/base_manager.py"
)
base=importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

class PluginManager(base.BaseManager):

    def info(self,name):
        db=self.database.load("plugins")
        for p in db:
            if p["name"]==name:
                return p
        return None
