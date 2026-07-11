import importlib
import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location(
    "base_manager",
    Path.cwd()/"sigma-core/managers/base_manager.py"
)
base=importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

class PluginManager(base.BaseManager):

    def reload(self,module):
        return importlib.reload(module)
