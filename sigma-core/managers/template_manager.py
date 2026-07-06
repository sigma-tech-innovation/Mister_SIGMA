import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "base_manager",
    Path.cwd() / "sigma-core/managers/base_manager.py"
)

base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

class TemplateManager(base.BaseManager):

    def list(self):
        for tpl in self.database.load("templates"):
            print(
                f'{tpl["id"]} | {tpl["name"]} | {tpl["version"]}'
            )

    def next_id(self):
        db = self.database.load("templates")

        if not db:
            return "TPL-0001"

        last = max(
            int(x["id"].split("-")[1])
            for x in db
        )

        return f"TPL-{last+1:04d}"
